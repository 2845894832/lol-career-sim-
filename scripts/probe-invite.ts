import { reduce } from '../src/core/reduce';
import { newGame } from '../src/core/state';
import type { GameState } from '../src/types';

function week(s: GameState, plan: string[]) {
  let next = s;
  plan.forEach((a, i) => {
    next = reduce(next, { kind: 'selectAction', slot: i, action: a as never }).state;
  });
  next = reduce(next, { kind: 'endWeek' }).state;
  let guard = 0;
  while (next.pendingEvent && guard++ < 20) {
    const id = next.pendingEvent.eventId;
    next = reduce(next, { kind: 'chooseOption', option: 0 }).state;
    console.log(`  第 ${next.week} 周事件 ${id} → 选 A`);
  }
  return next;
}

let s = newGame(7);
for (let w = 1; w <= 6; w++) {
  s = week(s, ['rank', 'train', 'rest']);
  console.log(`第 ${w} 周：第 ${s.placement} 名，签约=${s.signed}`);
}
