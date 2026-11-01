import puppeteer from 'puppeteer-core';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
const errs = [];
p.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
p.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
await p.goto('file:///D:/deepseek-harness/default-workspace/vibe-game-producer/teach/lessons/0006-%E5%8A%A8%E6%95%88%E4%B8%8E%E5%9B%9E%E6%89%A7.html', { waitUntil: 'networkidle0' });
const info = await p.evaluate(() => ({
  len: document.body.innerText.trim().length,
  head: document.body.innerText.trim().slice(0, 60),
  h1: document.querySelector('h1')?.textContent ?? null,
  sheetDisplay: getComputedStyle(document.querySelector('.sheet')).display,
  sheetHeight: document.querySelector('.sheet').getBoundingClientRect().height,
}));
console.log(JSON.stringify({ info, errs }, null, 1));
await b.close();
