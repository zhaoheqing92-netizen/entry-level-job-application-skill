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
    await page.locator('#role').fill('初级测试工程师');
    await page.locator('#cities').fill('示例城市');
    assert.match(await page.locator('#search-prompt').textContent(), /示例城市的初级测试工程师/);
    assert.match(await page.locator('#search-prompt').textContent(), /不注册、不上传、不提交/);
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
    await page.locator('#apply .extra').evaluate(node => { node.open = true; });
    await page.locator('#allow-files').fill('中文简历');
    await page.locator('#limit').selectOption('3');
    await page.locator('[value="submit"]').check();
    const apply = await page.locator('#apply-prompt').textContent();
    assert.match(apply, /我授权在上述范围内填写、上传并提交/);
    assert.match(apply, /最多 3 份/);
    assert.match(apply, /允许上传：中文简历/);
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
