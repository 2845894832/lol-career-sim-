import { newGame } from '../src/core/state';
import { trainGain, gainPoints } from '../src/core/growth';

const s = newGame(7);
for (const phase of [1, 3, 7]) {
  s.year = phase;
  s.attrs.operation = 55;
  const rows: string[] = [];
  for (const v of [55, 59, 60, 79, 80, 99]) {
    s.attrs.operation = v;
    rows.push(`${v}→+${trainGain(s, 'operation')}`);
  }
  console.log(`第 ${phase} 年（${phase === 1 ? '成长' : phase === 3 ? '巅峰' : '衰退'}）`, rows.join('  '));
}

// 从 55 练到 100 需要几格（巅峰期，无成长加成）
s.year = 3;
s.attrs.operation = 55;
let slots = 0;
while (s.attrs.operation < 100 && slots < 500) {
  gainPoints(s, 'operation', trainGain(s, 'operation'));
  slots += 1;
}
console.log('巅峰期 55→100 需要', slots, '格');
