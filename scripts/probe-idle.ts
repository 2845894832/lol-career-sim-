import { reduce } from '../src/core/reduce';
import { newGame } from '../src/core/state';
import { rankOf } from '../src/core/ladder';
import type { GameState } from '../src/types';

function week(s: GameState, plan: string[]): GameState {
  let next = s;
  plan.forEach((a, i) => {
    next = reduce(next, { kind: 'selectAction', slot: i, action: a as never }).state;
  });
  next = reduce(next, { kind: 'endWeek' }).state;
  let guard = 0;
  while (next.pendingEvent && guard++ < 20) {
    next = reduce(next, { kind: 'chooseOption', option: 0 }).state;
  }
  return next;
}

let s = newGame(42);
for (let w = 1; w <= 5; w++) s = week(s, ['rank', 'train', 'rest']);
console.log(`第 5 周结束：第 ${s.placement} 名 ${rankOf(s.rankPoints, s.placement).name}`);
for (let w = 6; w <= 9; w++) {
  s = week(s, ['rest', 'rest', 'rest']);
  console.log(`不打第 ${w - 5} 周：第 ${s.placement} 名 ${rankOf(s.rankPoints, s.placement).name}`);
}
