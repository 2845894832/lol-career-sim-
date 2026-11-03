import puppeteer from 'puppeteer-core';
import { startCareer } from './lib/start.mjs';
import { existsSync } from 'node:fs';

const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find((p) => existsSync(p));
const url = process.argv[2] ?? 'http://127.0.0.1:8123/';
const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto(url, { waitUntil: 'networkidle0' });
await startCareer(page);
// 造一条荣誉，确认渲染
await page.evaluate(() => {
  const raw = localStorage.getItem(Object.keys(localStorage).find((k) => k.startsWith('lpl-career')));
  const env = JSON.parse(raw);
  env.state.honors = [
    { id: 'lpl-champion', year: 1 },
    { id: 'rookie-of-year', year: 1 },
    { id: 'season-mvp', year: 2 },
  ];
  localStorage.setItem(Object.keys(localStorage).find((k) => k.startsWith('lpl-career')), JSON.stringify(env));
});
await page.reload({ waitUntil: 'networkidle0' });
await page.click('[data-tab="career"]');
await new Promise((r) => setTimeout(r, 250));
await page.screenshot({ path: 'shots/career.png', fullPage: true });
console.log('saved shots/career.png');
await browser.close();
