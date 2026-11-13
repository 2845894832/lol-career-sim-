import puppeteer from 'puppeteer-core';
import path from 'node:path';
import fs from 'node:fs';

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const root = process.cwd();
const html = path.join(root, 'docs/build/13-14-cards.html');
const outDir = path.join(root, 'docs/13-14-一页图文');
fs.mkdirSync(outDir, { recursive: true });

const b = await puppeteer.launch({ executablePath: EDGE, headless: 'new' });
const p = await b.newPage();
await p.setViewport({ width: 900, height: 1200, deviceScaleFactor: 2 });
await p.goto('file:///' + html.replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
await p.evaluate(() => document.fonts.ready);

const names = { c1: '1-三层', c2: '2-三个词', c3: '3-39个字段' };
for (const [id, name] of Object.entries(names)) {
  const el = await p.$('#' + id);
  await el.screenshot({ path: path.join(outDir, name + '.png') });
  console.log('saved', path.join(outDir, name + '.png'));
}
await b.close();
