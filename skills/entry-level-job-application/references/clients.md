# 跨 Agent 安装与配置

核对日期：2026-10-27。下列入口按官方文档整理，配置文件做过语法与一致性检查；未逐个客户端完成安装、浏览器操作和真实投递测试，不标为端到端验证通过。

## 先识别真正执行任务的宿主

依据当前运行环境、工具清单、客户端版本和实际生效配置确认宿主，不能凭模型名称、桌面窗口品牌或机器上存在某个 CLI 就决定。使用 DeepSeek 模型不一定在 DeepSeek Harness；外层应用里的其他 Agent 也未必读取外层的配置。只配置当前执行宿主，不为本机所有 Agent 批量安装。

同时确认 MCP 子进程实际运行的主机、系统和文件权限。SSH、容器、WSL 或云端不会自动获得本机 Windows 桌面和简历路径。Windows-MCP 只部署到获授权且可访问交互桌面的 Windows 运行环境，不因用户电脑是 Windows 就在 Linux 中安装。

核心是标准 `SKILL.md` 和 `references/`，整目录复制才能保留相对引用。`agents/openai.yaml` 是 Codex 附加元数据，其他宿主无需识别；不能把其中依赖声明当成通用自动安装器。安装步骤由助手按 [MCP 初始化](mcp.md) 执行。

## 技能发现与调用

所有路径按实际宿主的用户目录展开；已有自定义技能根时优先复用，不覆盖同名技能。

| 宿主 | 放置完整技能目录 | 调用 |
|---|---|---|
| Codex | 当前宿主已启用的技能根，如 `~/.codex/skills/entry-level-job-application/`；以本机发现配置为准 | `$entry-level-job-application` |
| Claude Code | `~/.claude/skills/entry-level-job-application/`；项目级为 `.claude/skills/entry-level-job-application/` | `/entry-level-job-application` |
| DeepSeek Harness | 默认 `~/.dsh/skills/entry-level-job-application/`；项目级为 `.dsh/skills/entry-level-job-application/` | `/entry-level-job-application` |
| ZCode Agent | `~/.zcode/skills/entry-level-job-application/`，或“设置 → 技能 → 导入” | `$entry-level-job-application` |

DeepSeek Harness 的 `DSH_HOME` 可更改用户根，也支持 `.agents/skills` 与自定义提供者；只扫描直接技能目录，不把整个仓库再套一层。ZCode 导入后刷新并确认启用，复制方式后续需重新同步，软链需保持来源有效。Claude Code 未发现新增目录时按当前客户端的技能刷新方式处理；发现文件存在不等于已经进入模型技能目录。

通用调用文字：“请加载 entry-level-job-application 技能，识别当前 Agent 并初始化配套 MCP，再按我的简历和授权处理求职申请。”不强迫不支持 `$` 或 `/` 的宿主使用特定前缀。

来源：[Agent Skills 格式](https://agentskills.io/specification)、[Claude Code 技能](https://code.claude.com/docs/en/skills)、[DeepSeek 文件系统技能](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[DeepSeek 技能调用](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/tool-skill/README.md)、[ZCode 技能](https://zcode.z.ai/cn/docs/skill)。

## MCP 配置分支

下列命令和模板都只用于已经核对且不存在的服务。先检查所有生效作用域、备份并增量合并；不得绕过主动禁用、同名冲突、管理员策略或审批。服务包版本与下载步骤统一见 [MCP 初始化](mcp.md)。只复制技能目录时，可直接用本页内嵌示例，不依赖仓库根目录的模板文件。

### Codex

先用本机 `codex mcp --help` 和 `codex mcp list --json` 确认参数及已有服务；输出时过滤凭据。当前 CLI 示例：

```text
codex mcp add playwright -- npx -y @playwright/mcp@0.0.83
codex mcp add windows-mcp --env ANONYMIZED_TELEMETRY=false -- uvx --python 3.14 --from windows-mcp==0.8.8 windows-mcp serve --transport stdio --tools Screenshot,Snapshot,Click,Type,Scroll,Move,Shortcut,WaitFor,ControlStatus
```

只在 Codex 分支调用这些命令。新增后重读目标配置并检查当前会话工具连接，不能因 CLI 返回成功就声称可调用。

### Claude Code

优先 CLI，避免把用户级服务误写进 `settings.json`。默认 MCP local scope 仅当前项目私有；跨项目的 user scope 存在 `~/.claude.json`；project scope 使用项目根 `.mcp.json`。本流程默认用户级，用户指定项目级时再改 scope：

```text
claude mcp list
claude mcp add --transport stdio --scope user playwright -- npx -y @playwright/mcp@0.0.83
claude mcp add --transport stdio --scope user windows-mcp --env ANONYMIZED_TELEMETRY=false -- uvx --python 3.14 --from windows-mcp==0.8.8 windows-mcp serve --transport stdio --tools Screenshot,Snapshot,Click,Type,Scroll,Move,Shortcut,WaitFor,ControlStatus
```

CLI 参数先与本机 `claude mcp add --help` 核对。Windows 若实际出现 `.cmd` 启动问题，再使用客户端支持的 `cmd.exe /d /c npx ...` 兼容启动方式，不把包装方式写死到其他系统。用 `claude mcp get <名称>` 和会话内 `/mcp` 核查；项目配置审批、会话重启及受管限制按客户端处理。

项目 `.mcp.json` 的形状是 `{"mcpServers": {"playwright": {"type": "stdio", "command": "npx", "args": ["-y", "@playwright/mcp@0.0.83"]}}}`；不要把这份完整对象覆盖用户 `~/.claude.json`。依据：[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)。

### DeepSeek Harness

使用 Cordis 的 MCP 客户端插件，不使用 Codex TOML 或 `mcpServers`。先确定当前 profile、`DSH_HOME` 和实际组合层；默认用户根是 `~/.dsh`。

持久化优先合并到当前 profile 的 `<DSH_HOME>/profiles/<name>/cordis.patch.yml`。仅当用户需要跨 profile 时使用 `<DSH_HOME>/cordis.patch.yml`。检查现有插件 `id`、`serverName` 与来源，避免多个 insert 重复启动同一服务；保留其他 patch：

```yaml
# 合并到当前 profile 的 Cordis patch；不是 mcpServers JSON。
# 非 Windows 运行环境请移除 windows-mcp 条目。
- insert:
    - id: job-application-playwright
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: playwright
        transport: stdio
        command: npx
        args: ['-y', '@playwright/mcp@0.0.83']
    - id: job-application-windows-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: windows-mcp
        transport: stdio
        command: uvx
        args: ['--python', '3.14', '--from', 'windows-mcp==0.8.8', 'windows-mcp', 'serve', '--transport', 'stdio', '--tools', 'Screenshot,Snapshot,Click,Type,Scroll,Move,Shortcut,WaitFor,ControlStatus']
        env:
          ANONYMIZED_TELEMETRY: 'false'
```

CLI/Web 可使用 `dsh web --patch <overlay文件绝对路径>` 一次加载本模板；桌面版由其自身 profile/设置管理，不用该命令假装启动桌面版。修改后按当前宿主支持的方式重新加载配置，等待当前调用范围能看到对应工具再验证。只有使用默认配置包含的 MCP 客户端能力时才直接插入；自定义部署先核查该插件及工具服务是否可用。

依据：[MCP 插件字段](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md)、[overlay 与持久化](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/mcp-memory.md)、[CLI/Profile](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)。

### ZCode Agent

优先检测“设置 → MCP 服务器”的生效来源，也可读取原生配置：

- 用户级 `~/.zcode/cli/config.json`、工作区级 `.zcode/config.json`：键为 `mcp.servers`。
- 同作用域的 `.agents/mcp.json` 只作兼容回退，键为 `mcpServers`。原生文件出现任一服务后，会整组遮蔽该回退来源。
- 因此优先修改当前有效来源。原来只用 `.agents` 时继续增量编辑那里；切换原生来源前必须保留已有服务，不能只加入新服务而使旧配置失效。保持 `enable: false` 的禁用状态。

原生配置示例，合并子项而非覆盖整个文件：

```json
{
  "mcp": {
    "servers": {
      "playwright": {
        "command": "npx",
        "args": [
          "-y",
          "@playwright/mcp@0.0.83"
        ]
      },
      "windows-mcp": {
        "command": "uvx",
        "args": [
          "--python",
          "3.14",
          "--from",
          "windows-mcp==0.8.8",
          "windows-mcp",
          "serve",
          "--transport",
          "stdio",
          "--tools",
          "Screenshot,Snapshot,Click,Type,Scroll,Move,Shortcut,WaitFor,ControlStatus"
        ],
        "env": {
          "ANONYMIZED_TELEMETRY": "false"
        }
      }
    }
  }
}
```

若使用设置界面，“完整配置”输入接受单层服务映射或 `mcpServers`，它不同于磁盘原生 `mcp.servers` 包装。通过界面添加时先确认不会遮蔽现有回退配置。添加后检查服务状态及当前会话工具；不要编造 `zcode mcp add` 命令。依据：[ZCode MCP](https://zcode.z.ai/cn/docs/mcp-services)。

## 其他 Agent 与能力不足时

先查实际宿主的官方技能格式、MCP transport、配置作用域和管理接口，再选择分支；`mcpServers` 只是常见格式，不是所有客户端通用文件格式。若没有技能发现机制但允许读取文件，可让助手直接读取 `SKILL.md` 及按需引用的文件，不能称为原生技能安装成功。

- 有本地文件/命令和 stdio MCP：可以执行自动初始化，仍需握手及实际功能检查。
- 只有远程 MCP 或纯聊天 API：不能靠导入 Markdown 获得本机桌面能力；先完成搜索、评估或文案，明确缺少的执行能力，不临时公开本机桌面服务。
- 没有特定提问工具时用普通对话补问；没有调度器时不能承诺自动定时。工具名称映射到当前宿主已发现的能力，不硬编码 Codex 的工具名。
- 浏览器填表、文件上传和桌面操作各自核验。跨设备文件路径或不支持图像的模型可能限制操作，保留待办而非冒充成功。

兼容性分别报告“技能已发现、配置格式已核对、MCP 已连接、实际操作已验证”；不要将前两项写成全部自动投递已实测。
