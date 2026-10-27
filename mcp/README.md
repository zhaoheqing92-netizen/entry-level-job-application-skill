# MCP 自动安装与配置

Playwright MCP 与 Windows-MCP 已作为本技能的配套依赖写入元数据，并由求职流程的第 0 步识别宿主后自动检测、安装、配置及验证。非 Codex 宿主按通用正文执行，不依赖 Codex 元数据。Windows 默认补齐两项，非 Windows 跳过 Windows-MCP；已有可用配置直接复用。

实际执行以技能内的 [MCP 自动安装与初始化](../skills/entry-level-job-application/references/mcp.md) 为准，其中包含依赖安装、配置保护、失败恢复和连接验证；各宿主命令与路径见 [跨 Agent 适配](../skills/entry-level-job-application/references/clients.md)。只复制或阅读本仓库不会自行启动安装，须由支持执行本地操作的助手运行技能。

## 配置模板

- [mcpServers 外壳示例](mcp-config.example.json)：仅供明确支持该结构的入口使用。
- [Codex TOML](codex-config.example.toml)
- [Claude Code 项目 .mcp.json 示例](claude-code.example.json)：用户级优先使用 CLI，不覆盖 ~/.claude.json。
- [DeepSeek Harness Cordis overlay](deepseek-harness.cordis.example.yaml)：合并到当前生效 patch。
- [ZCode 原生配置示例](zcode.example.json)：使用 mcp.servers，注意原生与 .agents 来源优先级。
- [2Captcha 官方服务示例](2captcha-config.example.json)：仅在验证码分支需要且已获授权时合并；须安全注入 `API_TOKEN`，模板不包含凭据。其他宿主按自身配置结构映射同一命令、参数和工具白名单，详见 [验证码处理](../skills/entry-level-job-application/references/captcha.md)。

各宿主模板使用相同的固定版本：Playwright MCP 0.0.83、Windows-MCP 0.8.8；Windows-MCP 通过 uv 使用 Python 3.14，关闭匿名遥测并限制桌面工具。安装前核对上游元数据，不覆盖已有可用版本。

模板用于合并缺失的服务项，不能覆盖整份客户端配置。备份、运行记录及凭据保存在用户私有位置；不会自动安装浏览器扩展、创建开机任务或开放远程访问。

## 上游与账号

- [Playwright MCP 固定版本说明](https://github.com/microsoft/playwright-mcp/blob/v0.0.83/README.md)
- [Windows-MCP 发布包元数据](https://pypi.org/project/windows-mcp/0.8.8/)
- [账号创建与恢复](../skills/entry-level-job-application/references/accounts-and-recovery.md)

本仓库不包含上述服务端源码。邮箱、密码管理与本人验证需要单独可用且获授权的能力，MCP 初始化成功不能替代申请提交或账号验证。
