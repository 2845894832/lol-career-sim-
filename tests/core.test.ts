import { describe, expect, it } from 'vitest';
import { CONFIG } from '../src/config';
import { reduce } from '../src/core/reduce';
import { applyAction, canAfford } from '../src/core/actions';
import { advanceYear, gainExp } from '../src/core/growth';
import { autoMatch, applyMatchOutcome } from '../src/core/match';
import { normalEnding, specialEnding } from '../src/core/endings';
import { drawEvent } from '../src/core/events';
import { createRng } from '../src/rng';
import { fromSaveJson, toSaveJson } from '../src/core/save';
import { loadSaved, persist } from '../src/core/save';
import { newGame, rankTier } from '../src/core/state';
import { ATTR_KEYS, type Action, type GameState } from '../src/types';

/** 一周：排三格 → 结周 → 处理事件。 */
function step(state: GameState): GameState {
  let s = state;
  const plan: { action: 'rank' | 'stream' | 'rest'; slot: number }[] = [
    { slot: 0, action: 'rank' },
    { slot: 1, action: 'stream' },
    { slot: 2, action: 'rest' },
  ];
  for (const p of plan) {
    s = reduce(s, { kind: 'selectAction', slot: p.slot, action: p.action }).state;
  }
  s = reduce(s, { kind: 'endWeek' }).state;
  let guard = 0;
  while (s.pendingEvent && guard++ < 3) {
    s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
  }
  return s;
}

function runCareer(seed: number): GameState {
  let s = newGame(seed);
  let guard = 0;
  while (!s.ended && guard++ < 400) s = step(s);
  return s;
}

describe('开局', () => {
  it('五项属性在 40–70 之间随机，人气固定 20', () => {
    for (let seed = 1; seed <= 40; seed++) {
      const s = newGame(seed);
      for (const key of ATTR_KEYS) {
        if (key === 'popularity') expect(s.attrs[key]).toBe(20);
        else {
          expect(s.attrs[key]).toBeGreaterThanOrEqual(40);
          expect(s.attrs[key]).toBeLessThanOrEqual(70);
        }
      }
    }
  });

  it('同种子开局完全一致', () => {
    expect(newGame(99)).toEqual(newGame(99));
  });
});

describe('确定性', () => {
  it('同状态 + 同动作 + 同种子 → 同结果', () => {
    const a = newGame(1234);
    const b = newGame(1234);
    expect(step(a)).toEqual(step(b));
  });

  it('连续 20 周后两条同种子路径仍一致', () => {
    let a = newGame(77);
    let b = newGame(77);
    for (let i = 0; i < 20; i++) {
      a = step(a);
      b = step(b);
    }
    expect(a).toEqual(b);
  });
});

describe('边界不变式', () => {
  it('跑一整局，六维与人气始终在 0–100', () => {
    let s = newGame(2024);
    let guard = 0;
    while (!s.ended && guard++ < 400) {
      s = step(s);
      for (const key of ATTR_KEYS) {
        expect(s.attrs[key]).toBeGreaterThanOrEqual(0);
        expect(s.attrs[key]).toBeLessThanOrEqual(100);
      }
      expect(s.stamina).toBeGreaterThanOrEqual(0);
      expect(s.coachTrust).toBeGreaterThanOrEqual(0);
      expect(s.coachTrust).toBeLessThanOrEqual(100);
      expect(s.injury).toBeGreaterThanOrEqual(0);
      expect(s.injury).toBeLessThanOrEqual(3);
    }
  });

  it('属性到 100 后继续训练不再涨', () => {
    const s = newGame(5);
    s.attrs.operation = 100;
    s.exp.operation = 0;
    const gain = gainExp(s, 'operation', 999);
    expect(gain.points).toBe(0);
    expect(s.attrs.operation).toBe(100);
  });

  it('体力不够时该格只能选休息', () => {
    const s = newGame(1);
    s.stamina = 3;
    expect(canAfford(s, 0, 'rank')).toBe(false);
    const next = reduce(s, { kind: 'selectAction', slot: 0, action: 'rank' }).state;
    expect(next.actionGrid[0]).toBe('rest');
  });
});

describe('行动', () => {
  it('未签约时训练赛与商业活动不可用', () => {
    const s = newGame(1);
    expect(s.signed).toBe(false);
    const afterScrim = reduce(s, { kind: 'selectAction', slot: 0, action: 'scrim' }).state;
    expect(afterScrim.actionGrid[0]).toBeNull();
    const afterBiz = reduce(s, { kind: 'selectAction', slot: 0, action: 'business' }).state;
    expect(afterBiz.actionGrid[0]).toBeNull();
  });

  it('健身提高体力上限，休息恢复体力', () => {
    const s = newGame(3);
    s.stamina = 10;
    const before = s.maxStamina;
    applyAction(s, 'fitness', null);
    expect(s.maxStamina).toBeGreaterThan(before);
    const low = s.stamina;
    applyAction(s, 'rest', null);
    expect(s.stamina).toBeGreaterThan(low);
  });

  it('上分累积段位', () => {
    const s = newGame(3);
    const before = s.rankPoints;
    applyAction(s, 'rank', null);
    expect(s.rankPoints).toBeGreaterThan(before);
  });
});

describe('成长', () => {
  it('属性越高，涨一点需要的经验越多', () => {
    const low = newGame(1);
    const high = newGame(1);
    low.attrs.operation = 30;
    high.attrs.operation = 90;
    low.exp.operation = 0;
    high.exp.operation = 0;
    low.year = 1;
    high.year = 1;
    gainExp(low, 'operation', 200);
    gainExp(high, 'operation', 200);
    expect(low.attrs.operation - 30).toBeGreaterThan(high.attrs.operation - 90);
  });

  it('衰退期四项下降，心态与人气不降', () => {
    const s = newGame(1);
    s.year = 7;
    s.attrs.operation = 80;
    s.attrs.laning = 80;
    s.attrs.teamfight = 80;
    s.attrs.awareness = 80;
    s.attrs.mentality = 50;
    s.attrs.popularity = 50;
    advanceYear(s);
    expect(s.attrs.operation).toBeLessThan(80);
    expect(s.attrs.laning).toBeLessThan(80);
    expect(s.attrs.teamfight).toBeLessThan(80);
    expect(s.attrs.awareness).toBeLessThan(80);
    expect(s.attrs.mentality).toBeGreaterThanOrEqual(50);
    expect(s.attrs.popularity).toBe(50);
  });
});

describe('事件与临场值', () => {
  it('临时加减在结周后清零', () => {
    let s = newGame(11);
    s.temp = { operation: 10 };
    for (let i = 0; i < 3; i++) s = reduce(s, { kind: 'selectAction', slot: i, action: 'rest' }).state;
    s = reduce(s, { kind: 'endWeek' }).state;
    let guard = 0;
    while (s.pendingEvent && guard++ < 3) {
      s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    }
    expect(s.temp).toEqual({});
  });

  it('必败选项一定失败', () => {
    const s = newGame(1);
    s.pendingEvent = { eventId: 'E02', isMatch: false };
    const before = s.attrs.laning;
    const r = reduce(s, { kind: 'chooseOption', option: 1 }).state;
    expect(r.attrs.laning).toBeLessThan(before);
  });
});

describe('比赛', () => {
  it('自动比赛会改变教练信任或伤病', () => {
    const s = newGame(8);
    const before = s.coachTrust;
    const { win } = autoMatch(s);
    applyMatchOutcome(s, win, false);
    expect(s.coachTrust).not.toBe(before);
  });
});

describe('存档', () => {
  it('序列化再反序列化后状态等价', () => {
    const s = newGame(42);
    s.attrs.operation = 66;
    s.flags.push('试训通过');
    const back = fromSaveJson(toSaveJson(s));
    expect(back).not.toBeNull();
    expect(back).toEqual({ ...s, temp: {} });
  });

  it('版本不符时安全重开而不是崩', () => {
    const s = newGame(42);
    const raw = JSON.stringify({ version: 999, state: s });
    expect(fromSaveJson(raw)).toBeNull();
    expect(fromSaveJson('not json')).toBeNull();
    expect(fromSaveJson(null)).toBeNull();
  });

  it('没有 localStorage 时读写不抛错', () => {
    expect(loadSaved()).toBeNull();
    expect(() => persist(newGame(1))).not.toThrow();
  });
});

describe('整局', () => {
  it('固定种子跑完整局，一定落在一个结局上', () => {
    const ended = runCareer(555);
    expect(ended.ended).not.toBeNull();
    expect(['normal', 'special']).toContain(ended.ended?.kind);
    expect(ended.ended?.title.length).toBeGreaterThan(0);
  });

  it('同种子跑两局，结局与关键数值完全一致', () => {
    const a = runCareer(1234);
    const b = runCareer(1234);
    expect(a.ended).toEqual(b.ended);
    expect(a.attrs).toEqual(b.attrs);
    expect(a.year).toBe(b.year);
  });

  it('结局分普通与特殊两种模板', () => {
    const s = newGame(1);
    expect(normalEnding(s, 'expired').kind).toBe('normal');
    expect(specialEnding(s).kind).toBe('special');
    expect(specialEnding(s).note.length).toBeGreaterThan(0);
  });

  it('段位按点数映射到十档', () => {
    expect(rankTier(0).name).toBe('黑铁');
    expect(rankTier(CONFIG.rank.max).name).toBe('王者');
  });
});

describe('事件抽取', () => {
  it('权重 1:10 的抽取比例符合量级', () => {
    const { rng } = createRng(2024);
    let special = 0;
    const total = 12000;
    for (let i = 0; i < total; i++) {
      if (rng.weighted([1, 10]) === 0) special++;
    }
    const ratio = special / total;
    expect(ratio).toBeGreaterThan(0.06);
    expect(ratio).toBeLessThan(0.12);
  });

  it('第 3 年第 26 周必出决赛事件', () => {
    const s = newGame(1);
    s.year = 3;
    s.week = 26;
    const r = drawEvent(s);
    expect(r.event?.id).toBe('E03');
  });

  it('休赛期抽不到比赛事件', () => {
    const s = newGame(3);
    s.week = 28;
    for (let i = 0; i < 60; i++) {
      const r = drawEvent(s);
      s.rngState = r.rngState;
      if (r.event) expect(r.event.kind).not.toBe('match');
    }
  });

  it('事件写入的标记能被结局尾注读到', () => {
    const s = newGame(1);
    s.flags.push('试训通过');
    expect(normalEnding(s, 'expired').note).toContain('试训');
  });
});

describe('动作接口', () => {
  it('未知槽位不会写坏状态', () => {
    const s = newGame(1);
    const r = reduce(s, { kind: 'selectAction', slot: 9, action: 'rank' } as Action).state;
    expect(r.actionGrid).toEqual([null, null, null]);
  });
});
