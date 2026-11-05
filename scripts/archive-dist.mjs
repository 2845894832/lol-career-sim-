// 归档当前构建产物：dist/index.html → dist/archive/index-YYYYMMDD-HHmm.html
// 只读 dist/index.html，不改它；dist/* 已被 .gitignore 忽略，归档不进版本库。
// 用法：npm run build 之后跑 npm run build:archive（或 node scripts/archive-dist.mjs）。
// 回滚：把 dist/archive/ 里上一版的文件重命名/复制回 dist/index.html，再重传平台。
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(root, "dist", "index.html");
const archiveDir = join(root, "dist", "archive");

if (!existsSync(src)) {
  console.error("没有 dist/index.html，先跑 npm run build");
  process.exit(1);
}

const pad = (n) => String(n).padStart(2, "0");
const d = new Date();
const stamp =
  `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-` +
  `${pad(d.getHours())}${pad(d.getMinutes())}`;

mkdirSync(archiveDir, { recursive: true });
const dest = join(archiveDir, `index-${stamp}.html`);
copyFileSync(src, dest);
console.log(`归档 → ${dest}`);
