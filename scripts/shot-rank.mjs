import puppeteer from 'puppeteer-core';
import { existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const candidates = [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
];
const exe = candidates.find((p) => existsSync(p));
const browser = await puppeteer.launch({ executablePath: exe, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto('file://' + resolve('dist/index.html'), { waitUntil: 'load' });
await new Promise((r) => setTimeout(r, 300));
mkdirSync('shots', { recursive: true });
await page.screenshot({ path: 'shots/rank-code.png', fullPage: false });
const meta = await page.$eval('.meta', (el) => el.textContent?.trim());
console.log(meta);
await browser.close();
