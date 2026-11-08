"""Private, local submission ledger. No browser, account, or network actions."""

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sqlite3
import sys

from check_application import check_packet


class StateError(ValueError):
    pass


def utc_now():
    return datetime.now(timezone.utc)


def identity(packet):
    if not isinstance(packet, dict) or not isinstance(packet.get("job"), dict):
        raise StateError("Application and job must be JSON objects")
    job = packet.get("job", {})
    values = [packet.get("candidate_ref"), job.get("employer"), job.get("job_id")]
    if any(not isinstance(v, str) or not v.strip() for v in values):
        raise StateError("candidate_ref, job.employer and job.job_id are required")
    cycle = job.get("cycle", "")
    if not isinstance(cycle, str):
        raise StateError("job.cycle must be text")
    return json.dumps([v.strip() for v in values] + [cycle.strip()], ensure_ascii=False)


def timestamp(value):
    if not isinstance(value, str):
        raise StateError("Evidence needs an observed_at timestamp with timezone")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StateError("Invalid observed_at timestamp") from exc
    if result.tzinfo is None:
        raise StateError("Evidence timestamp must include timezone")
    return result


class Ledger:
    """One database per user, shared by their cooperating agents."""

    def __init__(self, path):
        if str(path) != ":memory:":
            target = Path(path).resolve()
            # Private records must not be written beside the publishable skill.
            skill_root = Path(__file__).resolve().parents[1]
            package_root = skill_root.parent.parent if skill_root.parent.name == "skills" else skill_root
            if target == package_root or package_root in target.parents:
                raise StateError("Choose a private database path outside the skill repository")
            target.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=10)
        self.db.row_factory = sqlite3.Row
        with self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS applications ("
                            "key TEXT PRIMARY KEY, status TEXT NOT NULL, started_at TEXT, "
                            "updated_at TEXT NOT NULL, note TEXT NOT NULL, evidence_ref TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")

    def close(self):
        self.db.close()

    def get(self, packet):
        row = self.db.execute("SELECT * FROM applications WHERE key=?", (identity(packet),)).fetchone()
        return dict(row) if row else {"key": identity(packet), "status": "new"}

    def set_paused(self, paused):
        if not isinstance(paused, bool):
            raise StateError("paused must be a boolean")
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO settings VALUES ('paused', ?)", (str(int(paused)),))
        return {"paused": paused}

    def _paused(self):
        row = self.db.execute("SELECT value FROM settings WHERE key='paused'").fetchone()
        return bool(row and row[0] == "1")

    def _write(self, key, status, now, note="", evidence_ref=None, started_at=None):
        self.db.execute(
            "INSERT INTO applications VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET status=excluded.status, "
            "started_at=COALESCE(excluded.started_at, applications.started_at), "
            "updated_at=excluded.updated_at, note=excluded.note, evidence_ref=excluded.evidence_ref",
            (key, status, started_at, now.isoformat(), note, evidence_ref),
        )

    def begin(self, packet, now=None):
        """Persist BEFORE clicking submit. A crash keeps the retry blocked."""
        now = now or utc_now()
        report = check_packet(packet, now=now)
        if report.get("ready") is not True:
            raise StateError("Submission checks did not pass; run check_application for details")
        key = identity(packet)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self._paused():
                raise StateError("User paused applications")
            current = self.get(packet)
            if current["status"] not in {"new", "draft"}:
                raise StateError("Cannot submit from state: " + current["status"])
            self._write(key, "submitting", now, started_at=now.isoformat())
        return self.get(packet)

    def handoff(self, packet, reason, now=None):
        if not isinstance(reason, str) or not reason.strip():
            raise StateError("A short non-sensitive handoff reason is required")
        now = now or utc_now()
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self.get(packet)["status"] not in {"new", "draft", "waiting_user"}:
                raise StateError("Resolve the outstanding submission before changing its state")
            self._write(identity(packet), "waiting_user", now, reason)
        return self.get(packet)

    def unknown(self, packet, now=None):
        now = now or utc_now()
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self.get(packet)["status"] not in {"submitting", "unknown"}:
                raise StateError("No outstanding submission to reconcile")
            self._write(identity(packet), "unknown", now, "Check official application history; do not click again")
        return self.get(packet)

    def reconcile(self, packet, evidence, now=None):
        """Record an observation, never infer success from an uploaded file/draft."""
        now = now or utc_now()
        if not isinstance(evidence, dict) or identity(evidence) != identity(packet):
            raise StateError("Evidence identity does not match this application")
        observed = timestamp(evidence.get("observed_at"))
        if observed > now + timedelta(minutes=1) or now - observed > timedelta(hours=24):
            raise StateError("Recheck the live page; evidence is stale or future-dated")
        ref = evidence.get("reference")
        if not isinstance(ref, str) or not ref.strip():
            raise StateError("A private observation reference is required")
        status, kind = evidence.get("status"), evidence.get("kind")
        if status not in {"submitted", "not_submitted", "ready_to_resume"}:
            raise StateError("Evidence is not an application outcome or resume check")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.get(packet)
            previous = current["status"]
            if previous == "submitted":
                if status != "submitted":
                    raise StateError("A confirmed application cannot be reset")
                return current
            if previous not in {"waiting_user", "submitting", "unknown"}:
                raise StateError("No pending state to reconcile")
            if observed < timestamp(current["updated_at"]):
                raise StateError("Observation predates the pending state")
            if status == "submitted":
                if kind not in {"success_page", "application_record"}:
                    raise StateError("Only a final success page or application record confirms submission")
                target = "submitted"
            elif status == "not_submitted":
                if (previous not in {"submitting", "unknown"} or kind != "application_record"
                        or evidence.get("definitive") is not True):
                    raise StateError("Retry needs an explicit official not-submitted record")
                target = "draft"
            else:
                if (previous != "waiting_user" or kind != "live_form"
                        or evidence.get("blocker_resolved") is not True):
                    raise StateError("Resume requires a fresh page check that the blocker is resolved")
                target = "draft"
            self._write(identity(packet), target, now, evidence_ref=ref)
        return self.get(packet)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Private SQLite path outside the skill repository")
    parser.add_argument("action", choices=["status", "begin", "handoff", "unknown", "reconcile", "pause", "resume"])
    parser.add_argument("--input", help="Private application packet JSON")
    parser.add_argument("--evidence", help="Private observation JSON, required for reconcile")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    ledger = None
    try:
        if args.action not in {"pause", "resume"} and not args.input:
            parser.error("--input is required for this action")
        if args.action == "reconcile" and not args.evidence:
            parser.error("--evidence is required for reconcile")
        packet = json.loads(Path(args.input).read_text(encoding="utf-8-sig")) if args.input else None
        ledger = Ledger(args.db)
        if args.action in {"pause", "resume"}:
            result = ledger.set_paused(args.action == "pause")
        elif args.action == "reconcile":
            evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8-sig"))
            result = ledger.reconcile(packet, evidence)
        elif args.action == "handoff":
            result = ledger.handoff(packet, args.reason)
        else:
            result = getattr(ledger, "get" if args.action == "status" else args.action)(packet)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (StateError, OSError, sqlite3.Error, ValueError, TypeError, KeyError) as exc:
        # Only error type/state is printed; malformed input may contain private data.
        print(json.dumps({"error": str(exc) if isinstance(exc, StateError) else type(exc).__name__}))
        return 2
    finally:
        if ledger:
            ledger.close()


if __name__ == "__main__":
    sys.exit(main())
