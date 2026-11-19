# 2026-11-19 求职申请提交方式变更

**自动提交默认关闭。** 申请准备好后，助手展示公司、岗位、所用附件和官网入口，停在最后一步，等待用户本人提交。用户看过当前最终申请，并在此刻明确要求助手代交，助手才可以提交这一份。换岗位、修改申请、恢复或重试均须重新确认。

## 原行为与改动依据

原版搜索和本地草稿本身不会投递。进入代投流程后，技能明确要求沿用持续提交授权。只要已保存的 `authorization.submit=true` 与候选人、岗位范围及其余检查相符，`begin` 就能进入 `submitting`。旧版回归复现中，未提供当刻确认的 CLI 调用退出码为 0，台账进入了该状态。原有检查覆盖资格、暂停、重复投递等条件，缺少逐份当刻确认，因此需要改执行入口。

新版沿用原来的身份键、事务和交接状态。材料检查通过给出 `next_action=await_user_submission`，助手通过 `handoff` 留在 `waiting_user`。发现历史偏好或旧的 `submit:true`，助手须指出该设置，告知用户如需代交，应在最后一步重新确认。新包示例省略 `submit`。旧的 `submit:false` 仍禁止代交，允许本人提交。

代交确认采用每次调用单独传入的 `begin --confirm-submit-now APPLICATION_KEY`，沿用候选人、雇主、岗位编号及批次组成的键。这样旧 JSON 和旧命令即使原样重放，也不能进入提交中。这个键只标识申请。宿主负责核实用户刚刚看过最终申请并明确同意；脚本无法鉴别聊天答复，也无法禁止宿主自行操作浏览器。

## 提交路径审计

| 路径 | 新默认下的行为与边界 |
|---|---|
| 官网或雇主 ATS 的最终按钮，包括浏览器、Playwright MCP、Windows 桌面及无 Python 宿主 | 技能要求停在按钮前。无 Python 时沿用同一确认规则并记入可靠私有记录；缺少可靠记录时交给本人提交。这是宿主执行的规则。仓库没有直接点击招聘网站或发送投递请求的适配器。 |
| `check_application.py`、`Ledger.begin` 及其 CLI | 检查脚本只读。普通 `begin` 和仅含旧授权的调用都会被拦住；带错申请键也会失败。仅在当前确认、范围、材料、暂停状态及去重检查均通过后才记录 `submitting`，随后宿主可代点一次。 |
| 本人提交、交接、恢复、重试及并发 | 本人提交后可从 `waiting_user` 凭正式回执记账，无需代交。`resume` 只解除暂停；“继续”、验证码完成或回到草稿均不能授权代交。结果未知时先查官网，得到确定未提交的证据后仍需当刻确认。并发 `begin` 只允许一个进入。 |
| 多岗位、定时任务、旧偏好及工具配置 | 可以在原有权限内继续准备其他申请。数量上限、调度、已连接的 MCP 和旧配置均不能授权最终提交。仓库中的 MCP 示例只配置工具连接。 |
| 教程、复制用提示词、示例及演示 | 交互指南默认本地草稿。第四项改为“核对已填申请”，批量范围只控制核对份数。页面、文本及 PDF 都说明逐份交接；演示只操作虚构数据和本地台账。 |
| 当前安装及下载入口 | 双语 README 和教程 README 指向下方候选包。源教程直链的独立技能 ZIP 也已重建。两种安装方式均含新规则和脚本。 |
| 历史包、已安装副本、线上交付 | 人工另行安装旧包仍可启用旧流程。已核对 `dist/` 的 5 个日期归档及未替换的 `downloads/entry-level-job-application-with-guide.zip` 含原持续授权指令。仓库修改不会更新用户已有安装；线上 SkillPay 文件需由秘书核验并发布。 |

审计覆盖本项目的技能、脚本、调用方、宿主配置、客户入口和本地 ZIP。历史开发启动脚本用于运行开发任务，未发现独立投递实现。依任务边界，`growth-20261119/` 和 `evaluation/` 均排除在检查与改动之外。

## 测试记录

| 实际执行的检查 | 通过 | 失败 |
|---|---:|---:|
| 改动前 Python 全套测试 | 40 | 0 |
| 改动后 `python -B -m unittest discover -s tests -v` | 43 | 0 |
| 源教程 `node tools/test_guide.cjs` 离线浏览器套件 | 1 套 | 0 |
| `python -B tools/demo.py` 虚构数据演示 | 8 个材料场景、5 个流程场景 | 0 |
| 从实际候选 ZIP 解压后复跑材料及台账测试 | 40 | 0 |
| 对解压后的客户教程复跑相同浏览器套件 | 1 套 | 0 |

最终 43 项包括 26 项材料检查、14 项台账测试和 3 项交付测试。新增回归覆盖保存的 `submit:true`、JSON 内伪装的确认、未传确认参数、错申请键、本人交接与回执、当前代交及重试；暂停和并发去重检查继续通过。教程新增断言在旧版能复现提前授权，更新后通过。浏览器测试使用本机 Playwright 和 Edge，禁止 HTTP(S) 请求。无 Python 分支按技能文本推演了“旧授权加继续”和“确认后表单改变”两种情况，均应停下。真实招聘投递为 0 次。

## 本地交付包

沿用上次的 `python -B tools/package_skill.py --with-guide --output <暂存候选包路径>`，在 `downloads/` 中暂存构建。核对 24 个成员的清单、CRC、23 个直接收录文件与源码的字节一致性及客户版 HTML 的安装入口，解包复测通过后替换同名候选文件。

| 文件 | 大小（字节） | SHA-256 |
|---|---:|---|
| [SkillPay 候选包](downloads/entry-level-job-application-with-guide-candidate-20261119.zip) | 424051 | `e4372ac516af0e99c22fefc1b085ec100515a3d049aadff1f706c4aca7a769a3` |
| [源教程链接的独立技能包](docs/starter-kit/entry-level-job-application.zip) | 48834 | `8aae952ef7bd823d4433291082800f0f5c7e693448da695b1678988f47cac41b` |

独立技能包的 14 个成员均通过 CRC 和逐文件比对。保留的旧版 `downloads/entry-level-job-application-with-guide.zip` 的 SHA-256 仍为 `c88b7d57d43a6f774809a045339164371cd2ed451728f2779083ebfa4d585bec`。本次只准备本地候选交付，没有推送 GitHub 或替换 SkillPay 线上文件。

## 变更文件

- 技能目录 `skills/entry-level-job-application/` 下的 `SKILL.md`、`scripts/check_application.py`、`scripts/application_state.py`、`assets/application.example.json`、`references/execution.md`、`references/evidence.md`、`references/intake-and-privacy.md`、`references/accounts-and-recovery.md`。
- 用户文档与教程包括 `README.md`、`README.en.md`、`docs/customer-start.txt`，以及 `docs/starter-kit/` 下的 `README.md`、`guide.html`、`guide.pdf`、`prompts/02-authorized-apply.txt`。PDF 从教程的打印版重新生成，已检查单页 A4 的文本边界及新授权说明。
- 验证及记录包括 `tests/test_application_state.py`、`tests/test_check_application.py`、`tools/test_guide.cjs`、`tools/demo.py`、`docs/demo.md`、`TESTING.md` 和本文件 `AUTOSUBMIT_CHANGE.md`。
- 交付产物为上表两个 ZIP。项目未发现独立 changelog 或 release notes 惯例，本次记录使用本文件和现有测试索引。
