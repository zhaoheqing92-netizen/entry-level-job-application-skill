# 示例配置：只补齐缺少的工具

已有浏览器或桌面工具可用时，直接复用，无须安装本目录中的 MCP。普通聊天网页不一定支持本地技能或 MCP；先确认客户端具备这些能力。

## 选哪个文件

| 需要什么 | Codex | Claude Code |
| --- | --- | --- |
| 网页读取、填写与上传 | codex-playwright.example.toml | claude-playwright.example.json |
| 操作 Windows 原生窗口（可选） | codex-windows-optional.example.toml | claude-windows-optional.example.json |

浏览器工具通常已能完成网页申请。只有确需操作 Windows 原生窗口时再加桌面工具。Windows-MCP 需要实际可交互的 Windows 桌面，不能默认在 Linux、WSL 或云端会话中使用。

## 最短使用步骤

1. 让 Agent 列出当前可用工具，判断究竟缺什么。
2. 确认当前客户端、系统、配置作用域和真实可执行文件路径。
3. 备份原配置，只合并缺失的服务条目；同名服务已存在时先比较，不新增重复键。
4. 重载 MCP 或客户端，检查服务启动是否成功。
5. 先用空白网页或虚构资料验证读取、输入和上传能力，再使用真实申请材料。

不要把示例中的整个文件覆盖到现有配置上。保留原来的服务、密钥、权限和禁用设置。这里没有安装脚本，也不会自动下载软件。

## Codex

将选用的 TOML 表合并到当前生效的配置。用户级常见位置是 `~/.codex/config.toml`；不要在同一文件内重复创建 `[mcp_servers.playwright]` 等同名表。

技能目录与 MCP 配置目录不是一回事：当前官方技能文档的用户级位置为 `~/.agents/skills/`，项目级为 `.agents/skills/`。已有自定义或旧版安装应按客户端实际发现结果处理，不重复搬迁。

## Claude Code

JSON 文件是项目级 `.mcp.json` 的结构示例，服务条目在 `mcpServers` 下。若已有该文件，只合并选中的服务对象。

用户级配置优先使用当前版本支持的 `claude mcp add` 命令与用户作用域；这些示例不是完整的 `~/.claude.json`，不可拿来覆盖该文件。项目级服务可能需要客户端确认信任或启用。

## 运行前提与固定版本

- Playwright MCP 使用项目既有版本 `@playwright/mcp@0.0.83`；需要 Node.js 和 npx。该版本文档要求 Node.js 18+，新安装建议使用仍受支持的 Node.js LTS。浏览器依赖按 MCP 实际报错处理。
- Windows-MCP 使用 `windows-mcp==0.8.8`，该版本元数据要求 Python 3.14+；示例由 uvx 管理 Python 3.14，首次运行可能下载依赖。需要事先安装 uv 并让 uvx 可被客户端找到。
- 这是与原技能配套的固定版本，不代表最新版本，也不代表在每个客户端均已实测。
- 示例使用 `npx` 和 `uvx` 命令名。如果宿主无法找到命令，先定位真实可执行文件，再按宿主要求调整。不要盲目调用会打开微软商店的 Windows Python 执行别名。
- Windows-MCP 示例仅暴露截图、查看、点击、输入、滚动等列出的桌面工具，并关闭匿名遥测；仍需遵循宿主的授权规则。

## 私有文件与验证

在私有求职工作目录中操作，简历、证书、浏览器快照、下载内容、账号资料和申请记录不要放在开源仓库里。按实际工具支持的方式设置私有输出目录；不要为了上传简历开启任意磁盘访问。

配置文件可被解析，只说明语法正确。服务出现在工具列表、页面可以操作、附件可上传是后续不同检查。安装成功不等于已经投递，购买技能也不等于授权对外提交申请。

DeepSeek Harness、ZCode 等宿主先按它们当前版本的配置规范操作。安装包中的 `references/clients.md` 和 `references/mcp.md` 提供适配参考；不要把上述格式直接照搬到不支持的客户端。

## 官方参考

- [Codex 技能目录](https://learn.chatgpt.com/docs/build-skills)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Claude Code 技能](https://code.claude.com/docs/en/skills)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Playwright MCP 固定版本说明](https://github.com/microsoft/playwright-mcp/blob/v0.0.83/README.md)
- [Windows-MCP 0.8.8 元数据](https://pypi.org/project/windows-mcp/0.8.8/)
- [Windows-MCP 项目](https://github.com/CursorTouch/Windows-MCP)

整理日期：2026-11-09。未修改用户现有 MCP 配置，未执行安装或真实投递。