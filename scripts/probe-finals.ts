import { reduce } from '../src/core/reduce';
import { newGame } from '../src/core/state';
import { HONOR_LABEL } from '../src/types';
import type { GameState } from '../src/types';

function autoWeek(s: GameState): GameState {
  let next = s;
  ['rank', 'train', 'rest'].forEach((a, i) => {
    next = reduce(next, { kind: 'selectAction', slot: i, action: a as never }).state;
  });
  next = reduce(next, { kind: 'endWeek' }).state;
  let guard = 0;
  while (next.pendingEvent && guard++ < 20) {
    const ev = next.pendingEvent.eventId;
    process.stdout.write(`  事件 ${ev}`);
    next = reduce(next, { kind: 'chooseOption', option: 1 }).state;
    console.log(` → 选项 B`);
  }
  return next;
}

let s = newGame(7);
s = { ...s, signed: true };
for (let w = 1; w <= 9; w++) {
  const before = s.week;
  s = autoWeek(s);
  if (s.week === 9 && before === 8) break;
}
console.log('第 8 周后荣誉：', s.honors.map((h) => HONOR_LABEL[h]).join('、') || '无');
console.log('心态：', s.attrs.mentality, '人气：', s.attrs.popularity);
