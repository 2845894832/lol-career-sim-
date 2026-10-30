/**
 * 批量验证：不打开界面，把一整局跑完并统计分布。
 * 运行：node node_modules/vite-node/vite-node.mjs scripts/batch.ts
 */
import { CONFIG } from '../src/config';
import { reduce } from '../src/core/reduce';
import { getEvent } from '../src/core/events';
import { newGame } from '../src/core/state';
import { ATTR_KEYS, ATTR_LABEL } from '../src/types';
import type { ActionId, AttrKey, GameState } from '../src/types';

/** 每周的策略：能签就练，不能签就上分+直播，最后休息。 */
function pickActions(s: GameState, mode: 'busy' | 'idle'): ActionId[] {
  if (mode === 'idle') return ['rest', 'rest', 'rest'];
  const plan: ActionId[] = [];
  plan.push(s.signed ? 'scrim' : 'rank');
  plan.push(s.signed ? 'business' : 'stream');
  plan.push('rest');
  return plan;
}

function playOne(seed: number, mode: 'busy' | 'idle'): GameState {
  let s = newGame(seed);
  let guard = 0;

  while (!s.ended && guard++ < 600) {
    if (s.pendingEvent) {
      const event = getEvent(s.pendingEvent.eventId);
      if (!event) break;
      // 固定策略：按种子选一个选项，保证可复现。
      const index = seed % event.options.length;
      s = reduce(s, { kind: 'chooseOption', option: index }).state;
      continue;
    }

    const plan = pickActions(s, mode);
    for (let slot = 0; slot < plan.length; slot++) {
      s = reduce(s, { kind: 'selectAction', slot, action: plan[slot]! }).state;
    }
    s = reduce(s, { kind: 'endWeek' }).state;
  }

  return s;
}

function percentile(values: number[], p: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[idx] ?? 0;
}

const RUNS = Number(process.argv[2] ?? 1000);
const results: GameState[] = [];
const failues: string[] = [];

for (let i = 0; i < RUNS; i++) {
  const mode = i % 2 === 0 ? 'busy' : 'idle';
  const s = playOne(i + 1, mode);
  if (!s.ended) {
    failues.push(`种子 ${i + 1} 没有走到结局（停在第 ${s.year} 年第 ${s.week} 周）`);
    continue;
  }
  results.push(s);
}

const kindCount = { normal: 0, special: 0 };
const titleCount = new Map<string, number>();
const peakYears: number[] = [];
const endYears: number[] = [];

for (const s of results) {
  kindCount[s.ended!.kind]++;
  titleCount.set(s.ended!.title, (titleCount.get(s.ended!.title) ?? 0) + 1);
  peakYears.push(s.peakYear);
  endYears.push(s.year);
}

const avg = (xs: number[]): number => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);

console.log(`\n批量验证：${RUNS} 局`);
console.log('═'.repeat(46));
console.log(`跑到结局：${results.length} / ${RUNS}`);
if (failues.length > 0) {
  console.log(`未结束：${failues.length} 局`);
  for (const f of failues.slice(0, 5)) console.log('  - ' + f);
}

console.log(`\n结局类型：普通 ${kindCount.normal} · 特殊 ${kindCount.special}`);
console.log('\n结局标题分布：');
for (const [title, count] of [...titleCount.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${title}　${count} 次（${((count / results.length) * 100).toFixed(1)}%）`);
}

console.log(`\n巅峰年份：均值 ${avg(peakYears).toFixed(1)}，中位 ${percentile(peakYears, 50)}`);
console.log(`生涯长度：均值 ${avg(endYears).toFixed(1)} 年`);

console.log('\n属性区间（最终）：');
for (const key of ATTR_KEYS) {
  const values = results.map((s) => s.attrs[key as AttrKey]);
  console.log(
    `  ${ATTR_LABEL[key]}  min ${Math.min(...values)} · p50 ${percentile(values, 50)} · max ${Math.max(...values)}`,
  );
}

console.log(`\n可调项：生涯 ${CONFIG.career.years} 年 · 每周 ${CONFIG.career.weeksPerYear} 周`);
