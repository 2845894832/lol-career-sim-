import puppeteer from 'puppeteer-core';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new', args: ['--no-sandbox'] });
const p = await b.newPage();
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
await p.goto('file:///D:/deepseek-harness/default-workspace/vibe-game-producer/dist/index.html', { waitUntil: 'networkidle0' });
await p.evaluate(() => localStorage.clear());
await p.reload({ waitUntil: 'networkidle0' });

const fill = async () => {
  for (let i = 0; i < 3; i++) {
    const slots = await p.$$('.slot');
    const v = await slots[i].$eval('.v', (el) => el.textContent.trim());
    if (v !== '空') continue;
    await slots[i].click();
    const rest = await p.$('.sheet [data-act="pick-action"][data-id="rest"]');
    if (rest) await rest.click();
    await new Promise((r) => setTimeout(r, 60));
  }
};

for (let week = 1; week <= 8; week++) {
  await fill();
  const fin = await p.$('[data-act="end-week"]:not([disabled])');
  if (!fin) { console.log('no end-week at', week); break; }
  await fin.click();
  await new Promise((r) => setTimeout(r, 200));
  const cont = await p.$('[data-act="continue"]');
  if (cont) { await cont.click(); await new Promise((r) => setTimeout(r, 150)); }
  if (await p.$('[data-act="choose"]')) {
    const sheet = await p.$('.overlay .sheet');
    await sheet.screenshot({ path: 'shots/event-sheet.png' });
    console.log('event captured at week', week);
    break;
  }
}
await b.close();
