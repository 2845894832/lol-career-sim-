import puppeteer from 'puppeteer-core';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const url = process.argv[2] ?? 'http://127.0.0.1:8124/';
const out = process.argv[3] ?? 'shots/slice-ending.png';

const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await p.goto(url, { waitUntil: 'networkidle0' });
await p.evaluate(() => localStorage.clear());
await p.reload({ waitUntil: 'networkidle0' });

const plan = ['rank', 'review', 'rest'];
for (let week = 1; week <= 12; week++) {
  if (await p.$('.ending')) break;
  for (let slot = 0; slot < 3; slot++) {
    const slots = await p.$$('.slot');
    await slots[slot].click();
    await p.waitForSelector('.sheet', { timeout: 3000 });
    const btn = await p.$(`.sheet [data-id="${plan[slot]}"]`);
    if (!btn) throw new Error(`第 ${week} 周第 ${slot + 1} 格找不到 ${plan[slot]}`);
    await btn.click();
    await new Promise((r) => setTimeout(r, 60));
  }
  // 结周（可能先有事件）
  const endBtn = await p.$('[data-act="end-week"]');
  await endBtn.click();
  await new Promise((r) => setTimeout(r, 150));
  // 事件选项
  for (let guard = 0; guard < 4; guard++) {
    const opt = await p.$('.sheet [data-act="choose"]');
    if (!opt) break;
    await opt.click();
    await new Promise((r) => setTimeout(r, 150));
  }
  // 结算浮层「继续」
  for (let guard = 0; guard < 3; guard++) {
    const cont = await p.$('[data-act="continue"]');
    if (!cont) break;
    await cont.click();
    await new Promise((r) => setTimeout(r, 150));
  }
  await new Promise((r) => setTimeout(r, 100));
}

const title = await p.$eval('.ending h2', (el) => el.textContent).catch(() => null);
const bodyText = await p.$eval('.ending p', (el) => JSON.stringify(el.textContent)).catch(() => null);
console.log('ending:', title);
console.log('body:', bodyText);
await p.screenshot({ path: out, fullPage: true });
console.log('saved', out);
await b.close();
