/**
 * 05 号 ticket 用：旧占位强度 vs 新名单强度，同一套决策跑对照。
 *
 * 运行：npx vite-node scripts/05-opponent/sim.ts
 * 只读 src/；新旧差别只在 CONFIG.match.opponentSource（'fixed' | 'roster'）。
 *
 * 口径：
 * - 8 种子 × 3 策略 × 2 模式 = 48 局，每局跑到第 8 年结束，决策表与 03 号 sim.ts 相同。
 * - 「胜/负」= 日志里的「赢了。」/「输了…」，即 settleMatch 那条信任主线（每年约 26 场）。
 * - 「每年名次」= 每年第 30 周结算后 myPlace(state)（联赛内排名，1 起）。
 * - 「进决赛」= 触发过 SPR- / SUM- 开头或 E03 这类决赛事件。
 * - 「全胜/全败赛季」= 某年信任主线的比赛 ≥3 场且全赢 / 全输。
 * - 「最终段位」= rankOf(rankPoints, placement)。
 */
import { CONFIG } from '../../src/config';
import { reduce } from '../../src/core/reduce';
import { getEvent } from '../../src/core/events';
import { isMatchWeek, newGame } from '../../src/core/state';
import { myPlace } from '../../src/core/league';
import { rankOf } from '../../src/core/ladder';
import type { ActionId, GameState, LogEntry } from '../../src/types';

type Strategy = 'balanced' | 'grind' | 'noScrim';
type Mode = 'fixed' | 'roster';

const SEEDS = [1, 2, 3, 4, 5, 6, 7, 8];
const STRATEGIES: Strategy[] = ['balanced', 'grind', 'noScrim'];
const MODES: Mode[] = ['fixed', 'roster'];

function plan(s: GameState, strategy: Strategy): ActionId[] {
  if (strategy === 'grind') return s.signed ? ['scrim', 'scrim', 'rest'] : ['rank', 'rank', 'rest'];
  if (strategy === 'noScrim') return s.signed ? ['train', 'business', 'rest'] : ['rank', 'stream', 'rest'];
  return s.signed ? ['scrim', 'business', 'rest'] : ['rank', 'stream', 'rest'];
}

interface SeasonLine {
  year: number;
  wins: number;
  losses: number;
  place: number | null;
}
interface RunResult {
  mode: Mode;
  seed: number;
  strategy: Strategy;
  wins: number;
  losses: number;
  seasons: SeasonLine[];
  finals: number;
  finalYear: number;
  finished8: boolean;
  tier: string;
  place: number;
  rankPoints: number;
  trust: number;
}

function playOne(mode: Mode, seed: number, strategy: Strategy): RunResult {
  let s = newGame(seed);
  let guard = 0;
  let wins = 0;
  let losses = 0;
  let finals = 0;
  let seasonWins = 0;
  let seasonLosses = 0;
  let lastPlace: number | null = null;
  const seasons: SeasonLine[] = [];

  const takeLogs = (logs: LogEntry[]) => {
    for (const l of logs) {
      if (l.text === '赢了。') {
        wins += 1;
        seasonWins += 1;
      }
      if (l.text.startsWith('输了')) {
        losses += 1;
        seasonLosses += 1;
      }
    }
  };

  const closeSeason = (year: number) => {
    seasons.push({ year, wins: seasonWins, losses: seasonLosses, place: lastPlace });
    seasonWins = 0;
    seasonLosses = 0;
    lastPlace = null;
  };

  while (!s.ended && guard++ < 600) {
    // 第 30 周没有赛程，先记下这一刻的联赛名次，跨年后再算就没了。
    if (s.week === CONFIG.career.weeksPerYear && s.signed && s.year > 0) {
      lastPlace = myPlace(s);
    }
    const yearBefore = s.year;

    if (s.pendingEvent) {
      const event = getEvent(s.pendingEvent.eventId);
      if (!event) break;
      if (/^(SPR|SUM)-/.test(event.id) || event.id === 'E03') finals += 1;
      const r = reduce(s, { kind: 'chooseOption', option: seed % event.options.length });
      s = r.state;
      takeLogs(r.log);
    } else {
      const actions = plan(s, strategy);
      for (let slot = 0; slot < 3; slot++) {
        const r = reduce(s, { kind: 'selectAction', slot, action: actions[slot]! });
        s = r.state;
        takeLogs(r.log);
      }
      const r = reduce(s, { kind: 'endWeek' });
      s = r.state;
      takeLogs(r.log);
    }

    if (s.year !== yearBefore) closeSeason(yearBefore);
  }
  if (seasonWins + seasonLosses > 0) closeSeason(s.year);

  return {
    mode,
    seed,
    strategy,
    wins,
    losses,
    seasons,
    finals,
    finalYear: s.year,
    finished8: s.year >= CONFIG.career.years,
    tier: rankOf(s.rankPoints, s.placement).name,
    place: s.placement,
    rankPoints: s.rankPoints,
    trust: s.coachTrust,
  };
}

const allRuns: RunResult[] = [];
for (const mode of MODES) {
  (CONFIG.match as unknown as { opponentSource: Mode }).opponentSource = mode;
  for (const strategy of STRATEGIES) {
    for (const seed of SEEDS) allRuns.push(playOne(mode, seed, strategy));
  }
}

const pct = (n: number, d: number) => (d ? ((n / d) * 100).toFixed(1) + '%' : '—');
const avg = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
const f1 = (x: number) => x.toFixed(1);

const summary: Record<string, unknown> = {};

for (const mode of MODES) {
  const runs = allRuns.filter((r) => r.mode === mode);
  const w = runs.reduce((a, r) => a + r.wins, 0);
  const l = runs.reduce((a, r) => a + r.losses, 0);
  const finished = runs.filter((r) => r.finished8);
  const seasons = runs.flatMap((r) => r.seasons).filter((x) => x.place !== null);

  const yearPlace = Array.from({ length: 8 }, (_, i) => {
    const rows = runs
      .flatMap((r) => r.seasons)
      .filter((x) => x.year === i + 1 && x.place !== null)
      .map((x) => x.place!);
    return rows.length ? avg(rows) : null;
  });

  const winsByYear = Array.from({ length: 8 }, (_, i) => {
    const rows = runs.flatMap((r) => r.seasons).filter((x) => x.year === i + 1);
    return rows.length ? avg(rows.map((x) => x.wins)) : null;
  });

  const allWin = runs.flatMap((r) => r.seasons).filter((x) => x.wins >= 3 && x.losses === 0).length;
  const allLoss = runs.flatMap((r) => r.seasons).filter((x) => x.losses >= 3 && x.wins === 0).length;
  const seasonCount = runs.flatMap((r) => r.seasons).length;

  const tiers: Record<string, number> = {};
  for (const r of runs) tiers[r.tier] = (tiers[r.tier] ?? 0) + 1;
  const trustLow = runs.filter((r) => r.trust < CONFIG.match.benchThreshold).length;
  const trustMin = Math.min(...runs.map((r) => r.trust));

  const byStrategy = STRATEGIES.map((strategy) => {
    const rs = runs.filter((r) => r.strategy === strategy);
    const bw = rs.reduce((a, r) => a + r.wins, 0);
    const bl = rs.reduce((a, r) => a + r.losses, 0);
    return {
      strategy,
      winRate: bw / (bw + bl),
      winsAvg: bw / rs.length,
      finalsAvg: avg(rs.map((r) => r.finals)),
    };
  });

  const label = mode === 'fixed' ? '旧：60 / 78 占位' : '新：名单真值';
  console.log(`【${label}】`);
  console.log(`  比赛 ${w + l} 场 · 胜 ${w} · 负 ${l} · 胜率 ${pct(w, w + l)}`);
  console.log(`  平均每局胜场 ${f1(w / runs.length)} · 跑完 8 年的 ${finished.length}/${runs.length} 局，胜场均值 ${f1(avg(finished.map((r) => r.wins)))}`);
  console.log(`  每年胜场：${winsByYear.map((x, i) => `Y${i + 1}:${x === null ? '—' : f1(x)}`).join(' · ')}`);
  console.log(`  每年名次：${yearPlace.map((x, i) => `Y${i + 1}:${x === null ? '—' : f1(x)}`).join(' · ')}（1 最好）`);
  console.log(`  进决赛：${runs.filter((r) => r.finals > 0).length}/${runs.length} 局 · 平均 ${f1(avg(runs.map((r) => r.finals)))} 次`);
  console.log(`  全胜赛季 ${allWin}/${seasonCount} · 全败赛季 ${allLoss}/${seasonCount}`);
  console.log(`  最终段位：${Object.entries(tiers).map(([k, v]) => `${k} ${v}`).join(' · ')}`);
  console.log(`  全服名次均值 ${f1(avg(runs.map((r) => r.place)))} · 信任终值 ${f1(avg(runs.map((r) => r.trust)))} · 信任 <${CONFIG.match.benchThreshold} 的 ${trustLow}/${runs.length} 局（最低 ${trustMin}）`);
  console.log('');

  summary[mode] = {
    label,
    matches: w + l,
    wins: w,
    losses: l,
    winRate: w / (w + l),
    winsAvg: w / runs.length,
    finished8: finished.length,
    winsAvgFinished: avg(finished.map((r) => r.wins)),
    winsByYear,
    placeByYear: yearPlace,
    finalsRuns: runs.filter((r) => r.finals > 0).length,
    finalsAvg: avg(runs.map((r) => r.finals)),
    allWin,
    allLoss,
    seasonCount,
    tiers,
    byStrategy,
    placeAvg: avg(runs.map((r) => r.place)),
    trustAvg: avg(runs.map((r) => r.trust)),
    trustLow,
    trustMin,
  };
}

// 按策略拆：确认结论不是被某个策略带偏
console.log('【按策略拆】');
for (const mode of MODES) {
  for (const strategy of STRATEGIES) {
    const runs = allRuns.filter((r) => r.mode === mode && r.strategy === strategy);
    const w = runs.reduce((a, r) => a + r.wins, 0);
    const l = runs.reduce((a, r) => a + r.losses, 0);
    console.log(`  ${mode}/${strategy}: 胜率 ${pct(w, w + l)} · 胜场 ${f1(w / runs.length)} · 决赛 ${f1(avg(runs.map((r) => r.finals)))} 次`);
  }
}
console.log('');

const fs = await import('node:fs');
fs.writeFileSync(
  new URL('./out.json', import.meta.url),
  JSON.stringify(
    { generatedAt: new Date().toISOString(), summary, runs: allRuns.map((r) => ({ ...r, seasons: r.seasons })) },
    null,
    2,
  ),
);
console.log('已写出 scripts/05-opponent/out.json');
