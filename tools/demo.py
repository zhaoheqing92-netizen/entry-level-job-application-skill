"""Offline fictional demonstration; no employer, account, browser or payment requests."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import html
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/entry-level-job-application/scripts"))
from check_application import check_packet
from application_state import Ledger, StateError


def run_demo():
    now = datetime(2026, 11, 8, 2, 30, tzinfo=timezone.utc)
    base = json.loads((ROOT / "skills/entry-level-job-application/assets/application.example.json").read_text(encoding="utf-8"))
    cases = []

    def check(name, packet, expected):
        result = check_packet(packet, now=now)
        cases.append({"name": name, "expected_ready": expected, "actual_ready": result["ready"],
                      "passed": result["ready"] is expected, "issues": [i["code"] for i in result["issues"]],
                      "warnings": result.get("warnings", []), "score_range": result["score_range"]})

    check("完整且已核对的虚构申请", base, True)
    p = deepcopy(base)
    p["requirements"]["graduation"]["status"] = "fail"
    p["fit"] = {name: 5 for name in base["fit"]}
    check("毕业届别硬性不符，满分不能抵消", p, False)
    p = deepcopy(base)
    p["facts"]["graduation"]["status"] = "conflict"
    check("毕业资料存在冲突", p, False)
    p = deepcopy(base)
    p["sources"]["job-page"]["observed_at"] = "2026-10-01T10:00:00+08:00"
    check("新检查时间不能替换旧官网证据", p, False)
    p = deepcopy(base)
    p["requirements"]["experience"] = {"status": "not_stated", "source_id": "job-page", "note": "完整虚构JD未写经验限制"}
    check("完整JD没有经验限制，保留提醒并继续", p, True)
    p = deepcopy(base)
    p["terms"][1]["selected"] = True
    check("可选营销被误选", p, False)
    p = deepcopy(base)
    p["fields"][2]["employer"] = "Another Employer"
    check("另一公司的开放题不能直接套用", p, False)
    p = deepcopy(base)
    p["attachments"][0]["language"] = "zh"
    check("英文栏位不能上传中文版本", p, False)

    workflow = []
    with tempfile.TemporaryDirectory(prefix="job-skill-demo-", dir=ROOT.parent) as folder:
        assert Path(folder).resolve().parent == ROOT.parent.resolve()
        ledger = Ledger(Path(folder) / "fictional.sqlite")
        def expect(label, expected, action):
            try:
                action()
                actual = "accepted"
            except StateError:
                actual = "blocked"
            workflow.append({"name": label, "expected": expected, "actual": actual, "passed": expected == actual})
        try:
            ledger.handoff(base, "虚构页面等待本人验证", now)
            expect("本人验证未完成时阻止提交", "blocked", lambda: ledger.begin(base, now))
            e = {"candidate_ref": base["candidate_ref"], "job": base["job"],
                 "observed_at": (now + timedelta(minutes=1)).isoformat(), "reference": "synthetic:observation-1",
                 "kind": "live_form", "status": "ready_to_resume", "blocker_resolved": True}
            ledger.reconcile(base, e, now + timedelta(minutes=2))
            expect("核对已解决卡点后开始一次提交", "accepted", lambda: ledger.begin(base, now + timedelta(minutes=3)))
            ledger.unknown(base, now + timedelta(minutes=4))
            expect("超时结果不明时阻止重复提交", "blocked", lambda: ledger.begin(base, now + timedelta(minutes=5)))
            e.update(kind="application_record", status="submitted", observed_at=(now + timedelta(minutes=6)).isoformat())
            ledger.reconcile(base, e, now + timedelta(minutes=7))
            expect("已确认提交后继续阻止重复", "blocked", lambda: ledger.begin(base, now + timedelta(minutes=8)))
            final = ledger.get(base)["status"]
        finally:
            ledger.close()
    return {"evaluation_type": "simulation_only", "generated_at": datetime.now(timezone.utc).isoformat(),
            "fixture_time": now.isoformat(), "external_submissions": 0, "payment_transactions": 0,
            "cases": cases, "workflow": workflow, "final_state": final,
            "passed": all(c["passed"] for c in cases + workflow),
            "limits": "Synthetic regression checks only; not live ATS reliability, agent benchmark, payment integration or hiring outcomes."}


def render(report):
    rows = []
    for case in report["cases"] + report["workflow"]:
        rows.append("<tr><td>" + html.escape(case["name"]) + "</td><td>" + ("通过" if case["passed"] else "失败") + "</td></tr>")
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>初级岗位求职助手 · 离线演示</title><style>body{max-width:880px;margin:48px auto;padding:0 24px;font:17px/1.7 system-ui;color:#17283a;background:#f8fafc}"
            "table{width:100%;border-collapse:collapse;background:white}th,td{padding:12px;text-align:left;border-bottom:1px solid #d6dee7}"
            "aside{padding:16px;background:#e8eff9;border-radius:8px}code{overflow-wrap:anywhere}</style>"
            "<h1>初级岗位自动求职助手</h1><p>用户给简历和目标，助手核实官网岗位、准备材料，在授权范围内申请。</p>"
            "<aside><strong>这是离线虚构演示。</strong>没有真实招聘网站提交，没有支付交易，也不代表已获得面试或录用。</aside>"
            "<h2>本次实际运行的检查</h2><table><thead><tr><th>场景</th><th>结果</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
            "<h2>模拟恢复过程</h2><p>等待本人验证 → 核对页面 → 提交中 → 结果未知 → 查询模拟回执 → 已提交；重复 begin 被阻止。</p>"
            "<p>工具只检查输入一致性；来源真假、语义与网站操作仍由 Agent 核验。真实客户端、ATS 和支付需分别验收。</p>"
            "<p>生成时间：<code>" + html.escape(report["generated_at"]) + "</code></p></html>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write fictional JSON and HTML report to this directory")
    args = parser.parse_args()
    report = run_demo()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "demo.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.output / "demo.html").write_text(render(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
