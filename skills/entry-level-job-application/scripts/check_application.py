#!/usr/bin/env python3
"""Read-only submission packet checks. Evidence is asserted by the agent, not verified here."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from urllib.parse import urlsplit


REQUIREMENTS = ("degree", "major", "graduation", "experience", "location", "work_authorization")
WEIGHTS = {"goals": 30, "experience": 25, "growth": 20, "conditions": 15, "interests": 10}


def _object(value):
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def _list(value):
    if not isinstance(value, list):
        raise ValueError("Expected a JSON array")
    return value


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _empty(value):
    return (value is None or isinstance(value, str) and not value.strip()
            or isinstance(value, (list, dict)) and not value)


def _https(value):
    if not _text(value):
        return False
    url = urlsplit(value)
    return url.scheme == "https" and bool(url.hostname) and not url.username and not url.password


def _time(value):
    if not isinstance(value, str):
        raise ValueError("Evidence timestamps need ISO 8601 text with an explicit time zone")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Evidence timestamps need an explicit time zone")
    return result


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _score(fit):
    if fit is None:
        return None
    fit = _object(fit)
    low = high = 0
    for name, weight in WEIGHTS.items():
        value = fit.get(name)
        bounds = [0, 5] if value is None else value if isinstance(value, list) else [value, value]
        if len(bounds) != 2 or not all(_number(v) for v in bounds) or not 0 <= bounds[0] <= bounds[1] <= 5:
            raise ValueError("Fit values must be 0..5, [low, high], or null")
        low += bounds[0] * weight / 5
        high += bounds[1] * weight / 5
    return [round(low, 2), round(high, 2)]


def check_packet(packet, now=None):
    """Return a submission report; never browse, open attachments, write data, or submit.

    now may be an aware datetime for repeatable tests. Omit it for live checks.
    Malformed packets return valid=False; missing evidence blocks readiness.
    """
    try:
        return _check_packet(_object(packet), now or datetime.now(timezone.utc))
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        return {"valid": False, "ready": False, "decision": "needs_review",
                "issues": [{"code": "invalid_packet", "message": str(error)}], "score_range": None}


def _check_packet(packet, now):
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be a timezone-aware datetime")
    issues = []
    warnings = []

    def issue(code, message):
        issues.append({"code": code, "message": message})

    job = _object(packet.get("job", {}))
    employer, job_id = job.get("employer"), job.get("job_id")
    candidate = packet.get("candidate_ref")
    if not all(_text(v) for v in (candidate, employer, job_id)):
        issue("identity", "Candidate, employer and exact job ID are required")
    sources = _object(packet.get("sources", {}))
    facts = _object(packet.get("facts", {}))
    max_age = packet.get("max_age_hours", 24)
    if not _number(max_age) or not 0 < max_age <= 168:
        raise ValueError("max_age_hours must be greater than zero and at most 168")

    def in_scope(record):
        expected = {"candidate_ref": candidate, "employer": employer, "job_id": job_id}
        return all(key not in record or record[key] == value for key, value in expected.items())

    def source(source_id, official=False):
        record = _object(sources.get(source_id, {})) if _text(source_id) else {}
        good = record.get("verified") is True and _text(record.get("ref")) and in_scope(record)
        if official:
            good = (good and record.get("kind") == "official" and _https(record.get("ref"))
                    and _https(record.get("official_entry_url"))
                    and record.get("employer") == employer and record.get("job_id") == job_id)
        else:
            good = (good and record.get("kind") in ("candidate", "authorization")
                    and record.get("candidate_ref") == candidate)
        return record if good else None

    def fact(fact_id):
        record = _object(facts.get(fact_id, {})) if _text(fact_id) else {}
        refs = _list(record.get("source_ids", []))
        if (record.get("status") != "confirmed" or _empty(record.get("value")) or not in_scope(record)
                or not refs or not all(source(ref) for ref in refs)):
            return None
        return record

    def current_requirement_source(source_id):
        record = source(source_id, official=True)
        return record and 0 <= (now - _time(record.get("observed_at"))).total_seconds() / 3600 <= max_age

    official = source(job.get("source_id"), official=True)
    if official is None:
        issue("official_source", "Exact job needs a verified official URL and employer-to-ATS provenance")
    else:
        observed = _time(official.get("observed_at"))
        checked = _time(job.get("verified_at"))
        ages = [(now - stamp).total_seconds() / 3600 for stamp in (observed, checked)]
        if any(age < 0 or age > max_age for age in ages):
            issue("stale_job", "Refresh the exact job: observation is stale, future-dated or inconsistent")
    status = job.get("status")
    ineligible = status == "closed"
    if status != "open":
        issue("job_status", "Exact job is not verified open")
    if job.get("closes_at") is not None and _time(job["closes_at"]) <= now:
        ineligible = True
        issue("job_closed", "The recorded closing time has passed")

    requirements = _object(packet.get("requirements", {}))
    for name in REQUIREMENTS:
        requirement = _object(requirements.get(name, {}))
        result = requirement.get("status", "unknown")
        if result == "fail":
            ineligible = True
            issue("requirement_failed", name + ": hard requirement failed")
        elif result not in ("pass", "no_restriction", "not_stated"):
            issue("requirement_unknown", name + ": resolve the actual hard condition before submission")
        if result in ("pass", "fail", "no_restriction"):
            if not _text(requirement.get("quote")) or not current_requirement_source(requirement.get("source_id")):
                issue("requirement_evidence", name + ": missing official wording for this exact job")
        if result == "not_stated":
            if not _text(requirement.get("note")) or not current_requirement_source(requirement.get("source_id")):
                issue("requirement_evidence", name + ": inspected official source and an absence note are required")
            warnings.append(name + ": no restriction was stated; this does not guarantee employer acceptance")
        if result == "pass":
            refs = _list(requirement.get("fact_ids", []))
            if not refs or not all(fact(ref) for ref in refs):
                issue("requirement_facts", name + ": missing, unknown or conflicting candidate facts")

    for field in _list(packet.get("fields", [])):
        field = _object(field)
        name = field.get("name", "unnamed field")
        if type(field.get("required")) is not bool:
            raise ValueError("Every form field needs required: true or false")
        if "text" in field and "value" in field:
            raise ValueError("A field must use either text or value, never both")
        if not in_scope(field):
            issue("answer_scope", str(name) + ": field belongs to a different candidate, employer or job")
        narrative = "text" in field
        value = field.get("text") if narrative else field.get("value")
        if _empty(value):
            if field["required"]:
                issue("required_field", str(name) + ": required value is missing")
            continue
        if narrative:
            refs = _list(field.get("fact_ids", []))
            if (not _text(value) or field.get("reviewed") is not True or not refs
                    or not all(fact(ref) for ref in refs)):
                issue("narrative_evidence", str(name) + ": review the answer against confirmed source facts")
            if field.get("employer") != employer or field.get("job_id") != job_id:
                issue("answer_scope", str(name) + ": answer belongs to a different employer or job")
        else:
            known = fact(field.get("fact_id"))
            if (known is None or json.dumps(known["value"], sort_keys=True, allow_nan=False)
                    != json.dumps(value, sort_keys=True, allow_nan=False)):
                issue("field_fact", str(name) + ": value differs from its confirmed fact or has no support")

    authorization = _object(packet.get("authorization", {}))
    scope = _list(authorization.get("scope", []))
    allowed = False
    for entry in scope:
        entry = _object(entry)
        ids = _list(entry.get("job_ids", []))
        if entry.get("employer") == employer and job_id in ids:
            allowed = True
    if (authorization.get("submit") is not True or authorization.get("paused") is not False
            or authorization.get("candidate_ref") != candidate or not allowed):
        issue("authorization", "Submission needs active authorization for this candidate, employer and job")
    authorized_refs = _list(authorization.get("attachment_refs", []))
    for attachment in _list(packet.get("attachments", [])):
        attachment = _object(attachment)
        ref = attachment.get("ref")
        if type(attachment.get("required")) is not bool:
            raise ValueError("Every attachment slot needs required: true or false")
        if not _text(ref):
            if attachment["required"]:
                issue("attachment_missing", "A required attachment has not been selected")
            continue
        if ref not in authorized_refs or attachment.get("authorized") is not True:
            issue("attachment_authorization", "Selected attachment is outside the authorized references")
        if (not _text(attachment.get("expected_role")) or not _text(attachment.get("expected_language"))
                or attachment.get("role") != attachment.get("expected_role")
                or attachment.get("language") != attachment.get("expected_language")):
            issue("attachment_mismatch", "Selected attachment role or language does not match the form")
    for term in _list(packet.get("terms", [])):
        term = _object(term)
        if type(term.get("required")) is not bool or type(term.get("selected")) is not bool:
            raise ValueError("Every term needs required and selected booleans")
        if term["required"] and not term["selected"]:
            issue("required_term", "A required declaration is not selected")
        if term["selected"] and (not term["required"] or term.get("authorized") is not True
                                 or term.get("applicable") is not True):
            issue("unsafe_term", "Selected declaration must be necessary, authorized and factually applicable")

    if packet.get("form_reviewed") is not True:
        issue("form_review", "Agent must compare the complete packet against the current form and originals")
    score_range = _score(packet.get("fit"))
    return {"valid": True, "ready": not issues,
            "decision": "ineligible" if ineligible else "needs_review" if issues else "eligible",
            "issues": issues, "warnings": warnings, "score_range": score_range}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Private JSON packet; read only")
    args = parser.parse_args()
    try:
        packet = json.loads(args.input.read_text(encoding="utf-8"))
        report = check_packet(packet)
    except (OSError, ValueError) as error:
        report = {"valid": False, "ready": False, "decision": "needs_review",
                  "issues": [{"code": "invalid_input", "message": str(error)}], "score_range": None}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if not report["valid"] else 0 if report["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
