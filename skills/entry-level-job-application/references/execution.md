# 提交检查和恢复工具

仅在自动提交或需要可靠恢复时读取。用户只提供简历、目标和授权；下面的输入由助手整理，不能要求用户手填 JSON。

两个 Python 3.10+ 标准库脚本，无第三方依赖，不联网、不控制浏览器、不安装软件、不处理密码。没有运行能力时沿用现有私有记录，不为它们强制安装 Python。

## 提交前

复用已确认的候选人事实，为当前岗位形成[证据输入](evidence.md)。保存到用户授权的私有目录，不能放在技能仓库内。命令中的 `<skill>`、`<private>` 由助手换成实际已验证路径。

```text
python "<skill>/scripts/check_application.py" --input "<private>/application.json"
```

`ready=true` 只表示结构化检查通过，不证明网页真实、不保证雇主接受资格，也不代表申请成功。开放题仍由助手对照原始材料核查；不能为过检查虚构来源或添加未经实际核对的 `reviewed` 标志。

## 持久状态

同一候选人的协作 Agent 共用一个私有数据库和稳定标识。不要每轮重建数据库、换候选人别名或招聘批次来绕过去重。`candidate_ref` 是私有不透明代号；雇主与岗位编号沿用已规范的官方标识。数据库外的申请历史仍需先查，不能自动发现。

```text
python "<skill>/scripts/application_state.py" --db "<private>/applications.sqlite" status --input "<private>/application.json"
python "<skill>/scripts/application_state.py" --db "<private>/applications.sqlite" begin --input "<private>/application.json"
```

`begin` 重跑检查，并以 SQLite 事务检查暂停和重复状态，保存 `submitting`。**只有这一步成功才点击一次网页提交**。点击前后进程中断都先核对官网，再恢复。

| 状态 | 下一步 |
|---|---|
| new / draft | 补齐材料，核对当前页面，获授权后 begin |
| waiting_user | 用户处理后重新观察页面，不能凭“继续”解除卡点 |
| submitting / unknown | 查询官方结果；禁止重点击或再次 begin |
| submitted | 跳过，不重置为草稿 |

`handoff --reason "不含隐私的卡点"` 记录人工接管；`unknown` 记录结果不明，均带 `--input`。`pause` / `resume` 设置共享暂停标志，后者只在用户恢复授权后调用。暂停仍可核对已经发出的请求；它不是操作系统级终止按钮，助手也须停止浏览器动作与调度。

## 观察回执后恢复

观察记录沿用同一 `candidate_ref` 和 `job` 身份：

```json
{
  "candidate_ref": "demo-candidate",
  "job": {"employer": "Example Engineering", "job_id": "ENTRY-1", "cycle": "2027"},
  "kind": "application_record",
  "status": "submitted",
  "observed_at": "2026-11-08T08:02:00+00:00",
  "reference": "private-observation-1"
}
```

```text
python "<skill>/scripts/application_state.py" --db "<private>/applications.sqlite" reconcile --input "<private>/application.json" --evidence "<private>/observation.json"
```

- 确认提交：`kind=success_page` 或 `application_record`，`status=submitted`；对应账号和岗位，观察时间在本次动作之后，`reference` 指向实际私有证据。
- 允许重试：官网明确确认未提交，`kind=application_record`、`status=not_submitted`、`definitive=true`。列表暂未显示、未收到邮件或超时不是确定未提交。
- 接管后续填：重新核对已登录的对应表单和申请历史，`kind=live_form`、`status=ready_to_resume`、`blocker_resolved=true`。已提交则记录真实提交结果。

观察需带时区且在24小时内。只存最小私有引用，不存密码、验证码、令牌链接或整页个人资料；数据库不是密码库，不自行加密，应使用用户已有私有存储。

两份脚本须一起保留。只通过 MCP 加载文本的市场未必支持本地脚本执行；先确认交付方式，不能把“已上架”写成“全部客户端已验证”。
