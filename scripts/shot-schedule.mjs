import puppeteer from 'puppeteer-core';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await page.goto('http://127.0.0.1:8123/?dev=signed', { waitUntil: 'networkidle0' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle0' });
await page.click('[data-act="tab"][data-tab="schedule"]');
await new Promise((r) => setTimeout(r, 200));
await page.screenshot({ path: 'shots/schedule-screen.png' });
console.log('saved shots/schedule-screen.png');
await browser.close();
