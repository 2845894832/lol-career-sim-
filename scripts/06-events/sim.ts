/**
 * 06 号 ticket 用：量化「事件库太小」到底小到什么程度。
 *
 * 运行：npx vite-node scripts/06-events/sim.ts
 * 输出：scripts/06-events/out-<tag>.json（tag 由命令行参数给，默认 after）
 *
 * 口径：
 * - 8 种子 × 3 策略 = 24 局，每局跑到第 8 年结束（约 240 周）。
 * - 「一次抽取」= 每周 endWeek() 里调用 drawEvent() 的那一次；排满三格才算一次。
 * - 「无事件」= 抽完 pendingEvent 仍为空（含兜底池也抽不到）。
 * - 「重复」= 同一局内同一个 event.id 被抽到的次数。
 * - 选项固定按 (seed + 周次) % 选项数 选，保证可复现，不引入额外随机。
 */
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { reduce } from '../../src/core/reduce';
import { getEvent } from '../../src/core/events';
import { newGame } from '../../src/core/state';
import type { ActionId, GameState } from '../../src/types';
import { EVENTS, FILLER_EVENTS } from '../../src/data/events';

type Strategy = 'balanced' | 'grind' | 'noScrim';

const SEEDS = [1, 2, 3, 4, 5, 6, 7, 8];
const STRATEGIES: Strategy[] = ['balanced', 'grind', 'noScrim'];

function plan(s: GameState, strategy: Strategy): ActionId[] {
  if (strategy === 'grind') return s.signed ? ['scrim', 'scrim', 'rest'] : ['rank', 'rank', 'rest'];
  if (strategy === 'noScrim') return s.signed ? ['train', 'business', 'rest'] : ['rank', 'stream', 'rest'];
  return s.signed ? ['scrim', 'business', 'rest'] : ['rank', 'stream', 'rest'];
}

interface RunResult {
  seed: number;
  strategy: Strategy;
  draws: number;
  events: number;
  empties: number;
  distinct: number;
  maxRepeat: { id: string; count: number };
  counts: Record<string, number>;
}

function playOne(seed: number, strategy: Strategy): RunResult {
  let s = newGame(seed);
  const counts: Record<string, number> = {};
  let draws = 0;
  let empties = 0;
  let events = 0;
  let guard = 0;

  while (!s.ended && guard++ < 500) {
    if (s.pendingEvent) {
      const event = getEvent(s.pendingEvent.eventId);
      if (!event) break;
      const index = (seed + s.week) % event.options.length;
      s = reduce(s, { kind: 'chooseOption', option: index }).state;
      continue;
    }

    const acts = plan(s, strategy);
    for (let slot = 0; slot < 3; slot++) {
      s = reduce(s, { kind: 'selectAction', slot, action: acts[slot]! }).state;
    }
    s = reduce(s, { kind: 'endWeek' }).state;

    // endWeek 里若抽到事件，会挂 pendingEvent；没挂就是「本周无事件」。
    draws++;
    if (s.pendingEvent) {
      events++;
      const id = s.pendingEvent.eventId;
      counts[id] = (counts[id] ?? 0) + 1;
    } else if (!s.ended) {
      empties++;
    }
  }

  let maxRepeat = { id: '-', count: 0 };
  for (const [id, n] of Object.entries(counts)) {
    if (n > maxRepeat.count) maxRepeat = { id, count: n };
  }

  return {
    seed,
    strategy,
    draws,
    events,
    empties,
    distinct: Object.keys(counts).length,
    maxRepeat,
    counts,
  };
}

const runs: RunResult[] = [];
for (const seed of SEEDS) {
  for (const strategy of STRATEGIES) {
    runs.push(playOne(seed, strategy));
  }
}

const ids = new Set<string>();
const perEvent = new Map<string, { total: number; runs: number; maxRepeat: number }>();
for (const r of runs) {
  for (const [id, n] of Object.entries(r.counts)) {
    ids.add(id);
    const cur = perEvent.get(id) ?? { total: 0, runs: 0, maxRepeat: 0 };
    cur.total += n;
    cur.runs += 1;
    cur.maxRepeat = Math.max(cur.maxRepeat, n);
    perEvent.set(id, cur);
  }
}

const sum = (f: (r: RunResult) => number): number => runs.reduce((a, r) => a + f(r), 0);
const totalDraws = sum((r) => r.draws);
const totalEvents = sum((r) => r.events);
const totalEmpties = sum((r) => r.empties);

const table = [...perEvent.entries()]
  .map(([id, v]) => ({
    id,
    kind: [...EVENTS, ...FILLER_EVENTS].find((e) => e.id === id)?.kind ?? 'final/invite',
    total: v.total,
    runs: v.runs,
    avgPerRun: Number((v.total / runs.length).toFixed(2)),
    avgWhenPresent: Number((v.total / v.runs).toFixed(2)),
    maxRepeat: v.maxRepeat,
  }))
  .sort((a, b) => b.total - a.total);

const summary = {
  runs: runs.length,
  totalDraws,
  totalEvents,
  totalEmpties,
  emptyRate: Number((totalEmpties / totalDraws).toFixed(4)),
  drawsPerRun: Number((totalDraws / runs.length).toFixed(1)),
  eventsPerRun: Number((totalEvents / runs.length).toFixed(1)),
  emptiesPerRun: Number((totalEmpties / runs.length).toFixed(1)),
  distinctEvents: ids.size,
  maxRepeatInRun: runs.reduce((m, r) => Math.max(m, r.maxRepeat.count), 0),
  avgRepeatOfDrawn: Number((totalEvents / Math.max(1, ids.size)).toFixed(1)),
  avgRepeatPerRun: Number(
    (runs.reduce((m, r) => m + Math.max(...Object.values(r.counts), 0), 0) / runs.length).toFixed(1),
  ),
};

const tag = process.argv[2] ?? 'after';
const here = dirname(fileURLToPath(import.meta.url));
const out = { tag, generatedAt: new Date().toISOString(), summary, runs, table };
writeFileSync(join(here, `out-${tag}.json`), JSON.stringify(out, null, 2), 'utf-8');

const pad = (v: string | number, n: number): string => String(v).padEnd(n);
console.log(
  pad('事件', 14) + pad('类型', 10) + pad('总次数', 8) + pad('均值/局', 9) + pad('出现局数', 9) + '单局最高',
);
for (const row of table) {
  console.log(
    pad(row.id, 14) +
      pad(row.kind, 10) +
      pad(row.total, 8) +
      pad(row.avgPerRun, 9) +
      pad(row.runs, 9) +
      row.maxRepeat,
  );
}
console.log('---');
for (const [k, v] of Object.entries(summary)) console.log(k, v);
