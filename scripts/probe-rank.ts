import { CONFIG } from '../src/config';
import { reduce } from '../src/core/reduce';
import { newGame } from '../src/core/state';
import { rankOf, weeklyGain } from '../src/core/ladder';
import type { GameState } from '../src/types';

type Plan = ('rank' | 'train' | 'rest')[];
function week(s: GameState, plan: Plan): GameState {
  let next = s;
  plan.forEach((a, i) => {
    next = reduce(next, { kind: 'selectAction', slot: i, action: a }).state;
  });
  next = reduce(next, { kind: 'endWeek' }).state;
  let guard = 0;
  while (next.pendingEvent && guard++ < 20) {
    next = reduce(next, { kind: 'chooseOption', option: 0 }).state;
  }
  return next;
}

const PLAN: Plan = (process.argv[2] ?? 'rank,rank,rest').split(',') as Plan;

let s = newGame(42);
console.log(`开局 第 ${s.placement} 名 ${rankOf(s.rankPoints, s.placement).name} 分 ${Math.round(s.rankPoints)}`);
for (let w = 1; w <= 40; w++) {
  s = week(s, PLAN);
  if (s.ended) { console.log('结束', s.ended.title); break; }
  const r = rankOf(s.rankPoints, s.placement);
  console.log(`第 ${w} 周：第 ${s.placement} 名 ${r.name} 分 ${Math.round(s.rankPoints)} 本周+${weeklyGain(s.rankPoints)} 签约=${s.signed}`);
}
console.log('赛年：', s.year, '周', s.week);
