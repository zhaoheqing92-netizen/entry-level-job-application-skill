import concurrent.futures
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/entry-level-job-application/scripts"))
from application_state import Ledger, StateError, identity


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="job-skill-test-", dir=ROOT.parent)
        self.assertEqual(Path(self.temp.name).resolve().parent, ROOT.parent.resolve())
        self.path = Path(self.temp.name) / "applications.sqlite"
        self.ledger = Ledger(self.path)
        self.packet = json.loads((ROOT / "skills/entry-level-job-application/assets/application.example.json").read_text(encoding="utf-8"))
        self.application_key = identity(self.packet)
        self.now = datetime(2026, 11, 8, 8, tzinfo=timezone.utc)
        self.packet["job"]["verified_at"] = self.now.isoformat()
        for source in self.packet["sources"].values():
            if source.get("kind") == "official":
                source["observed_at"] = self.now.isoformat()

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def evidence(self, status="submitted", kind="application_record", **extra):
        return {"candidate_ref": self.packet["candidate_ref"], "job": deepcopy(self.packet["job"]),
                "status": status, "kind": kind, "observed_at": (self.now + timedelta(minutes=1)).isoformat(),
                "reference": "private-observation-1", **extra}

    def test_begin_needs_current_confirmation_for_this_application(self):
        with self.assertRaisesRegex(StateError, "confirm"):
            self.ledger.begin(self.packet, self.now)
        for field in ("employer", "job_id", "cycle"):
            other = deepcopy(self.packet)
            other["job"][field] += "-other"
            with self.assertRaises(StateError):
                self.ledger.begin(self.packet, self.now, confirmed_application=identity(other))
        other = dict(self.packet, candidate_ref="another-user")
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=identity(other))
        self.assertEqual("new", self.ledger.get(self.packet)["status"])
        waiting = self.ledger.handoff(self.packet, "Ready for the user to submit", self.now)
        self.assertEqual("waiting_user", waiting["status"])
        done = self.ledger.reconcile(self.packet, self.evidence(), self.now + timedelta(minutes=2))
        self.assertEqual("submitted", done["status"])

    def test_legacy_packet_cannot_confirm_cli_begin(self):
        now = datetime.now(timezone.utc).isoformat()
        self.packet["job"]["verified_at"] = now
        self.packet["sources"]["job-page"]["observed_at"] = now
        self.packet["authorization"].update(submit=True, confirmed_application=self.application_key)
        packet_path = Path(self.temp.name) / "legacy.json"
        packet_path.write_text(json.dumps(self.packet), encoding="utf-8")
        cmd = [sys.executable, str(ROOT / "skills/entry-level-job-application/scripts/application_state.py"),
               "--db", str(self.path), "begin", "--input", str(packet_path)]
        blocked = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(2, blocked.returncode, blocked.stdout)
        self.assertIn("authorization.submit", json.loads(blocked.stdout)["error"])
        self.assertEqual("new", self.ledger.get(self.packet)["status"])
        confirmed = subprocess.run(cmd + ["--confirm-submit-now", self.application_key], capture_output=True, text=True)
        self.assertEqual(0, confirmed.returncode, confirmed.stdout + confirmed.stderr)
        self.assertEqual("submitting", json.loads(confirmed.stdout)["status"])

    def test_resume_after_process_exit_does_not_resubmit(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        other = Ledger(self.path)
        try:
            self.assertEqual(other.get(self.packet)["status"], "submitting")
            with self.assertRaises(StateError):
                other.begin(self.packet, self.now, confirmed_application=self.application_key)
        finally:
            other.close()

    def test_two_agents_only_one_can_begin(self):
        barrier = threading.Barrier(2)
        def worker():
            db = Ledger(self.path)
            try:
                barrier.wait(timeout=10)
                try:
                    db.begin(self.packet, self.now, confirmed_application=self.application_key)
                    return "started"
                except StateError:
                    return "blocked"
            finally:
                db.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: worker(), range(2)))
        self.assertCountEqual(results, ["started", "blocked"])

    def test_unknown_cannot_be_erased_by_handoff_or_repeated_begin(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        self.ledger.unknown(self.packet, self.now)
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        with self.assertRaises(StateError):
            self.ledger.handoff(self.packet, "wait", self.now)
        self.assertEqual(self.ledger.get(self.packet)["status"], "unknown")

    def test_wrong_account_or_job_receipt_rejected(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        for field in ("candidate", "job"):
            e = self.evidence()
            if field == "candidate":
                e["candidate_ref"] = "another-user"
            else:
                e["job"]["job_id"] = "OTHER-2"
            with self.assertRaises(StateError):
                self.ledger.reconcile(self.packet, e, self.now + timedelta(minutes=2))
        self.assertEqual(self.ledger.get(self.packet)["status"], "submitting")

    def test_draft_upload_or_old_evidence_not_success(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        for e in (self.evidence(kind="upload"), self.evidence(status="draft"),
                  self.evidence(observed_at=(self.now - timedelta(minutes=1)).isoformat())):
            with self.assertRaises(StateError):
                self.ledger.reconcile(self.packet, e, self.now + timedelta(minutes=2))

    def test_confirmed_submission_is_terminal_and_idempotent(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        e = self.evidence()
        self.ledger.reconcile(self.packet, e, self.now + timedelta(minutes=2))
        self.assertEqual(self.ledger.reconcile(self.packet, e, self.now + timedelta(minutes=2))["status"], "submitted")
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        with self.assertRaises(StateError):
            self.ledger.reconcile(self.packet, self.evidence(status="not_submitted", definitive=True), self.now + timedelta(minutes=2))

    def test_retry_requires_definitive_official_failure_not_absence_of_email(self):
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        self.ledger.unknown(self.packet, self.now)
        for e in (self.evidence(status="not_submitted", kind="email_search", definitive=True),
                  self.evidence(status="not_submitted")):
            with self.assertRaises(StateError):
                self.ledger.reconcile(self.packet, e, self.now + timedelta(minutes=2))
        self.ledger.reconcile(self.packet, self.evidence(status="not_submitted", definitive=True), self.now + timedelta(minutes=2))
        self.assertEqual(self.ledger.get(self.packet)["status"], "draft")
        with self.assertRaisesRegex(StateError, "confirm"):
            self.ledger.begin(self.packet, self.now + timedelta(minutes=3))
        self.ledger.begin(self.packet, self.now + timedelta(minutes=3), confirmed_application=self.application_key)

    def test_user_says_continue_is_not_verified_handoff(self):
        self.ledger.handoff(self.packet, "Complete verification in the official form", self.now)
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        with self.assertRaises(StateError):
            self.ledger.reconcile(self.packet, self.evidence(status="ready_to_resume", kind="live_form"), self.now + timedelta(minutes=2))
        self.ledger.reconcile(self.packet, self.evidence(status="ready_to_resume", kind="live_form", blocker_resolved=True), self.now + timedelta(minutes=2))
        self.ledger.begin(self.packet, self.now + timedelta(minutes=3), confirmed_application=self.application_key)

    def test_global_pause_stops_new_submissions_but_allows_reconciliation(self):
        self.ledger.set_paused(True)
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        self.ledger.set_paused(False)
        self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        self.ledger.set_paused(True)
        self.ledger.reconcile(self.packet, self.evidence(), self.now + timedelta(minutes=2))
        self.assertEqual(self.ledger.get(self.packet)["status"], "submitted")

    def test_bad_packet_never_starts_submission(self):
        self.packet["authorization"]["submit"] = False
        with self.assertRaises(StateError):
            self.ledger.begin(self.packet, self.now, confirmed_application=self.application_key)
        self.assertEqual(self.ledger.get(self.packet)["status"], "new")

    def test_no_private_database_inside_publishable_skill(self):
        with self.assertRaises(StateError):
            Ledger(ROOT / "private" / "applications.sqlite")

    def test_malformed_identity_has_a_controlled_error(self):
        for packet in (None, [], {}, {"job": None}, {"job": []}):
            with self.assertRaises(StateError):
                identity(packet)


if __name__ == "__main__":
    unittest.main()
