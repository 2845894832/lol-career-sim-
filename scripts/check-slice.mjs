import puppeteer from 'puppeteer-core';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
const errs = [];
p.on('pageerror', (e) => errs.push(e.message));
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await p.goto('http://127.0.0.1:8124/', { waitUntil: 'networkidle0' });
await p.evaluate(() => localStorage.clear());
await p.reload({ waitUntil: 'networkidle0' });
console.log('slots:', (await p.$$('.slot')).length);
const slots = await p.$$('.slot');
await slots[0].click();
await new Promise((r) => setTimeout(r, 300));
const info = await p.evaluate(() => ({
  sheet: !!document.querySelector('.sheet'),
  overlay: !!document.querySelector('.overlay'),
  opts: document.querySelectorAll('[data-act="pick-action"]').length,
  bodyLen: document.body.innerText.length,
}));
console.log(info, 'errs:', errs);
await b.close();
