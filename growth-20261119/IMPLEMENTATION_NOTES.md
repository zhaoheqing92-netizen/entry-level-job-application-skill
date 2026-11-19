# 初级岗位求职助手 · 2026-11-19 本地候选版

## 版本说明（供发布时使用）

第一次试用时，准备一条雇主官网的岗位链接，再用两句话写自己的毕业届别、专业和一项经历。把 README 开头的指令发给已加载技能的 Agent，它会核对实际工作地和硬性资格，引用岗位原文，告诉你值得继续、还有哪项要问，或为什么可以跳过。读不到官网时，可以贴出职位说明。手上还没有目标岗位的人，可以继续按城市和方向找新岗。

双语首页把免费完整包和第一条指令放到了付款说明前。新增的离线虚构示例展示了同一位求职者为什么保留 Alpha 的助理测试岗、排除 Beta 的热管理研发岗。免费与一次性 ¥19.9 支持档的功能相同，模型费用另计。[中文首页](../README.md) · [English](../README.en.md) · [示例文字版](../docs/job-check-comparison.md)

本地保存的在售包中，教程在简历栏留空时会向用户要简历，默认的草稿话术还会授权上传。候选版允许先凭两句事实核岗，准备申请时默认只在本地出稿。官网填写、上传指定附件和最终提交分别选择。“先看这里”增加了一句加载确认指令，可以请 Agent 报出它实际读到的 `SKILL.md` 路径。

候选 ZIP 和原包都含 24 个文件，内容有变化的只有 `guide.html` 和 `先看这里.txt`。本版的一页 PDF 沿用旧稿，安装时可参考，选择授权请看 HTML。对照图和双语说明在仓库中查看。[本地候选包](../downloads/entry-level-job-application-with-guide-candidate-20261119.zip)

## 执行与验收

### 逐文件改动

以下路径相对于项目根目录。

| 文件 | 改动与原因 |
|---|---|
| `README.md` | 先说明谁能用、能得到什么，再给免费包和第一轮核岗原话。把对照图放在付款码前，兼容宿主和费用跟下载入口走，同版权益跟付款入口走。保留找新岗的例句，并提示使用旧包时怎样限定本地草稿。 |
| `README.en.md` | 同步首用与支持区的次序，给出英文指令、可展开的中文原话和英文示例解读，明确交互教程为中文。 |
| `docs/job-check-comparison.html` | 静态图的可编辑源文件。左栏引用 Alpha 的工作职责并摘录已有自我介绍，右栏引用 Beta 的毕业时间与学历要求。 |
| `docs/job-check-comparison.png` | 将双栏结果导出为 1080 × 1920 PNG，右上角标明“离线虚构示例”，供手机查看和两份 README 引用。 |
| `docs/job-check-comparison.md` | 对照图的纯文字版，可单独阅读或复用于 SkillPay。两个出处分别指向场景输入和留档输出。 |
| `.gitignore` | 为这张公开示例图添加精确例外，防止现有的 `*.png` 规则导致后续交付漏图。 |
| `docs/starter-kit/guide.html` | 默认预览第一轮核岗指令，发现新岗保留为第二选项。申请预览直接取选中标签的文字，只有选择上传且指定文件时才给出文件授权。同步安装确认句和 HTML 打印段。 |
| `docs/starter-kit/README.md` | 更新教程的核岗与申请选项，并给打开旧包或旧 PDF 的读者可用的本地草稿指令和 HTML 入口。 |
| `tools/test_guide.cjs` | 增加空简历、本地草稿和明确上传三类回归断言，替换原先把“最终提交”当成同时授权填、传、提的预期。覆盖四个动作之间的切换和漏填文件名。 |
| `docs/customer-start.txt` | 对应包根的“先看这里.txt”。说明解压层级，增加报告实际加载位置、无简历核岗、仅本地出稿三句，保留找新岗的次入口，并标注 PDF 中的旧授权说明。 |
| `downloads/entry-level-job-application-with-guide-candidate-20261119.zip` | 按原打包清单生成独立候选文件，用来核对实际交付内容。 |
| `growth-20261119/IMPLEMENTATION_NOTES.md` | 保存本页版本说明、变更依据、复测方法和候选包指纹，供作者以后核对领取端文件。 |

### 首用、授权和包内入口的验收依据

- **读者能否上手。** 按 `anti-defensive-writing` 把会改变选择的条件放到对应入口，保留同版权益、费用和证据说明。用 `humanizer-zh` 轻校中文时逐句保留授权动词、条件和原文引语。两份 README 均保留第一轮核岗原话；英文页给了可直接发送的译文。
- **触发说明。** 按 `skill-quality-reviewer` 对照技能标识、首次加载说明和实际任务入口。`SKILL.md` 允许先用学历与经历核岗；两句个人事实和一个官网链接即可发出第一条指令。包内加载确认要求 Agent 报出它能读取的实际技能文件。
- **话术与授权一致。** 对照教程控件标签、预览和复制文本检查四个动作。即使已在附件栏填写文件名，回到本地草稿也不能让该文件进入授权。包内 `prompts/02-authorized-apply.txt` 是单独的、显式同时授权填写、上传和提交的模板；默认草稿不调用它。
- **包内入口。** 根据 `skill-quality-reviewer` 的资源引用检查，从实际生成的 ZIP 读取根部入口和引用。检查客户版的安装按钮、相对文件与页内目标，并逐字节比对技能正文、脚本和参考资料。

### 本地复测结果

Windows，Python 3.12.10，Node.js 24.21.0，Playwright 1.62.1，Chrome 157.0.8103.79。以下从项目根目录执行；浏览器使用独立的无头会话。

| 检查对象 | 实测结果 |
|---|---|
| Python 单元及交付测试 | **40/40**。含状态恢复、提交前检查、离线演示和打包。 |
| 仓库教程、从候选包解压的教程 | 两者分别通过 **1/1 套、27/27 次断言**，每套另检查 5 个配置链接。含 320、768、1440 像素宽度下的三个页签、键盘、复制与回退、外部请求及脚本错误检查。 |
| 候选包安装入口 | 额外 **2/2**。点击“查看安装方法”能切换到安装页签，确认话术能要求报出实际加载路径。 |
| 双语 README | 中文 21/21、英文 14/14 个本地引用存在。原链接及每个目标的出现次数全部保留；含外链计数从 20、13 变为 22、15，每页只新增图及文字版。两页均核对了原句和“免费包 → 指令 → 结果图 → 支付码”的次序。 |
| 对照图 | 3/3 段引文逐字对应指定输入或输出，图源与文字版一致，2/2 个来源链接可读。320、360 像素视口下的双栏布局检查 6/6；PNG 可解码，缩到手机宽度读图可辨，无裁切。 |
| 候选 ZIP | 成员 24/24 与打包清单一致；CRC 通过，无重名、无嵌套 ZIP。13/13 个技能运行文件与源码逐字节一致，包内教程的本地文件引用、页内目标及技能正文的 17 处相对引用均可定位。 |

**测试与打包命令**（PowerShell）

```powershell
python -B -m unittest discover -s tests -v
$pw = "$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright"
$chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
node tools/test_guide.cjs $pw $chrome

$candidate = 'downloads/entry-level-job-application-with-guide-candidate-20261119.zip'
$sale = 'downloads/entry-level-job-application-with-guide.zip'
python -B tools/package_skill.py --with-guide --output $candidate
python -B -m zipfile -t $candidate
python -B -m zipfile -l $candidate
Get-FileHash -Algorithm SHA256 -LiteralPath $candidate,$sale,'docs/starter-kit/guide.pdf'
```

打包命令只在目标文件尚不存在时执行，复核现有包从 `zipfile -t` 开始。解压后再跑同一套浏览器测试的命令如下，临时目录随测试清理。

```powershell
@'
from pathlib import Path
from shutil import copy2
from subprocess import run
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import sys
candidate, pw, chrome = sys.argv[1:]
with TemporaryDirectory() as folder:
    root = Path(folder)
    with ZipFile(candidate) as archive:
        archive.extractall(root/'docs/starter-kit')
    (root/'tools').mkdir()
    test = root/'tools/test_guide.cjs'
    copy2('tools/test_guide.cjs', test)
    run(['node', str(test), pw, chrome], check=True)
'@ | python -B - $candidate $pw $chrome
```


<details>
<summary>补充验收命令：重查两个 README、引文、图片、ZIP 引用和安装入口</summary>

沿用上面的 PowerShell 变量。本次使用本机已有的 Pillow 和 pypdf 检查图片和 PDF。

```powershell
$OutputEncoding = [Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
@'
from pathlib import Path
from zipfile import ZipFile
from html.parser import HTMLParser
from urllib.parse import urlsplit
from tempfile import TemporaryDirectory
from PIL import Image
from pypdf import PdfReader
from subprocess import run
import re, sys
sys.path.insert(0, 'tools')
import package_skill as builder

candidate, original, pw, chrome = sys.argv[1:]
read = lambda p: Path(p).read_text(encoding='utf-8')
prompt = next(line for line in read('growth-20261119/DISCUSSION.md').splitlines() if line.startswith('> '))
for name in ('README.md','README.en.md'):
    text = read(name)
    links = [a or b for a,b in re.findall(r'\]\(([^)]+)\)|<img [^>]*src="([^"]+)"', text)]
    local = [path for path in links if not urlsplit(path).scheme]
    assert all(Path(path).exists() for path in local)
    order = [original, prompt, 'docs/job-check-comparison.png', 'docs/skillpay-purchase-qr.png']
    assert [text.index(item) for item in order] == sorted(text.index(item) for item in order)
    print(name, len(local), 'local links;', len(links), 'total')
base = Path('docs/job-check-comparison')
source, alt = (read(base.with_suffix(ext)) for ext in ('.html', '.md'))
quotes = re.findall(r'<blockquote>“([^”]+)”</blockquote>', source)
job, result = read('tests/scenarios/quick-search.md'), read('evaluation/forward-test.md')
assert len(quotes) == 3 and quotes[0] in job and quotes[1] in result and quotes[2] in job
assert all(q in alt for q in quotes)
sources = re.findall(r'\]\(([^)]+)\)', alt)
assert len(sources) == 2 and all((base.parent/s).is_file() for s in sources)
with Image.open(base.with_suffix('.png')) as image:
    assert image.size == (1080,1920)
    image.verify()
assert len(PdfReader('docs/starter-kit/guide.pdf').pages) == 1

class Targets(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href','src') and value:
                links.add(value)
            if key == 'id':
                ids.add(value)

with TemporaryDirectory() as folder, ZipFile(candidate) as z, ZipFile(original) as old:
    names = z.namelist()
    assert sorted(names) == sorted(builder.FILES + ['LICENSE'] + builder.GUIDE_FILES + ['先看这里.txt']) == sorted(old.namelist())
    assert not any(n.lower().endswith('.zip') for n in names) and z.testzip() is None
    changed = [n for n in names if z.read(n) != old.read(n)]
    assert set(changed) == {'guide.html','先看这里.txt'}
    assert all(z.read(n) == (builder.SKILL/n).read_bytes() for n in builder.FILES)
    assert z.read('先看这里.txt') == Path('docs/customer-start.txt').read_bytes()
    links, ids = set(), set()
    Targets().feed(z.read('guide.html').decode('utf-8'))
    for target in map(urlsplit, links):
        if not target.scheme:
            assert not target.path or target.path in names
            assert not target.fragment or target.fragment in ids
    refs = [urlsplit(m) for m in re.findall(r'\]\(([^)]+)\)', z.read('SKILL.md').decode('utf-8'))]
    for target in (r for r in refs if not r.scheme):
        assert target.path in names
        if target.fragment:
            headings = re.findall(r'^#+ (.+)$', z.read(target.path).decode('utf-8'), re.M)
            assert target.fragment in {re.sub(r'[^\w -]', '', h.lower().strip()).replace(' ', '-') for h in headings}
    print(len(names), 'ZIP members;', len([r for r in refs if not r.scheme]), 'relative skill links;', changed)
    z.extractall(folder)
    run(['node','-',pw,chrome,base.with_suffix('.html').resolve().as_uri(),(Path(folder)/'guide.html').as_uri()], input="""
const assert = require('node:assert/strict');
const {chromium} = require(process.argv[2]);
(async () => {
  const browser = await chromium.launch({executablePath:process.argv[3]});
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[4]);
    for (const width of [320,360]) {
      await page.setViewportSize({width,height:900});
      const [a,b] = await page.locator('.jobs section').evaluateAll(nodes => nodes.map(n => n.getBoundingClientRect().toJSON()));
      assert.equal(a.right,b.left);
      assert.equal(a.width+b.width,width);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth),width);
    }
    await page.goto(process.argv[5]);
    await page.getByRole('link',{name:'查看安装方法'}).click();
    assert.equal(await page.getByRole('tab',{name:/安装技能/}).getAttribute('aria-selected'),'true');
    assert.match(await page.locator('#install-prompt').textContent(),/实际加载的 SKILL.md 路径/);
    console.log('6 layout checks and 2 package-entry checks passed.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode=1; });
""", encoding='utf-8', check=True)
'@ | python -B - $candidate $sale $pw $chrome
```

</details>

### 候选包指纹与根目录

候选包 **364,645 字节**。此 SHA-256 标识本次落盘文件；重新构建时包内时间戳可能改变。

| 文件 | SHA-256 |
|---|---|
| 候选包 | `4e3755085c464f3a172ec2986b76b98502dacafb71b1f86768e8ab5f2cddbb73` |
| 本地在售包 `entry-level-job-application-with-guide.zip`（开工前与验包后相同） | `34ca8520cc080c7d3e817beb8b55d4e20871b9f927a35883accf9843b3833e23` |

根部 5 个文件和 6 个目录如下，解压一层即可读取技能。

```text
SKILL.md
guide.html
先看这里.txt
guide.pdf
LICENSE
agents/
assets/
examples/
prompts/
references/
scripts/
```

### 偏离、待办与使用边界

- 按任务书原范围完成。为落实已批准的首用顺序，同步了教程初始页面及其 README；为保留可交付配图，补了一个精确忽略规则例外。打包脚本与清单沿用原版，对照图随仓库提供。
- **一页 PDF 待人工同步。** 用 `pypdf` 读取现有一页，确认它仍写着“根据我的简历”和“只填草稿／允许提交”。仓内有 HTML 打印样式，没有 PDF 再生脚本。已同步 HTML 打印内容，保留 PDF 原字节；其 SHA-256 为 `baeb9abf99067fbaecce973b7031bd2445f069e2557f7334fefef3ececbe25cb`。
- 没有新增待裁决事项。本轮只做本地文件与离线验收，未提交、推送、调整仓库设置或更换在售包。未登录账号、访问 SkillPay 或真实投递。公开下载仍指向原包，线上实际领取版本未核实。

