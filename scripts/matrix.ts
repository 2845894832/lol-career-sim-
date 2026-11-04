/**
 * 策略矩阵：把「每周三格怎么排」按 8 种行动的全体组合（含重复）跑一遍，
 * 看有没有别的高胜率路径。
 *
 * 用法：npx vite-node scripts/matrix.ts [seeds]
 * 输出：终端一张表 + 写入 P3-策略矩阵.md
 */
import { writeFileSync } from 'node:fs';
import { newGame } from '../src/core/state';
import { reduce } from '../src/core/reduce';
import { getEvent, successRateOf } from '../src/core/events';
import { canAfford, isActionUnlocked } from '../src/core/actions';
import { CONFIG } from '../src/config';
import type { ActionId, AttrKey, GameState } from '../src/types';

const ATTRS: AttrKey[] = ['operation', 'laning', 'teamfight', 'awareness', 'mentality'];
const IDS: ActionId[] = [
  'rank',
  'train',
  'review',
  'scrim',
  'fitness',
  'stream',
  'business',
  'rest',
];

type Policy = ActionId[];

function weakest(state: GameState): AttrKey | null {
  let best: AttrKey | null = null;
  let low = 101;
  for (const k of ATTRS) {
    if (state.attrs[k] < low) {
      low = state.attrs[k];
      best = k;
    }
  }
  return low >= 100 ? null : best;
}

function resolvePending(state: GameState): GameState {
  let guard = 0;
  while (state.pendingEvent && guard++ < 4) {
    const ev = getEvent(state.pendingEvent.eventId);
    if (!ev) {
      state = reduce(state, { kind: 'endWeek' }).state;
      continue;
    }
    let best = 0;
    let bestRate = -1;
    ev.options.forEach((o, i) => {
      const r = successRateOf(state, ev, o);
      if (r > bestRate) {
        bestRate = r;
        best = i;
      }
    });
    state = reduce(state, { kind: 'chooseOption', option: best }).state;
  }
  return state;
}

interface Result {
  policy: Policy;
  avg: number;
  min: number;
  signedYear: number | null;
  wins: number;
  honors: number;
  peakRank: number;
  year90: number | null;
  finalRp: number;
  endTitle: string;
}

function playOne(policy: Policy, seed: number): Result {
  let state = newGame(seed, '测试', 'MID');
  let peakRank = state.placement;
  let signYear: number | null = null;
  let year90: number | null = null;
  let weeks = 0;

  while (!state.ended && state.year <= CONFIG.career.years) {
    for (let slot = 0; slot < 3; slot++) {
      let want = policy[slot];
      if (!isActionUnlocked(state, want) || !canAfford(state, slot, want)) want = 'rest';
      let target: AttrKey | undefined;
      if (want === 'train') {
        const w = weakest(state);
        if (!w) {
          want = 'rest';
        } else {
          target = w;
          if (!canAfford(state, slot, want, target)) want = 'rest';
        }
      }
      state = reduce(state, { kind: 'selectAction', slot, action: want, target }).state;
    }

    state = reduce(state, { kind: 'endWeek' }).state;
    state = resolvePending(state);
    if (state.placement < peakRank) peakRank = state.placement;
    if (!signYear && state.signed) signYear = state.year;
    if (!year90 && ATTRS.every((k) => state.attrs[k] >= 90)) year90 = state.year;
    if (++weeks > CONFIG.career.years * 30 + 30) break;
  }

  const attrs = ATTRS.map((k) => state.attrs[k]);
  const avg = attrs.reduce((a, b) => a + b, 0) / attrs.length;
  const min = Math.min(...attrs);
  const wins = state.seasonResults.filter((r) => r.won).length;
  return {
    policy,
    avg,
    min,
    signedYear: signYear,
    wins,
    honors: state.honors.length,
    peakRank,
    year90,
    finalRp: state.rankPoints,
    endTitle: state.ended?.title ?? '未结束',
  };
}

function combos(): Policy[] {
  const out: Policy[] = [];
  for (let a = 0; a < IDS.length; a++)
    for (let b = a; b < IDS.length; b++)
      for (let c = b; c < IDS.length; c++) out.push([IDS[a], IDS[b], IDS[c]]);
  return out;
}

const SEEDS = Number(process.argv[2] ?? 6);
const rows: Result[] = [];
for (const p of combos()) {
  for (let s = 0; s < SEEDS; s++) rows.push(playOne(p, 1000 + s));
}

interface Agg {
  policy: Policy;
  avg: number;
  min: number;
  winRate: number;
  signRate: number;
  signYear: number;
  honors: number;
  year90: number;
  year90n: number;
  n: number;
}

const by = new Map<string, Agg>();
for (const r of rows) {
  const key = r.policy.join('+');
  const a = by.get(key) ?? {
    policy: r.policy,
    avg: 0,
    min: 0,
    winRate: 0,
    signRate: 0,
    signYear: 0,
    honors: 0,
    year90: 0,
    year90n: 0,
    n: 0,
  };
  a.avg += r.avg;
  a.min += r.min;
  if (r.year90 !== null) {
    a.year90 += r.year90;
    a.year90n += 1;
  }
  a.winRate += r.wins;
  a.honors += r.honors;
  if (r.signedYear !== null) {
    a.signRate += 1;
    a.signYear += r.signedYear;
  }
  a.n += 1;
  by.set(key, a);
}

const list = [...by.values()].map((a) => ({
  ...a,
  avg: a.avg / a.n,
  min: a.min / a.n,
  winRate: a.winRate / CONFIG.career.years,
  signRate: a.signRate / a.n,
  signYear: a.signRate ? a.signYear / a.signRate : 0,
  honors: a.honors / a.n,
  year90: a.year90n ? a.year90 / a.year90n : 0,
  year90n: a.year90n,
}));

list.sort((x, y) => y.avg - x.avg);

const name = (p: Policy) => p.map((id) => ({ rank: '上分', train: '专训', review: '复盘', scrim: '训练赛', fitness: '健身', stream: '直播', business: '商业', rest: '休息' } as Record<ActionId, string>)[id]).join(' + ');

const lines: string[] = [];
lines.push(`# 策略矩阵（${SEEDS} 组种子 × ${list.length} 种排法）\n`);
lines.push('每周三格固定按同一种排法重复，事件一率选成功率最高的选项。\n');
lines.push('| # | 每周三格 | 五维均值 | 最弱维 | 全 90 年 | 达 90 比例 | 年均胜场 | 签约年 | 荣誉数 |');
lines.push('| --- | --- | --- | --- | --- | --- | --- | --- | --- |');
list.forEach((a, i) => {
  lines.push(
    `| ${i + 1} | ${name(a.policy)} | ${a.avg.toFixed(1)} | ${a.min.toFixed(1)} | ${a.year90 ? a.year90.toFixed(1) : '—'} | ${a.year90n}/${a.n} | ${a.winRate.toFixed(1)} | ${a.signYear ? a.signYear.toFixed(1) : '—'} | ${a.honors.toFixed(2)} |`,
  );
});
lines.push('');
writeFileSync('P3-策略矩阵.md', lines.join('\n'), 'utf8');
console.log(lines.slice(0, 16).join('\n'));
console.log(`\n全部 ${list.length} 种已写入 P3-策略矩阵.md`);
