# 求职技能的公开研究与本轮取舍

核实日期：2026-11-09。Star是关注度，不是使用人数、面试率或成功率。本轮读取公开说明、技能文件和故障报告，没有安装或运行竞品。

## 关注度与值得借鉴的方法

| 项目 | 当日关注度与统计范围 | 本轮采用的思路 |
|---|---|---|
| [career-ops](https://github.com/career-ops-hq/career-ops) | GitHub页面约81.3k；完整求职框架 | 岗位筛选先于材料投入，产物和岗位可追溯 |
| [ai-job-search](https://github.com/ai-job-search-dev/ai-job-search) | GitHub API 70,759；完整框架 | 官网页面与岗位材料关联，工具结果要验证 |
| [ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills) | GitHub API 3,096；20个技能合集总数 | 保留母版，按具体职责调整表达并说明改动 |
| [resume-tailoring-skill](https://github.com/varunr89/resume-tailoring-skill) | GitHub API 865；独立技能 | 多岗位复用已确认素材，导出受限时交付完整文本 |
| [get-job.skill](https://github.com/agentenatalie/get-job.skill) | GitHub API 735；独立技能，页面缓存曾显示734 | 可迁移能力必须有真实经历，已提交版本保留 |
| [ASu-resume-skills](https://github.com/Claycui828/ASu-resume-skills) | GitHub API 430；生成和审计技能包 | 区分个人贡献与团队成果，区分用户确认与独立核验 |

读取的关键原文件：[ResumeSkills定制模块](https://github.com/Paramchoudhary/ResumeSkills/blob/main/skills/resume-tailor/SKILL.md)、[resume-tailoring入口](https://github.com/varunr89/resume-tailoring-skill/blob/master/skills/resume-tailoring/SKILL.md)、[get-job入口](https://github.com/agentenatalie/get-job.skill/blob/main/SKILL.md)、[ASu审计模块](https://github.com/Claycui828/ASu-resume-skills/blob/main/skills/asu-resume-audit-skill/SKILL.md)。

## 真实反馈与证据强弱

- [ai-job-search #536](https://github.com/ai-job-search-dev/ai-job-search/issues/536)：使用者提供不同查询写法的结果对照，维护者确认搜索模板与各平台语法不匹配。这里学的是按工具能力构造查询、空结果先诊断，不是使用所有第三方投递渠道。
- [career-ops #3887](https://github.com/career-ops-hq/career-ops/issues/3887)：有复现步骤的附件索引冲突，求职信覆盖了同岗位的简历引用；维护者已确认并修复。用实际文件内容、用途及岗位校验避免混用。历史报告不代表最新版仍有此问题。
- [ai-job-search v1.3.0发布记录](https://github.com/ai-job-search-dev/ai-job-search/releases)：维护者引用用户报告，PDF日期文本提取出错影响ATS导入。视觉与文本读取都需要检查，不宣称一次检查能证明所有ATS兼容。
- [resume-tailoring #7](https://github.com/varunr89/resume-tailoring-skill/issues/7)：两名用户描述技能文件嵌套导致安装后不被发现。本项目已有根目录SKILL.md的交付检查，本轮继续从解压后的运行包做新上下文测试，没有重复添加安装流程。
- [Cowork体验帖](https://www.reddit.com/r/ClaudeCowork/comments/1syex98/general_experience_trying_to_use_cowork_as_an/)：发帖者报告安装和实际定制流程脱节、仍反复使用原始简历。属个人体验，涉及第三方插件与宿主；帖中模型自评分不能当独立测评，更不能代表当前career-ops效果。用独立任务输出检验是否真的按岗位制作材料。

## 本轮改动

1. 结果默认精简为少量可行动选择：结论、理由、缺口、下一步。硬性门槛仍优先。
2. 明确交付岗位定制正文及改动说明，复用事实；没有数字就不编数字，没有格式工具先交付文本。
3. 核对附件实际内容及用途；同公司不同岗位分开，投递版本不被新稿覆盖。PDF检查可视效果和文字层。
4. 按搜索工具处理语法；异常结果做一次有依据的诊断，不把工具失败解释为没有岗位。

方法由本项目独立实现，未复制竞品代码或长段提示词。get-job.skill的CC-BY-NC-ND许可证不用于派生商业分发。不采用未经证实的时间节省/录用率数字，不新增全面试系统、外联、付费服务或数据采集。

运行时仍为14个文件，无新增依赖。竞品研究和测试记录留在仓库，不加入用户每次执行必读内容。具体测试与边界见[TESTING.md](../TESTING.md)。
