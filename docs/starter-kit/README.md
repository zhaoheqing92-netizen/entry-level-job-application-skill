# 交互式上手教程

![教程预览](preview.png)

**装好技能后，直接告诉 Agent 你的求职需求就能用，不需要先填这个网页。**

[下载客户完整包（技能＋教程）](../../downloads/entry-level-job-application-with-guide-candidate-20261119.zip)。解压后先看 `先看这里.txt`，里面有中文使用说明和 `guide.html`。

`guide.html` 只是可选教程：教你安装、帮你写需求，再把文字复制给 Agent。页面自己不会搜索、读取简历或投递。第一次用可以看看，会用就跳过。

用 Edge 或 Chrome 打开本目录的 [guide.html](guide.html) 即可使用下列选项。GitHub 的文件预览页只显示源码。旧的单独技能 ZIP 不带教程。旧版教程的选项可能较少。要写本地草稿时请直接告诉 Agent：“仅在本地写草稿，不访问招聘表单，不提交。”平台交付版本以实际领取的文件为准。

- **安装技能**：按客户端查看目录，下载同目录的技能安装 ZIP。
- **核岗位**：粘贴一条官网岗位链接，在消息里补上届别、专业和一项经历。想找新机会时选“发现新岗位”，再填岗位和城市。
- **去申请**：默认“仅在本地写草稿”。要操作官网时，单独选“在官网填写草稿”“上传指定附件”或“核对已填申请”，写清岗位范围，选上传时再写明文件。准备好后由你本人提交。若要 Agent 代交，请在核对这份最终申请时明确确认一次；教程里提前勾选的选项和旧代投偏好都不能授权这次提交。

缺工具时展开页面底部说明；已有工具够用就跳过安装。[配置示例](examples/README.md) 要合并，不能覆盖原设置。

页面离线可用，不上传、不保存个人资料，不执行实际投递。字体使用本机 Noto Sans SC 或系统中文字体，不同系统外观可能略有差异。

[一页速查 PDF（安装、核岗示例和四种申请准备选项）](guide.pdf) · [技能安装包](entry-level-job-application.zip)

## 开发检查

页面只有 HTML、CSS 和原生 JavaScript，没有构建步骤和运行依赖。开发者若已有 Playwright，可在仓库根目录运行：

```text
node tools/test_guide.cjs
```

也可以传入已安装 Playwright 的模块路径和 Chrome 可执行文件路径：

```text
node tools/test_guide.cjs "<Playwright 模块路径>" "<Chrome 可执行文件路径>"
```

测试使用虚构输入，检查动态话术、四种申请授权、剪贴板回退、配置链接、键盘导航和窄屏布局，不安装依赖或访问招聘网站。教程用户不需要运行它。

维护者重新打包（使用已安装的 Python，客户不用运行）：

```text
python tools/package_skill.py --with-guide --output dist/entry-level-job-application-with-guide.zip
```

生成的客户包在根目录放置 `SKILL.md`、`先看这里.txt` 和 `guide.html`，不需要再解压第二个安装包。为避免覆盖旧交付文件，输出路径必须尚不存在。
