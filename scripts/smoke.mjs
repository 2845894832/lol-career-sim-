/**
 * 冒烟测试：真开 Edge 无头浏览器，把 dist/index.html 点一遍。
 * 用法：node scripts/smoke.mjs
 */
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const require = createRequire(import.meta.url);
const puppeteer = require('puppeteer-core');

/** 浏览器路径可用 EDGE_PATH 覆盖，默认找本机 Edge。 */
const EDGE =
  process.env.EDGE_PATH ??
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PAGE = join(root, 'dist', 'index.html');

if (!existsSync(PAGE)) {
  console.error('先跑构建：node node_modules/vite/bin/vite.js build');
  process.exit(1);
}

const server = createServer((req, res) => {
  try {
    const body = readFileSync(PAGE);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end('not found');
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/`;

const browser = await puppeteer.launch({
  executablePath: EDGE,
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844 });

const errors = [];
page.on('pageerror', (e) => errors.push('JS 报错: ' + e.message));
page.on('console', (m) => {
  if (m.type() === 'error') errors.push('console: ' + m.text());
});

const sections = [];
let cur = null;
const section = (title) => {
  cur = { title, items: [] };
  sections.push(cur);
};
const check = async (label, fn) => {
  try {
    cur.items.push([true, label, (await fn()) ?? '']);
  } catch (e) {
    cur.items.push([false, label, e.message]);
  }
};
const assert = (cond, msg) => {
  if (!cond) throw new Error(msg);
};
const text = (sel) => page.$eval(sel, (el) => el.textContent.trim());
const has = async (sel) => (await page.$(sel)) !== null;

/** 结周后可能弹出事件卡和结果卡，一路点过去。 */
const clearOverlays = async () => {
  for (let i = 0; i < 5; i++) {
    if (await has('.overlay [data-act="choose"]')) {
      await page.click('.overlay [data-act="choose"]');
      await new Promise((r) => setTimeout(r, 60));
      continue;
    }
    if (await has('.overlay [data-act="continue"]')) {
      await page.click('.overlay [data-act="continue"]');
      await new Promise((r) => setTimeout(r, 60));
      continue;
    }
    break;
  }
};

/** 三格必须排满才能结周：把空格补成休息。 */
const fillSlots = async () => {
  for (let i = 0; i < 3; i++) {
    const slots = await page.$$('.slot');
    const slot = slots[i];
    if (!slot) continue;
    const v = await slot.$eval('.v', (el) => el.textContent.trim());
    if (v === '空') {
      await slot.click();
      const rest = await page.$('.sheet [data-act="pick-action"][data-id="rest"]');
      if (rest) await rest.click();
    }
  }
};

const endWeek = async () => {
  await fillSlots();
  await page.click('[data-act="end-week"]');
  await new Promise((r) => setTimeout(r, 80));
  await clearOverlays();
};

await page.goto(url, { waitUntil: 'load' });
await page.evaluate(() => localStorage.clear());
await page.goto(url, { waitUntil: 'load' });

section('开局屏');
await check('开局先停在“开始生涯”', async () => {
  const t = await text('.s-title');
  assert(t === '开始生涯', `实际：${t}`);
  return t;
});
await check('分路可选、名字必填才能开始', async () => {
  const disabled = await page.$eval('[data-act="start"]', (b) => b.disabled);
  await page.click('[data-act="role"][data-role="MID"]');
  const stillDisabled = await page.$eval('[data-act="start"]', (b) => b.disabled);
  await page.type('#nameInput', '测试');
  const enabled = await page.$eval('[data-act="start"]', (b) => !b.disabled);
  assert(disabled && stillDisabled && enabled, `disabled=${disabled} still=${stillDisabled} enabled=${enabled}`);
  return '空名字禁用、填完可点';
});
await check('点开始生涯进入第 1 周并落盘', async () => {
  await page.click('[data-act="start"]');
  await new Promise((r) => setTimeout(r, 150));
  const t = await text('.topbar .title');
  const saved = await page.evaluate(() => Object.keys(localStorage).some((k) => k.startsWith('lpl-career-proto')));
  assert(saved, '没写存档');
  return `${t}，已存档`;
});

section('主流程');
await check('页面加载无 JS 报错', async () => {
  assert(errors.length === 0, errors.join(' | '));
  return '0 个错误';
});
await check('开局停在第 1 年第 1 周', async () => {
  const t = await text('.topbar .title');
  assert(/第 1 年/.test(t) && /第 1 周/.test(t), `实际：${t}`);
  return t;
});
await check('六维可见', async () => {
  const names = await page.$$eval('.attr .name', (els) => els.map((e) => e.textContent.trim()));
  assert(names.length === 6, `只有 ${names.length} 项`);
  return names.join(' / ');
});
await check('三格都在', async () => {
  const n = (await page.$$('.slot')).length;
  assert(n === 3, `只有 ${n} 格`);
  return '3 格';
});
await check('点格子能选行动', async () => {
  await page.click('.slot');
  assert(await has('.sheet [data-act="pick-action"]'), '行动面板没出现');
  await page.click('.sheet [data-act="pick-action"][data-id="rank"]');
  const v = await text('.slot .v');
  assert(v === '上分', `格子里是「${v}」`);
  return v;
});
await check('结周进入下一周', async () => {
  await endWeek();
  const t = await text('.topbar .title');
  assert(/第 2 周/.test(t), `实际：${t}`);
  return t;
});
await check('刷新后回到上周状态，不是重开', async () => {
  await page.reload({ waitUntil: 'load' });
  const t = await text('.topbar .title');
  assert(!/第 1 周/.test(t), `刷新后又回到 ${t}`);
  return t;
});
await check('全程零外部请求', async () => {
  const ext = await page.evaluate(() =>
    performance
      .getEntriesByType('resource')
      .map((r) => r.name)
      .filter((u) => !u.startsWith('http://127.0.0.1')),
  );
  assert(ext.length === 0, ext.join(', '));
  return '只加载了页面本身';
});

section('连续推进');
await check('连点 12 周不崩、无报错', async () => {
  for (let i = 0; i < 12; i++) await endWeek();
  assert(errors.length === 0, errors.join(' | '));
  const t = await text('.topbar .title');
  return t;
});
await check('体力与六维仍在合法区间', async () => {
  const data = await page.evaluate(() => {
    const nums = [...document.querySelectorAll('.attr .val')].map((e) => Number(e.textContent));
    return { nums };
  });
  for (const n of data.nums) assert(n >= 0 && n <= 100, `属性越界：${n}`);
  return data.nums.join(',');
});

section('结局');
await check('点退役立刻看到结局', async () => {
  await page.click('[data-act="retire"]');
  const title = await text('.ending h2');
  assert(title.length > 0, '没有标题');
  return title;
});
await check('结局有正文与尾注', async () => {
  const paras = await page.$$eval('.ending p', (els) => els.map((e) => e.textContent.trim()));
  assert(paras.length >= 2, `只有 ${paras.length} 段`);
  return paras.join(' | ').slice(0, 60);
});
await check('「再来一局」能重开', async () => {
  await page.click('[data-act="restart"]');
  const t = await text('.s-title');
  assert(t === '开始生涯', `重开后是 ${t}`);
  return '回到开局屏';
});

section('响应式');
for (const w of [320, 360, 390, 430]) {
  await page.setViewport({ width: w, height: 844 });
  await page.reload({ waitUntil: 'load' });
  await check(`${w}px 无横向溢出`, async () => {
    const o = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      inner: window.innerWidth,
    }));
    assert(o.scroll <= o.inner, `内容 ${o.scroll}px > 视口 ${o.inner}px`);
    return `${o.scroll} ≤ ${o.inner}`;
  });
}

await browser.close();
server.close();

console.log('\n冒烟测试（真浏览器 · Edge 无头 · 390×844）\n');
let pass = true;
let total = 0;
let ok = 0;
for (const s of sections) {
  console.log(`── ${s.title} ${'─'.repeat(Math.max(0, 40 - s.title.length * 2))}`);
  for (const [good, label, detail] of s.items) {
    total++;
    if (good) ok++;
    else pass = false;
    console.log(`  ${good ? '✅' : '❌'} ${label}`);
    if (detail) console.log(`       ${detail}`);
  }
  console.log();
}
console.log('═'.repeat(50));
console.log(`${ok}/${total} 项通过`);
process.exit(pass ? 0 : 1);
