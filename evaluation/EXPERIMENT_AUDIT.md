# 评估证据审查

日期：2026-11-08。以下是独立新上下文 Agent 审查的整理版。请求模型为 gpt-6-astra（ultra），宿主未另行返回模型身份字段；同模型体系，结论为 provisional，不是第三方认证。原始调用记录保留在私有 .aris/traces/，不随技能发布。

总体结论：PASS（仅限本地软件评估）。本次为 fresh read-only reviewer 审查，review_independence: same-family，acceptance_status: provisional；不是产品认证。

已逐行读取全部指定文件，并独立运行：
- python -B -X utf8 -m unittest discover -s tests -v：39 项通过，退出码 0。
- python -B -X utf8 tools/demo.py：8 个申请包场景、4 个恢复检查全部通过，退出码 0。与保存的 JSON 相比，仅生成时间更新，业务结果一致。

A．参考答案来源：PASS。tests/test_check_application.py:17–31、tests/test_application_state.py:22–36 从虚构样例复制输入并改变字段。assets/application.example.json:2–31 使用 fictional-candidate-01、.example.test、synthetic: 引用。tools/demo.py:79–83 标为 simulation_only。没有冒充真实 ground truth。
B．评分归一化：PASS。check_application.py:13,57–69 权重 30/25/20/15/10，固定分母5。样例分量计算得 [61,77]，tests/test_check_application.py:34–40 有断言。evaluation/demo/demo.json:21–32 满分仍被硬条件拒绝。README 明确分数不是录用概率。
C．结果存在且数值匹配：PASS。TESTING.md:7–9 的39项、8+4场景和一个Agent案例均有文件，独立复跑一致。forward-test 的岗位筛选符合场景。全新上下文和3次读取的过程元数据在限定材料内只有文本记录，未独立认证。
D．未执行评估代码：PASS。tests/test_check_application.py:25–31 实际调用 check_packet；check_application.py:238–241 调用评分；tools/demo.py:22–26,64–82 调用检查与SQLite；tests/test_delivery.py:18–40 调用演示和打包。无未进入流程的结果计算。
E．范围表述：PASS。TESTING.md:3,8–9,15、README.md:37,54、README.en.md:45 明确本地模拟和未验证范围。JSON中的submitted是模拟状态，真实提交和支付为0。
F．类型：当前39项回归、离线演示、单Agent场景均为simulation_only。不是real_gt、human_eval或跨模型基准。

需要修正：无。支持的有限结论：39项本地测试通过、8+4项离线演示通过、一个离线Agent案例完成。
未复核十月历史集成、OCR或验证码；未访问网站、安装依赖、使用个人数据或修改源文件。
风险：来源字符串与声明的一致性检查不能证明真实来源、提交或支付。

公开整理说明：2026-11-08 移除了一个已单独归档的辅助规划文档引用及对应输入哈希，原始报告已在仓库外保留。本报告结论和其余哈希属于修改前快照，本次未重新审计；更新后的 README 和新增演示说明不在原审计范围内。
