import puppeteer from 'puppeteer-core';
import { startCareer } from './lib/start.mjs';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const url = process.argv[2] ?? 'http://127.0.0.1:8124/';
const out = process.argv[3] ?? 'shots/slice-ending.png';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pickRest(p) {
  const ok = await p.evaluate(() => {
    const all = [...document.querySelectorAll('.sheet .btn.opt')].filter((b) => !b.disabled);
    const rest = all.find((b) => (b.querySelector('.opt-name')?.textContent ?? '').includes('休息'));
    const btn = rest ?? all[all.length - 1];
    if (!btn) return false;
    btn.click();
    return true;
  });
  if (!ok) throw new Error('选不到行动');
  await sleep(120);
}

async function dismiss(p) {
  for (let i = 0; i < 6; i++) {
    const kind = await p.evaluate(() => {
      const ov = document.querySelector('.overlay');
      if (!ov) return null;
      if (ov.querySelector('[data-act="continue"]')) return 'outcome';
      if (ov.querySelector('[data-act="choose"]')) return 'event';
      return 'other';
    });
    if (!kind) return;
    if (kind === 'outcome') await p.click('[data-act="continue"]');
    else if (kind === 'event') await p.click('.overlay [data-act="choose"]');
    else await p.click('.overlay [data-act="close-sheet"]');
    await sleep(160);
  }
}

const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await p.goto(url, { waitUntil: 'networkidle0' });
await startCareer(p);

for (let week = 1; week <= 12; week++) {
  if (await p.$('.ending')) break;
  const before = await p.$eval('.title', (el) => el.textContent).catch(() => '');
  for (let slot = 0; slot < 3; slot++) {
    await p.evaluate((n) => document.querySelectorAll('.slot')[n].click(), slot);
    await p.waitForSelector('.sheet .btn.opt', { timeout: 3000 });
    await pickRest(p);
  }
  await p.click('[data-act="end-week"]');
  await sleep(240);
  await dismiss(p);
  // 等周数变化或出结局
  for (let i = 0; i < 20; i++) {
    if (await p.$('.ending')) break;
    const now = await p.$eval('.title', (el) => el.textContent).catch(() => '');
    if (now && now !== before) break;
    await sleep(120);
  }
  await sleep(120);
}

const title = await p.$eval('.ending h2', (el) => el.textContent).catch(() => null);
console.log('ending:', title);
await p.screenshot({ path: out, fullPage: true });
console.log('saved', out);
await b.close();
