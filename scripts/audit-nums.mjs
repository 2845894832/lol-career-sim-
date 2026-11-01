import puppeteer from 'puppeteer-core';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await p.goto('file:///D:/deepseek-harness/default-workspace/vibe-game-producer/dist/index.html', { waitUntil: 'networkidle0' });
await p.evaluate(() => localStorage.clear());
await p.reload({ waitUntil: 'networkidle0' });

// 把三格排满，让日志、结算、胜率列都出现
for (const i of [0, 1, 2]) {
  const slots = await p.$$('.slot');
  await slots[i].click();
  await p.waitForSelector('.btn[data-act="pick-action"]:not([disabled])');
  const opts = await p.$$('.btn[data-act="pick-action"]:not([disabled])');
  await opts[0].click();
  await new Promise((r) => setTimeout(r, 80));
}

const res = await p.evaluate(() => {
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && /\d/.test(n.textContent));
    if (!own) continue;
    const cs = getComputedStyle(el);
    out.push({
      tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
      text: el.textContent.trim().slice(0, 28),
      fvn: cs.fontVariantNumeric,
      align: cs.textAlign,
      font: cs.fontFamily.split(',')[0].replace(/["']/g, ''),
    });
  }
  return out;
});
console.log(JSON.stringify(res, null, 1));
await b.close();
