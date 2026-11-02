import puppeteer from 'puppeteer-core';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.goto('http://127.0.0.1:8124/', { waitUntil: 'networkidle0' });
// 直接用一段已知文本看排版：把 p 的文本改成无空格版本
const txt = await p.evaluate(() => {
  const el = document.querySelector('.ending p');
  return el ? JSON.stringify(el.textContent) : null;
});
const css = await p.evaluate(() => {
  const el = document.querySelector('.ending p');
  return el ? getComputedStyle(el).textAlign + ' / ' + getComputedStyle(el).wordSpacing : null;
});
console.log(txt, css);
await b.close();
