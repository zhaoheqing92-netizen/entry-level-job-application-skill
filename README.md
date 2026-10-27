# 初级岗位自动求职助手

这是一个供 AI 助手使用的求职工作流技能。它根据使用者授权读取简历、求职方向和附件，搜索各类企业的初级岗位，优先从企业官网及官网指向的招聘系统核实并申请。经授权后，它可以填写表单、上传适用材料、根据真实经历回答开放题，并在成功提交后继续寻找下一份合适的工作。

当申请要求填写多个志愿时，助手会先核查硬性条件，再从职业方向、已有能力、成长价值和实际条件等维度排序。它只勾选提交所必需且内容已核实的条款，记录真实状态，并在工具受阻时寻找可用的技能或工具继续处理。

## 适配哪些 Agent

核心采用通用 `SKILL.md + references/`，不依赖 Codex 专用工具。已按官方资料加入四个宿主的配置分支：

| Agent | 技能调用 | MCP 接入 |
|---|---|---|
| Codex | `$entry-level-job-application` | Codex CLI / TOML |
| Claude Code | `/entry-level-job-application` | Claude CLI / 对应作用域 |
| DeepSeek Harness | `/entry-level-job-application` | Cordis MCP 插件与 overlay |
| ZCode Agent | `$entry-level-job-application` | 原生 `mcp.servers` 或当前有效兼容来源 |

[跨 Agent 安装与配置](skills/entry-level-job-application/references/clients.md) 包含各自技能目录、命令、模板和配置冲突处理。以上是文档核实与配置检查，尚未逐个客户端做完整安装和投递实测。共享 MCP 已通过本机模拟表单测试，覆盖填写、双志愿、中文附件上传、可选营销取消及提交确认；详见[测试记录](TESTING.md)。`agents/openai.yaml` 仅是 Codex 扩展，其他 Agent 无需读取它。

## 如何使用

1. 在支持技能的 AI 助手中安装 `skills/entry-level-job-application` 目录，并提供网页搜索、读取本地文件和执行本地安装所需的权限。按上方适配指南选择该宿主的技能目录，复制整个文件夹以保留引用资源。
2. 告诉助手简历位置、求职方向、可接受地点、是否允许自动提交，以及可用于申请的附件和文件夹。助手会先读取现有信息，再集中询问无法确定且确实需要的信息。
3. 可说：“请加载 entry-level-job-application 技能，先识别当前 Agent 并初始化配套 MCP，再查找适合的初级岗位，在我授权的范围内填写并提交。”也可使用表中各客户端的快捷调用；也可以只要求搜索、评估或准备草稿。
4. 如果需要定期执行，明确频率、时区和通知方式；是否能定时取决于助手所在平台。说“暂停”即可停止后续操作，恢复后先核对上次进度。

## 遇到需要注册账号怎么办

- 先核对官网入口和已有账号，能免注册或复用登录就直接继续；不同企业的招聘系统分别核对，避免重复注册。
- 在授权范围内填写注册资料；按网站规则生成独立随机密码，先保存到用户已有的可信密码管理器并确认能找回，再注册。完成后告知条目位置和状态，不在聊天或申请日志展示密码。
- 验证码默认先检查官方 2Captcha MCP：服务可用、额度和解题余额足够且费用已获授权时优先使用；不可用或不足时转本地 `ddddocr` 图形识别。MCP 免费调用额度不等于免费解码，不会自动充值。复杂验证、本地无法识别或权限不允许时保留待办，详见 [验证码处理](skills/entry-level-job-application/references/captcha.md)。
- 已授权且账号匹配的邮箱验证可通过允许的工具处理；短信、扫码及需要本人完成的验证交接给用户，继续处理其他机会。
- 验证后回到原岗位续填；账号创建、草稿保存和申请成功分别记录。详见 [账号创建与恢复](skills/entry-level-job-application/references/accounts-and-recovery.md)。

## 内置 MCP 自动初始化

正式调用本技能执行求职流程时，助手先检测工具，自动安装缺失的依赖和配套 MCP、合并当前客户端配置并验证连接，再开始申请。MCP 实际运行环境为 Windows 时默认初始化 Playwright MCP 和 Windows-MCP；其他系统只初始化可支持的工具。远程、容器和 WSL 环境不自动共享本机桌面。已有可用配置直接复用，不重复安装或自动升级。

初始化属于技能工作流的一部分，包含必要的用户级下载和配置。用户已有此项授权时不重复确认；平台要求的权限审批和客户端重新加载仍需按提示处理。某项失败会保留进度并继续其他可做的工作。只阅读或修改技能不会触发安装。

## 配套 MCP

项目附有固定版本配置模板和[自动初始化指南](skills/entry-level-job-application/references/mcp.md)：

- **Playwright MCP**：读取招聘网页、查看表单、填写和上传文件，由微软 Playwright 项目维护。
- **Windows-MCP**：读取 Windows 窗口和屏幕状态，操作键鼠及应用窗口，由 CursorTouch 社区项目维护。

验证码分支按需接入 **2Captcha 官方 MCP**，无可用额度时使用本地 **ddddocr** 库；这两项的初始化、凭据要求与回退条件见 [验证码处理](skills/entry-level-job-application/references/captcha.md)。2Captcha 是该服务商的官方实现，不是招聘企业的验证接口；其本地 MCP 会连接远端服务。ddddocr 是离线识别库，不是 MCP，也不能保证通过所有人机验证。

这两项是独立的第三方开源 MCP 服务，**本仓库提供配置和使用流程，不包含它们的服务端源码**。安装和用户级配置已纳入技能启动流程，依赖也写入技能元数据。默认采用本机标准输入输出连接，不建立开机任务或自动接入个人浏览器会话；实际桌面操作只在需要时使用。

## 重要说明

- 该技能是操作指南，不是独立运行的程序。实际自动化能力取决于所用助手、权限、工具及招聘网站。
- 用户的简历、证件、附件、个人资料和申请记录应放在私有位置，切勿放进公开仓库；本仓库不包含真实求职者资料。
- 登录和注册按授权处理；需要本人验证、缺少必填事实或条款不适用时，助手会保留待办并推进其他机会，完成后可恢复，不会猜测、绕过或谎报成功。
- 技能不会保证录用，也不能代替本人参加测评或面试。

## 文件

- [技能说明](skills/entry-level-job-application/SKILL.md)
- [信息收集与隐私](skills/entry-level-job-application/references/intake-and-privacy.md)
- [岗位与志愿评分](skills/entry-level-job-application/references/scoring.md)
- [账号创建与恢复](skills/entry-level-job-application/references/accounts-and-recovery.md)
- [验证码处理](skills/entry-level-job-application/references/captcha.md)
- [跨 Agent 安装与配置](skills/entry-level-job-application/references/clients.md)
