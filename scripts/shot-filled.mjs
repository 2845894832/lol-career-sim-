import puppeteer from 'puppeteer-core';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const url = process.argv[2] ?? 'http://127.0.0.1:8123/';
const out = process.argv[3] ?? 'shots/rank-filled.png';

const browser = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto(url, { waitUntil: 'networkidle0' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle0' });

// 依次点三个空格，各选第一个能点的行动
for (const slot of [0, 1, 2]) {
  const slots = await page.$$('.slot');
  await slots[slot].click();
  await page.waitForSelector('.btn[data-act="pick-action"]:not([disabled])', { timeout: 3000 });
  const opts = await page.$$('.btn[data-act="pick-action"]:not([disabled])');
  await opts[0].click();
  await new Promise((r) => setTimeout(r, 120));
}
await page.screenshot({ path: out });
console.log('saved', out);
await browser.close();
