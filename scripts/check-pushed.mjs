// 检查「推到 GitHub 的那份文件」本身能不能玩、对不对。
// 用法：node scripts/check-pushed.mjs <url> <screenshotDir>
import puppeteer from 'puppeteer-core';
import { mkdir } from 'node:fs/promises';

const url = process.argv[2] ?? 'http://127.0.0.1:8125/';
const dir = process.argv[3] ?? 'shots/pushed';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const results = [];
const check = (name, ok, detail = '') => {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
};

await mkdir(dir, { recursive: true });

const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
p.on('pageerror', (e) => check('页面无 JS 报错', false, e.message));
await p.goto(url, { waitUntil: 'networkidle0' });
await p.evaluate(() => localStorage.clear());
await p.reload({ waitUntil: 'networkidle0' });

// 1) 开局屏
await p.waitForSelector('.starter', { timeout: 4000 }).catch(() => {});
const starterText = await p.$eval('body', (el) => el.innerText).catch(() => '');
check('开局屏在（选分路 / 摇数值 / 取名）', starterText.includes('开始生涯') && starterText.includes('摇'));
await p.screenshot({ path: `${dir}/01-starter.png`, fullPage: true });

// 选分路 + 取名 + 开始
await p.evaluate(() => document.querySelectorAll('.role')[1]?.click());
const nameOk = await p.$('.name-input');
if (nameOk) {
  await p.type('.name-input', '检查员');
  await sleep(120);
}
await p.evaluate(() => [...document.querySelectorAll('button')].find((x) => x.textContent.includes('开始生涯'))?.click());
await p.waitForSelector('.slot', { timeout: 4000 });
check('进入第 1 周（三个行动格已渲染）', Boolean(await p.$('.slot')));

// 2) 四个页签
const tabs = await p.$$eval('.tabs .tab', (els) => els.map((e) => e.textContent.trim()));
check('四个页签是 本周/赛程/生涯/收支', JSON.stringify(tabs) === JSON.stringify(['本周', '赛程', '生涯', '收支']), tabs.join('/'));

// 3) 新数值：上分成本 = 14 + 3×⌊(min(操作,对线) − 40) ÷ 10⌋
await p.evaluate(() => document.querySelectorAll('.slot')[0].click());
await p.waitForSelector('.sheet .btn.opt', { timeout: 3000 });
await sleep(400); // 等浮层动效走完再截图
const attrs = await p.$$eval('.attr', (els) => {
  const out = {};
  for (const el of els) {
    const k = el.querySelector('.name')?.textContent?.trim();
    const v = Number(el.querySelector('.val')?.textContent?.trim());
    if (k) out[k] = v;
  }
  return out;
});
const optTexts = await p.$$eval('.sheet .btn.opt', (els) => els.map((e) => e.innerText.replace(/\s+/g, ' ').trim()));
const rankLine = optTexts.find((t) => t.startsWith('上分')) ?? '';
const shownCost = Number((rankLine.match(/(\d+) 体力/) ?? [])[1]);
const expectCost = 14 + 3 * Math.floor((Math.min(attrs['操作'] ?? 0, attrs['对线'] ?? 0) - 40) / 10);
check('上分成本符合递增公式', shownCost === expectCost, `界面 ${shownCost} / 公式 ${expectCost}（操作 ${attrs['操作']}，对线 ${attrs['对线']}）`);
const restLine = optTexts.find((t) => t.startsWith('休息')) ?? '';
check('休息写「按上限的 25%」', restLine.includes('25%'), restLine);
await p.screenshot({ path: `${dir}/02-actions.png`, fullPage: true });
await p.evaluate(() => document.querySelector('.overlay')?.click());
await sleep(150);

// 4) 三个新页面各自有内容
for (const [tab, marker, file] of [
  ['schedule', '还没签约', '03-schedule.png'],
  ['career', '荣誉', '04-career.png'],
  ['money', '商店', '05-money.png'],
]) {
  await p.click(`[data-tab="${tab}"]`);
  await sleep(220);
  const txt = await p.evaluate(() => document.body.innerText).catch(() => '');
  check(`${tab} 页有内容`, txt.includes(marker), `${txt.replace(/\s+/g, ' ').slice(0, 40)}…`);
  await p.screenshot({ path: `${dir}/${file}`, fullPage: true });
}

// 5) 打到第 8 周收尾
async function pickRest() {
  await p.evaluate(() => {
    const all = [...document.querySelectorAll('.sheet .btn.opt')].filter((x) => !x.disabled);
    const rest = all.find((x) => (x.querySelector('.opt-name')?.textContent ?? '').includes('休息'));
    (rest ?? all[all.length - 1])?.click();
  });
  await sleep(110);
}
async function dismiss() {
  for (let i = 0; i < 6; i++) {
    const kind = await p.evaluate(() => {
      const ov = document.querySelector('.overlay');
      if (!ov) return null;
      if (ov.querySelector('[data-act="continue"]')) return 'outcome';
      if (ov.querySelector('[data-act="choose"]')) return 'event';
      return 'other';
    });
    if (!kind) return;
    if (kind === 'outcome') await p.click('[data-act="continue"]');
    else if (kind === 'event') await p.click('.overlay [data-act="choose"]');
    else await p.click('.overlay [data-act="close-sheet"]');
    await sleep(150);
  }
}

await p.click('[data-tab="week"]');
await sleep(150);
for (let w = 0; w < 12; w++) {
  if (await p.$('.ending')) break;
  const before = await p.$eval('.title', (el) => el.textContent).catch(() => '');
  for (let s = 0; s < 3; s++) {
    await p.evaluate((n) => document.querySelectorAll('.slot')[n].click(), s);
    await p.waitForSelector('.sheet .btn.opt', { timeout: 3000 });
    await pickRest();
  }
  await p.click('[data-act="end-week"]');
  await sleep(240);
  await dismiss();
  for (let i = 0; i < 20; i++) {
    if (await p.$('.ending')) break;
    const now = await p.$eval('.title', (el) => el.textContent).catch(() => '');
    if (now && now !== before) break;
    await sleep(120);
  }
}
const endingText = await p.$eval('.ending', (el) => el.innerText).catch(() => '');
const weekLine = await p.$eval('.title', (el) => el.textContent).catch(() => '');
check('第 8 周出「切片到此为止」', endingText.includes('切片到此为止'), weekLine.replace(/\s+/g, ' '));
await p.screenshot({ path: `${dir}/06-ending.png`, fullPage: true });

await b.close();
const failed = results.filter((r) => !r.ok).length;
console.log(`\n${results.length - failed}/${results.length} 通过`);
process.exit(failed ? 1 : 0);
