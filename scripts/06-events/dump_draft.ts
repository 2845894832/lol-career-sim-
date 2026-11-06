// 把草稿事件导出成 JSON，供审阅表使用；不修改 src。
import { writeFileSync } from 'node:fs';
import { EVENTS } from './_draft80';

const out = EVENTS.map((e) => ({
  id: e.id,
  kind: e.kind,
  phase: e.phase,
  tags: [...e.tags],
  text: e.text,
  once: e.once,
  weight: e.weight,
  opponent: e.opponent ?? null,
  opponentRole: e.opponentRole ?? null,
  year: e.year ?? null,
  week: e.week ?? null,
  options: e.options.map((o) => ({
    label: o.label,
    risk: o.risk,
    attrs: o.attrs ? [...o.attrs] : null,
    mix: o.mix ?? null,
    bonus: o.bonus ?? null,
    skillBonus: o.skillBonus ?? false,
    matchResult: o.matchResult ?? null,
    success: o.success ?? null,
    fail: o.fail ?? null,
    successText: o.successText ?? null,
    failText: o.failText ?? null,
  })),
}));

writeFileSync(new URL('./draft80.json', import.meta.url), JSON.stringify(out, null, 1), 'utf-8');
console.log('events', out.length, 'options', out.reduce((n, e) => n + e.options.length, 0));
