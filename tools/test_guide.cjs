// Optional developer check; the tutorial itself has no runtime dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.argv[2] || 'playwright');
const root = path.resolve(__dirname, '../docs/starter-kit');
(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.argv[3] ? { executablePath: process.argv[3] } : {})
  });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route(/^https?:/, route => {
      errors.push('Unexpected network request: ' + route.request().url());
      return route.abort();
    });
    await page.goto(pathToFileURL(path.join(root, 'guide.html')).href);
    const search = page.locator('#search-prompt');
    const prompt = page.locator('#apply-prompt');
    const help = page.locator('#apply-help');
    const files = page.locator('#allow-files');
    assert.doesNotMatch(await prompt.textContent(), /上传|回执/);
    assert.doesNotMatch(await help.textContent(), /回执/);
    assert.equal(await files.isDisabled(), true);
    assert.equal(await search.textContent(), '使用 entry-level-job-application。这个官网岗位是【链接】。我【毕业届别、专业】，做过【一项相关经历】。请核对实际工作地和硬性资格，引用一条岗位原文，告诉我该继续、先问哪一项，还是跳过。只核岗位，不注册、不上传、不提交。官网读不到时告诉我，我可以贴出职位说明。');
    await page.locator('#search-mode').selectOption('find');
    await page.locator('#role').fill('初级测试工程师');
    await page.locator('#cities').fill('示例城市');
    assert.match(await page.locator('#search-prompt').textContent(), /示例城市的初级测试工程师/);
    assert.match(await page.locator('#search-prompt').textContent(), /不注册、不上传、不提交/);
    assert.doesNotMatch(await search.textContent(), /简历/);
    await page.locator('#search .extra summary').click();
    await page.locator('#attachments').fill('D:/private/attachments');
    assert.match(await search.textContent(), /附件目录：D:\/private\/attachments/);
    await page.locator('#search-mode').selectOption('check');
    assert.doesNotMatch(await search.textContent(), /附件目录|D:\/private\/attachments/);
    await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', {
      configurable: true, value: { writeText: async text => { window.testCopy = text; } }
    }));
    await page.locator('[data-copy="search-prompt"]').click();
    assert.equal(await page.evaluate(() => window.testCopy), await page.locator('#search-prompt').textContent());
    await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', { configurable: true, value: undefined }));
    await page.locator('[data-copy="search-prompt"]').click();
    assert.equal(await page.evaluate(() => getSelection().toString()), await page.locator('#search-prompt').textContent());
    await page.locator('#tab-search').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tab-apply').getAttribute('aria-selected'), 'true');
    assert.equal(await page.locator('[value="draft"]').isChecked(), true);
    assert.match(await page.locator('#apply-prompt').textContent(), /不提交/);
    await page.locator('#scope').fill('示例公司 / 初级工程师');
    await page.getByText('在官网填写草稿', { exact: true }).click();
    assert.equal(await files.isDisabled(), true);
    assert.doesNotMatch(await help.textContent(), /回执/);
    assert.match(await prompt.textContent(), /本次只授权：在官网填写草稿。[\s\S]*不添加附件，不提交/);
    await page.getByText('上传指定附件', { exact: true }).click();
    assert.doesNotMatch(await help.textContent(), /回执/);
    assert.match(await prompt.textContent(), /等我给出具体文件后再操作/);
    await files.fill('中文简历.pdf');
    assert.match(await prompt.textContent(), /本次只授权：上传指定附件。[\s\S]*指定文件：中文简历\.pdf。[\s\S]*保留表单现有字段，不提交/);
    await page.getByText('仅在本地写草稿', { exact: true }).click();
    assert.equal(await files.isDisabled(), true);
    assert.equal(await files.inputValue(), '');
    assert.doesNotMatch(await help.textContent(), /回执/);
    assert.match(await prompt.textContent(), /本次只授权：仅在本地写草稿。[\s\S]*不访问招聘表单，不提交/);
    assert.doesNotMatch(await prompt.textContent(), /上传|中文简历\.pdf/);
    await page.locator('#apply .extra').evaluate(node => { node.open = true; });
    await page.locator('#limit').selectOption('3');
    await page.getByText('最终提交', { exact: true }).click();
    assert.equal(await files.isDisabled(), true);
    assert.match(await help.textContent(), /官网回执/);
    const apply = await prompt.textContent();
    assert.match(apply, /本次只授权：最终提交。[\s\S]*只提交我已确认且填妥的申请/);
    assert.match(apply, /最多 3 份/);
    assert.doesNotMatch(apply, /上传|中文简历\.pdf/);
    await page.locator('.tools').evaluate(node => { node.open = true; });
    for (const client of ['codex', 'claude', 'other']) {
      await page.locator('#config-client').selectOption(client);
      const links = await page.locator('#config-links a').evaluateAll(nodes => nodes.map(a => a.getAttribute('href')));
      for (const link of links) await fs.access(path.join(root, link));
    }
    for (const width of [320, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      for (const stage of ['install', 'search', 'apply']) {
        await page.locator('#tab-' + stage).click();
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      }
    }
    assert.deepEqual(errors, []);
    console.log('Guide checks passed: prompts, authorization, copy, links, keyboard, responsive, offline.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
