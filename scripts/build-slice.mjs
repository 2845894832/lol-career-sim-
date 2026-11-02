// 出切片副本：SLICE=1 让 vite.config 注入 __SLICE_AT__ = 8，产物在 dist-slice/。
// 用一条 shell 命令串（不用 args 数组），Windows 的 .cmd 也能跑。
import { spawnSync } from 'node:child_process';

const run = (cmd) => {
  const r = spawnSync(cmd, { stdio: 'inherit', shell: true, env: { ...process.env, SLICE: '1' } });
  if (r.status !== 0) process.exit(r.status ?? 1);
};

run('npx tsc --noEmit');
run('npx vite build');
