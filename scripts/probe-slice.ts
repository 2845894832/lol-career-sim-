import { reduce } from '../src/core/reduce';
import { newGame } from '../src/core/state';
import { CONFIG } from '../src/config';
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
    next = reduce(next, { kind: 'chooseOption', option: 0 }).state;
  }
  return next;
}

console.log('sliceAtWeek =', CONFIG.career.sliceAtWeek);

let s = newGame(11);
s = { ...s, signed: true };
for (let i = 0; i < 12; i++) {
  if (s.ended) break;
  s = autoWeek(s);
  console.log(`打完后 week=${s.week} 名次=${s.placement} 段位分=${s.rankPoints} 荣誉=${s.honors.map((h) => HONOR_LABEL[h]).join('、') || '无'}`);
}
if (s.ended) {
  console.log('--- 结局页 ---');
  console.log('标题:', s.ended.title);
  console.log('正文:', s.ended.body);
  console.log('尾注:', s.ended.note);
} else {
  console.log('!! 没有收尾');
}
