import puppeteer from 'puppeteer-core';
import { startCareer } from '../lib/start.mjs';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';

const exe = [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
].find((p) => existsSync(p));

const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto('http://127.0.0.1:8123/', { waitUntil: 'networkidle0' });
await startCareer(page);

await page.evaluate(() => {
  const key = Object.keys(localStorage).find((k) => k.startsWith('lpl-career'));
  const env = JSON.parse(localStorage.getItem(key));
  env.state.year = 3;
  env.state.week = 30;
  env.state.signed = true;
  env.state.freeAgent = false;
  env.state.honors = [
    { id: 'lpl-champion', year: 1 },
    { id: 'rookie-of-year', year: 1 },
    { id: 'season-mvp', year: 2 },
    { id: 'all-pro', year: 2 },
    { id: 'lpl-champion', year: 2 },
    { id: 'worlds-champion', year: 3 },
    { id: 'hall-of-fame', year: 3 },
  ];
  localStorage.setItem(key, JSON.stringify(env));
});

await page.reload({ waitUntil: 'networkidle0' });
await page.click('[data-tab="career"]');
await new Promise((r) => setTimeout(r, 300));

mkdirSync('shots', { recursive: true });
await page.screenshot({ path: 'shots/honors.png', fullPage: true });

const panel = await page.evaluate(() => {
  const panels = [...document.querySelectorAll('.panel')];
  return panels[panels.length - 1]?.outerHTML ?? '';
});
writeFileSync(
  'shots/honors-panel.html',
  `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>荣誉柜</title><body style="margin:0;background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif">${panel}</body></html>`,
);
console.log('saved shots/honors.png and shots/honors-panel.html');
await browser.close();
