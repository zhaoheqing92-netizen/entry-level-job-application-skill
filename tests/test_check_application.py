import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/entry-level-job-application/scripts/check_application.py"
SPEC = importlib.util.spec_from_file_location("check_application", SCRIPT)
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
FIXTURE = json.loads((ROOT / "skills/entry-level-job-application/assets/application.example.json").read_text(encoding="utf-8"))
NOW = datetime.fromisoformat("2026-11-08T02:30:00+00:00")


class SubmissionGuardTests(unittest.TestCase):
    def setUp(self):
        self.packet = copy.deepcopy(FIXTURE)

    def check(self):
        return GUARD.check_packet(self.packet, now=NOW)

    def blocked(self, code):
        report = self.check()
        self.assertFalse(report["ready"], report)
        self.assertIn(code, [issue["code"] for issue in report["issues"]], report)
        return report

    def test_ready_has_uncertain_fit_interval_and_does_not_mutate_packet(self):
        original = copy.deepcopy(self.packet)
        report = self.check()
        self.assertTrue(report["ready"], report)
        self.assertEqual("eligible", report["decision"])
        self.assertEqual([61, 77], report["score_range"])
        self.assertEqual(original, self.packet)

    def test_high_score_cannot_override_failed_degree_or_unknown_work_rights(self):
        self.packet["fit"] = dict.fromkeys(GUARD.WEIGHTS, 5)
        self.packet["requirements"]["degree"]["status"] = "fail"
        self.assertEqual("ineligible", self.blocked("requirement_failed")["decision"])
        self.packet["requirements"]["degree"]["status"] = "pass"
        self.packet["facts"]["work_authorization"]["status"] = "unknown"
        self.blocked("requirement_facts")

    def test_missing_hard_condition_is_unknown_not_a_pass(self):
        del self.packet["requirements"]["graduation"]
        self.blocked("requirement_unknown")

    def test_inspected_absence_is_allowed_with_a_warning_not_a_guarantee(self):
        self.packet["requirements"]["graduation"] = {
            "status": "not_stated", "source_id": "job-page", "note": "Full JD contains no cohort condition"
        }
        report = self.check()
        self.assertTrue(report["ready"], report)
        self.assertEqual(1, len(report["warnings"]))
        del self.packet["requirements"]["graduation"]["note"]
        self.blocked("requirement_evidence")

    def test_no_restriction_requires_actual_official_wording(self):
        del self.packet["requirements"]["experience"]["quote"]
        self.blocked("requirement_evidence")

    def test_conflicting_dates_and_direct_field_changes_block(self):
        self.packet["facts"]["graduation"]["status"] = "conflict"
        self.blocked("field_fact")
        self.packet["facts"]["graduation"]["status"] = "confirmed"
        self.packet["fields"][0]["value"] = "2026-06"
        self.blocked("field_fact")

    def test_stale_job_source_cannot_be_laundered_with_fresh_verified_time(self):
        self.packet["sources"]["job-page"]["observed_at"] = "2026-11-06T10:00:00+08:00"
        self.blocked("stale_job")

    def test_current_open_job_does_not_refresh_separate_old_requirement_evidence(self):
        self.packet["sources"]["old-conditions"] = copy.deepcopy(self.packet["sources"]["job-page"])
        self.packet["sources"]["old-conditions"]["observed_at"] = "2026-11-06T10:00:00+08:00"
        self.packet["requirements"]["graduation"]["source_id"] = "old-conditions"
        self.blocked("requirement_evidence")

    def test_timezone_offsets_exact_boundary_and_future_time(self):
        self.packet["sources"]["job-page"]["observed_at"] = "2026-11-07T10:30:00+08:00"
        self.assertTrue(self.check()["ready"])
        self.packet["sources"]["job-page"]["observed_at"] = "2026-11-07T10:29:59+08:00"
        self.blocked("stale_job")
        self.packet["sources"]["job-page"]["observed_at"] = "2026-11-08T02:30:01Z"
        self.blocked("stale_job")

    def test_naive_timestamps_and_unbounded_age_are_invalid(self):
        self.packet["job"]["verified_at"] = "2026-11-08T10:00:00"
        self.assertFalse(self.check()["valid"])
        self.packet = copy.deepcopy(FIXTURE)
        self.packet["max_age_hours"] = 100000
        self.assertFalse(self.check()["valid"])

    def test_closed_and_wrong_job_sources_block(self):
        self.packet["job"]["status"] = "closed"
        self.assertEqual("ineligible", self.blocked("job_status")["decision"])
        self.packet["job"]["status"] = "open"
        self.packet["sources"]["job-page"]["job_id"] = "OLD-TEST-02"
        self.blocked("official_source")

    def test_expired_deadline_blocks_even_fresh_open_claim(self):
        self.packet["job"]["closes_at"] = "2026-11-08T02:30:00Z"
        self.assertEqual("ineligible", self.blocked("job_closed")["decision"])

    def test_unknown_optional_field_can_be_omitted_but_not_filled(self):
        self.packet["fields"].append({"name": "GPA", "required": False})
        self.assertTrue(self.check()["ready"])
        self.packet["fields"][-1]["value"] = "4.0"
        self.blocked("field_fact")
        self.packet["fields"][-1] = {"name": "GPA", "required": True}
        self.blocked("required_field")

    def test_empty_required_values_block_but_confirmed_false_is_a_real_value(self):
        for value in (None, "", "  ", [], {}):
            with self.subTest(value=value):
                self.packet["fields"][0]["value"] = value
                self.blocked("required_field")
        self.packet = copy.deepcopy(FIXTURE)
        self.packet["facts"]["optional-permission"] = {
            "status": "confirmed", "value": False, "source_ids": ["candidate-confirmation"]
        }
        self.packet["fields"].append({"name": "Optional permission", "required": True,
                                      "value": False, "fact_id": "optional-permission"})
        self.assertTrue(self.check()["ready"])

    def test_cross_employer_answers_and_unreviewed_prose_block(self):
        self.packet["fields"][2]["employer"] = "Other Example Employer"
        self.blocked("answer_scope")
        self.packet["fields"][2]["employer"] = self.packet["job"]["employer"]
        self.packet["fields"][2]["reviewed"] = False
        self.blocked("narrative_evidence")

    def test_cross_candidate_sources_block(self):
        self.packet["sources"]["resume"]["candidate_ref"] = "different-fictional-candidate"
        self.blocked("requirement_facts")

    def test_attachments_require_exact_reference_role_and_language(self):
        self.packet["attachments"][0]["ref"] = "synthetic:unapproved-resume"
        self.blocked("attachment_authorization")
        self.packet["attachments"][0]["ref"] = "synthetic:resume-en-v1"
        self.packet["attachments"][0]["language"] = "zh"
        self.blocked("attachment_mismatch")
        self.packet["attachments"][0].pop("ref")
        self.blocked("attachment_missing")

    def test_optional_consent_and_untrue_required_declaration_block(self):
        self.packet["terms"][1].update(selected=True, authorized=True, applicable=True)
        self.blocked("unsafe_term")
        self.packet["terms"][1]["selected"] = False
        self.packet["terms"][0]["applicable"] = False
        self.blocked("unsafe_term")

    def test_scope_candidate_pause_and_review_are_enforced(self):
        for change in ({"paused": True}, {"submit": False}, {"candidate_ref": "other"},
                       {"scope": [{"employer": "Example Research", "job_ids": ["OTHER"]}]}):
            with self.subTest(change=change):
                self.packet = copy.deepcopy(FIXTURE)
                self.packet["authorization"].update(change)
                self.blocked("authorization")
        self.packet = copy.deepcopy(FIXTURE)
        self.packet["form_reviewed"] = False
        self.blocked("form_review")

    def test_malformed_types_never_pass_or_raise(self):
        for key, value in (("facts", []), ("fields", {}), ("fit", {"goals": True}),
                           ("requirements", []), ("authorization", [])):
            with self.subTest(key=key):
                packet = copy.deepcopy(FIXTURE)
                packet[key] = value
                report = GUARD.check_packet(packet, now=NOW)
                self.assertFalse(report["valid"], report)
                self.assertFalse(report["ready"])
        self.assertFalse(GUARD.check_packet([], now=NOW)["valid"])
        self.assertFalse(GUARD.check_packet({}, now=NOW)["ready"])

    def test_cli_exit_codes_and_input_unchanged(self):
        current = datetime.now(timezone.utc) - timedelta(seconds=2)
        self.packet["job"]["verified_at"] = current.isoformat()
        self.packet["sources"]["job-page"]["observed_at"] = current.isoformat()
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(ROOT))
            path = Path(folder) / "synthetic.json"
            for expected, content in ((0, json.dumps(self.packet)), (2, "{}"), (1, "{")):
                with self.subTest(exit_code=expected):
                    path.write_text(content, encoding="utf-8")
                    result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(path)],
                                            capture_output=True, text=True, check=False)
                    self.assertEqual(expected, result.returncode, result.stderr + result.stdout)
                    json.loads(result.stdout)
                    self.assertEqual(content, path.read_text(encoding="utf-8"))

    def test_company_scoped_facts_and_sources_do_not_transfer(self):
        self.packet["facts"]["relatives"] = {"status": "confirmed", "value": False,
            "source_ids": ["candidate-confirmation"], "employer": "Other Employer"}
        self.packet["fields"].append({"name": "Company relatives", "required": True, "value": False, "fact_id": "relatives"})
        self.blocked("field_fact")
        self.packet["facts"]["relatives"]["employer"] = self.packet["job"]["employer"]
        self.assertTrue(self.check()["ready"])
        self.packet["sources"]["candidate-confirmation"]["job_id"] = "OTHER-JOB"
        self.blocked("field_fact")

    def test_empty_narrative_cannot_hide_an_unsupported_value(self):
        self.packet["fields"].append({"name": "Salary", "required": False, "value": "made up", "text": ""})
        self.assertFalse(self.check()["valid"])
        self.assertFalse(self.check()["ready"])

    def test_blank_fact_cannot_satisfy_a_hard_requirement(self):
        for empty in (None, " ", [], {}):
            self.packet["facts"]["degree"]["value"] = empty
            self.blocked("requirement_facts")

    def test_nested_values_use_type_strict_comparison(self):
        self.packet["facts"]["multi"] = {"status": "confirmed", "value": [True], "source_ids": ["resume"]}
        self.packet["fields"].append({"name": "multi", "required": True, "value": [1], "fact_id": "multi"})
        self.blocked("field_fact")
        self.packet["fields"][-1]["value"] = [True]
        self.assertTrue(self.check()["ready"])


if __name__ == "__main__":
    unittest.main()
