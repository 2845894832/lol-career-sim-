import puppeteer from 'puppeteer-core';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto('http://127.0.0.1:8123/', { waitUntil: 'networkidle0' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle0' });
await page.click('[data-act="role"][data-role="MID"]');
await page.type('#nameInput', '阿呆');
await new Promise((r) => setTimeout(r, 150));
await page.screenshot({ path: 'shots/starter.png', fullPage: true });
console.log('saved shots/starter.png');
await browser.close();
