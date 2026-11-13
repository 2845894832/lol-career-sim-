// 掷骰体检：把 85 条草稿里的 roll 选项在三种状态下算一遍成功率。
// 用法（仓库根）：npx vite-node scripts/06-events/roll_audit.ts
import { newGame } from '../../src/core/state';
import { successRateOf } from '../../src/core/events';
import { createRng } from '../../src/rng';
import { ATTR_KEYS, type GameEvent, type GameState } from '../../src/types';
import draft from './draft80.json';

const events = draft as unknown as (GameEvent & { requires?: unknown })[];

function withAttrs(base: GameState, value: number, trust: number): GameState {
  const s = structuredClone(base);
  for (const k of ATTR_KEYS) s.attrs[k] = value;
  s.coachTrust = trust;
  return s;
}

const base = newGame(7);
const states: [string, GameState][] = [
  ['开局（属性 55 · 信任 40）', withAttrs(base, 55, 40)],
  ['中期（属性 70 · 信任 60）', withAttrs(base, 70, 60)],
  ['后期（属性 85 · 信任 80）', withAttrs(base, 85, 80)],
];

function quantile(xs: number[], q: number): number {
  const a = [...xs].sort((x, y) => x - y);
  return a[Math.min(a.length - 1, Math.floor(q * a.length))]!;
}

for (const [name, s] of states) {
  const all: number[] = [];
  const byKind = new Map<string, number[]>();
  for (const e of events) {
    for (const o of e.options) {
      if (o.risk !== 'roll') continue;
      const p = successRateOf(s, e, o);
      all.push(p);
      const arr = byKind.get(e.kind) ?? [];
      arr.push(p);
      byKind.set(e.kind, arr);
    }
  }
  const fmt = (x: number) => (x * 100).toFixed(1) + '%';
  console.log(`\n${name}  roll 选项 ${all.length}`);
  console.log(`  平均 ${fmt(all.reduce((a, b) => a + b, 0) / all.length)}  p10 ${fmt(quantile(all, 0.1))}  p50 ${fmt(quantile(all, 0.5))}  p90 ${fmt(quantile(all, 0.9))}`);
  console.log(`  <30% 占 ${((all.filter((p) => p < 0.3).length / all.length) * 100).toFixed(0)}%   >70% 占 ${((all.filter((p) => p > 0.7).length / all.length) * 100).toFixed(0)}%`);
  for (const [k, arr] of byKind) {
    console.log(`  ${k}: n=${arr.length} 平均 ${fmt(arr.reduce((a, b) => a + b, 0) / arr.length)}`);
  }
}

// RNG 抽查：同一个 p=0.5 的选项抽 20000 次，看实际命中率
const ctx = createRng(12345);
let hit = 0;
for (let i = 0; i < 20000; i++) if (ctx.rng.next() < 0.5) hit++;
console.log(`\nRNG 抽查 p=0.5 → 实测 ${(hit / 20000 * 100).toFixed(2)}%（20000 次）`);
