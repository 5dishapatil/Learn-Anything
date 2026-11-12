// Usage: node shoot.mjs <outDir> <url1|name1> <url2|name2> ...
import { chromium } from 'playwright-core';
import fs from 'node:fs';
const [, , outDir, ...targets] = process.argv;
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const width = Number(process.env.W || 1440), height = Number(process.env.H || 900);
const page = await browser.newPage({ viewport: { width, height } });
page.on('console', (m) => { if (m.type() === 'error') console.log('[console.error]', m.text().slice(0, 300)); });
page.on('pageerror', (e) => console.log('[pageerror]', e.message.slice(0, 300)));
for (const t of targets) {
  const [url, name, clickText] = t.split('|');
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch((e) => console.log('goto', e.message));
  if (clickText) {
    for (const ct of clickText.split('>')) {
      await page.getByText(ct, { exact: false }).first().click({ timeout: 8000 }).catch((e) => console.log('click fail', ct));
      await page.waitForTimeout(1500);
    }
  }
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${outDir}/${name}.png`, fullPage: process.env.FULL === '1' });
  console.log('shot', name);
}
await browser.close();
