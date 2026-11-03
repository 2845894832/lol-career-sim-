import puppeteer from 'puppeteer-core';
import { startCareer } from './lib/start.mjs';
import { existsSync } from 'node:fs';

const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find((p) => existsSync(p));
const url = process.argv[2] ?? 'http://127.0.0.1:8123/';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pick(page, label) {
  const ok = await page.evaluate((want) => {
    const btn = [...document.querySelectorAll('.sheet .btn.opt')].find(
      (b) => !b.disabled && b.querySelector('.opt-name')?.textContent?.trim() === want,
    );
    if (!btn) return false;
    btn.click();
    return true;
  }, label);
  if (!ok) throw new Error(`点不到行动 ${label}`);
  await sleep(140);
}

/** 关掉所有浮层：结果页点「继续」，事件选第一个选项。 */
async function dismiss(page) {
  for (let i = 0; i < 6; i++) {
    const kind = await page.evaluate(() => {
      const ov = document.querySelector('.overlay');
      if (!ov) return null;
      if (ov.querySelector('[data-act="continue"]')) return 'outcome';
      if (ov.querySelector('[data-act="choose"]')) return 'event';
      return 'other';
    });
    if (!kind) return;
    if (kind === 'outcome') await page.click('[data-act="continue"]');
    else if (kind === 'event') await page.click('.overlay [data-act="choose"]');
    else await page.click('.overlay [data-act="close-sheet"]');
    await sleep(180);
  }
}

const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto(url, { waitUntil: 'networkidle0' });
await startCareer(page);

for (let w = 0; w < 3; w++) {
  for (const [i, label] of ['直播', '直播', '休息'].entries()) {
    await page.evaluate((n) => document.querySelectorAll('.slot')[n].click(), i);
    await page.waitForSelector('.sheet [data-act="pick-action"]', { timeout: 3000 });
    await pick(page, label);
  }
  await page.click('[data-act="end-week"]');
  await sleep(220);
  await dismiss(page);
  await sleep(150);
}

await page.click('[data-tab="money"]');
await sleep(250);
await page.screenshot({ path: 'shots/money.png', fullPage: true });
console.log('saved shots/money.png');
await browser.close();
