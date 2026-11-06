import { describe, expect, it } from 'vitest';
import { CONFIG } from '../src/config';
import { isStarting, startRequirement, fixtureThisWeek, finalOpponentStrength, opponentStrength, rivalStrength, seasonAverageStrength, seasonStrengths, seasonTopStrength, winChance } from '../src/core/league';
import { reduce } from '../src/core/reduce';
import { staminaCost } from '../src/core/actions';
import { applyAction, canAfford } from '../src/core/actions';
import { advanceYear, gainExp, gainPoints, trainGain } from '../src/core/growth';
import { autoMatch, applyMatchOutcome, matchRate } from '../src/core/match';
import { normalEnding, specialEnding } from '../src/core/endings';
import { drawEvent, resolveOption, successRateOf } from '../src/core/events';
import { EVENTS } from '../src/data/events';
import { canPlay, benchReason } from '../src/core/match';
import { createRng } from '../src/rng';
import { fromSaveJson, toSaveJson } from '../src/core/save';
import { loadSaved, persist } from '../src/core/save';
import { newGame, rankTier } from '../src/core/state';
import { placementOf, rankOf, weeklyGain } from '../src/core/ladder';
import { ATTR_KEYS, MATCH_ATTRS, type Action, type GameEvent, type GameState } from '../src/types';
import { SHOP, buy, buyBlocker, hasOnce, restBonus, streamIncome, subActive, subUntil, weekIncome, weekSpend } from '../src/core/shop';
import { springFinal } from '../src/data/finals';

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
  it('练一次的收益固定：基础 1 点，成长阶段不再额外加成', () => {
    const young = newGame(1);
    const old = newGame(1);
    young.year = 1;
    old.year = 3;
    young.attrs.operation = 50;
    old.attrs.operation = 50;
    gainPoints(young, 'operation', 1);
    gainPoints(old, 'operation', 1);
    expect(young.attrs.operation).toBe(51);
    expect(old.attrs.operation).toBe(51);
  });

  it('属性越高，这一格越贵（每 10 点 +3 体力）', () => {
    const s = newGame(1);
    s.attrs.awareness = 45;
    expect(staminaCost(s, 'review')).toBe(8);
    s.attrs.awareness = 65;
    expect(staminaCost(s, 'review')).toBe(14);
    s.attrs.awareness = 95;
    expect(staminaCost(s, 'review')).toBe(23);
  });

  it('休息按体力上限的 20% 恢复', () => {
    const s = newGame(1);
    s.stamina = 10;
    s.maxStamina = 100;
    s.actionGrid = ['rest', 'rest', 'rest'];
    s.actionTargets = [null, null, null];
    const state = reduce(s, { kind: 'endWeek' }).state;
    expect(state.stamina).toBeGreaterThan(10 + 20 - 1);
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
    s.pendingEvent = { eventId: 'E02' };
    const before = s.attrs.laning;
    const r = reduce(s, { kind: 'chooseOption', option: 1 }).state;
    expect(r.attrs.laning).toBeLessThan(before);
  });
});

describe('比赛', () => {
  it('自动比赛会改变教练信任或伤病', () => {
    const s = newGame(8);
    const before = s.coachTrust;
    const { win } = autoMatch(s, CONFIG.match.opponentDefault);
    applyMatchOutcome(s, win, false);
    expect(s.coachTrust).not.toBe(before);
  });

  it('伤病标记会触发 E05，并在事件结算后清掉', () => {
    const s = newGame(1);
    s.signed = true;
    s.week = 10;
    s.injury = 0;
    s.flags.push('#手腕不适');
    const drawn = drawEvent(s);
    expect(drawn.event?.id).toBe('E05');
    resolveOption(s, drawn.event!, 0);
    expect(s.injury).toBe(1);
    expect(s.flags).not.toContain('#手腕不适');
    // once: false 的事件清掉标记后还能再次被 forced 抽到。
    s.flags.push('#手腕不适');
    expect(drawEvent(s).event?.id).toBe('E05');
  });

  it('临场加减会改变自动比赛的胜率', () => {
    let s = newGame(7);
    let normal = 0;
    let debuffed = 0;
    for (let i = 0; i < 200; i++) {
      const a = structuredClone(s);
      if (autoMatch(a, CONFIG.match.opponentDefault).win) normal++;
      s.rngState = a.rngState;

      const b = structuredClone(s);
      for (const key of MATCH_ATTRS) b.temp[key] = -1000;
      if (autoMatch(b, CONFIG.match.opponentDefault).win) debuffed++;
      s.rngState = b.rngState;
    }
    expect(normal).toBeGreaterThan(60);
    expect(debuffed).toBeLessThan(normal);
  });
});

describe('对手强度表', () => {
  it('赛程周的对手 = 赛程里那支队的名单强度', () => {
    const s = newGame(3);
    s.signed = true;
    s.teamId = 'RNG';
    s.year = 1;
    let found = 0;
    for (let w = 1; w <= CONFIG.career.matchWeeksPerYear; w++) {
      s.week = w;
      const fixture = fixtureThisWeek(s);
      if (!fixture) continue;
      found += 1;
      expect(opponentStrength(s)).toBeCloseTo(rivalStrength(1, fixture.rivalId), 6);
    }
    expect(found).toBeGreaterThan(0);
  });

  it('非赛程周用当季平均，决赛周用当季最强', () => {
    const s = newGame(3);
    s.signed = true;
    s.teamId = 'RNG';
    s.year = 1;
    s.week = 1; // 第 1 周没有赛程
    expect(opponentStrength(s)).toBeCloseTo(seasonAverageStrength(1), 6);

    s.year = CONFIG.career.finalYear;
    s.week = CONFIG.career.finalWeek;
    expect(opponentStrength(s)).toBeCloseTo(seasonTopStrength(CONFIG.career.finalYear), 6);
  });

  it('强度表只来自名单：按赛季降序，队数与 rosters 一致', () => {
    for (let year = 1; year <= CONFIG.career.years; year++) {
      const rows = seasonStrengths(year);
      expect(rows.length).toBeGreaterThanOrEqual(14);
      for (let i = 1; i < rows.length; i++) {
        expect(rows[i - 1]!.strength).toBeGreaterThanOrEqual(rows[i]!.strength);
      }
      const avg = rows.reduce((sum, r) => sum + r.strength, 0) / rows.length;
      expect(seasonAverageStrength(year)).toBeCloseTo(avg, 6);
    }
    // 第 1 季（S8）最强是 RNG 87.4，最弱是 VG 69.4，均为五人 ovr 均值。
    expect(seasonStrengths(1)[0]!.name).toBe('RNG');
    expect(seasonStrengths(1)[0]!.strength).toBeCloseTo(87.4, 6);
    const first = seasonStrengths(1);
    expect(first[first.length - 1]!.strength).toBeCloseTo(69.4, 6);
  });

  it('决赛事件按当季最强队算，不再用写死的 65', () => {
    const s = newGame(4);
    s.signed = true;
    s.year = 1;
    const event = springFinal(1);
    const option = event.options[0]!;
    expect(successRateOf(s, event, option)).toBeCloseTo(
      matchRate(s, seasonTopStrength(1), option.bonus ?? 0),
      6,
    );
    expect(finalOpponentStrength(1, 65)).toBeCloseTo(seasonTopStrength(1), 6);
  });

  it('opponentSource=fixed 时回到 60/78 兜底', () => {
    const s = newGame(5);
    s.signed = true;
    s.teamId = 'RNG';
    s.year = 1;
    s.week = 4;
    const saved = CONFIG.match.opponentSource;
    const cfg = CONFIG.match as { opponentSource: 'fixed' | 'roster' };
    try {
      cfg.opponentSource = 'fixed';
      expect(opponentStrength(s)).toBe(CONFIG.match.opponentDefault);
      s.year = CONFIG.career.finalYear;
      s.week = CONFIG.career.finalWeek;
      expect(opponentStrength(s)).toBe(CONFIG.match.opponentFinal);
      expect(finalOpponentStrength(1, 65)).toBe(65);
    } finally {
      cfg.opponentSource = saved;
    }
  });

  it('赛程表的 winChance 和信任主线的 matchRate 是同一个公式', () => {
    const s = newGame(6);
    s.signed = true;
    s.teamId = 'RNG';
    s.year = 1;
    s.week = 2;
    const fixture = fixtureThisWeek(s);
    expect(fixture).not.toBeNull();
    expect(winChance(s, fixture!.rivalId)).toBeCloseTo(
      matchRate(s, rivalStrength(1, fixture!.rivalId)),
      9,
    );
    // 信任 40 是支点；抬到 90，两条线一起涨同一个系数。
    s.coachTrust = 90;
    expect(winChance(s, fixture!.rivalId)).toBeCloseTo(
      matchRate(s, rivalStrength(1, fixture!.rivalId)),
      9,
    );
    expect(winChance(s, fixture!.rivalId)).toBeGreaterThan(0.5);
  });

  it('E01 的对手不再写死 60，按当周对手算', () => {
    const s = newGame(7);
    s.signed = true;
    s.teamId = 'RNG';
    s.year = 1;
    s.week = 4;
    const e01 = EVENTS.find((e) => e.id === 'E01')!;
    expect(e01.opponent).toBeUndefined();
    const option = e01.options[0]!;
    expect(successRateOf(s, e01, option)).toBeCloseTo(
      matchRate(s, opponentStrength(s), option.bonus ?? 0),
      9,
    );
    expect(opponentStrength(s)).toBeCloseTo(rivalStrength(1, fixtureThisWeek(s)!.rivalId), 9);
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

  it('段位看分档表', () => {
    expect(rankTier(0).name).toBe('黑铁');
    expect(rankTier(400).name).toBe('青铜');
    expect(rankTier(2800).name).toBe('大师');
    expect(rankTier(4500).name).toBe('王者');
    expect(rankTier(9999).name).toBe('王者');
  });

  it('最高档还要名次：分数到王者但名次不够就封在宗师', () => {
    expect(rankOf(9999, 1).name).toBe('王者');
    expect(rankOf(9999, 5000).name).toBe('宗师');
    expect(rankOf(2800, 5000).name).toBe('大师');
  });

  it('上分收益按档位递减', () => {
    expect(weeklyGain(0)).toBe(CONFIG.rank.perWeek.start);
    expect(weeklyGain(4500)).toBeLessThan(weeklyGain(0));
    expect(weeklyGain(9999)).toBe(Math.round(CONFIG.rank.perWeek.start * CONFIG.rank.perWeek.keep));
  });

  it('名次是确定性算出来的：同样的分数与周数永远同一个名次', () => {
    const a = placementOf(2800, 0);
    expect(placementOf(2800, 0)).toBe(a);
    expect(placementOf(9999, 0)).toBeLessThan(a);
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

  it('特殊事件在随机池里按 1:10 抽出', () => {
    let special = 0;
    const total = 4000;
    for (let i = 0; i < total; i++) {
      const s = newGame(i + 1);
      s.year = 1;
      s.week = 10;
      s.rngState = (i * 2654435761) >>> 0;
      const r = drawEvent(s);
      if (r.event?.id === 'E04') special++;
    }
    const ratio = special / total;
    expect(ratio).toBeGreaterThan(0.02);
    expect(ratio).toBeLessThan(0.08);
  });
});

describe('出场判定', () => {
  it('未签约不上场', () => {
    const s = newGame(1);
    s.week = 5;
    expect(canPlay(s)).toBe(false);
  });

  it('伤病到 3 赛季报销', () => {
    const s = newGame(1);
    s.week = 5;
    s.signed = true;
    s.injury = 3;
    expect(canPlay(s)).toBe(false);
  });

  it('伤病到 2 就上不了场，1 还能打', () => {
    const s = newGame(1);
    s.week = 5;
    s.signed = true;
    s.coachTrust = CONFIG.match.benchThreshold + 30;
    s.injury = 1;
    expect(canPlay(s)).toBe(true);
    s.injury = 2;
    expect(canPlay(s)).toBe(false);
    expect(benchReason(s)).toContain('上不了场');
  });

  it('教练信任低于替补线不上场，高于则能打', () => {
    const s = newGame(1);
    s.week = 5;
    s.signed = true;
    s.injury = 0;
    s.coachTrust = CONFIG.match.benchThreshold - 1;
    expect(canPlay(s)).toBe(false);
    s.coachTrust = CONFIG.match.benchThreshold + 5;
    expect(canPlay(s)).toBe(true);
  });

  it('休赛期没有比赛', () => {
    const s = newGame(1);
    s.week = 28;
    s.signed = true;
    expect(canPlay(s)).toBe(false);
  });
});

describe('动作接口', () => {
  it('未知槽位不会写坏状态', () => {
    const s = newGame(1);
    const r = reduce(s, { kind: 'selectAction', slot: 9, action: 'rank' } as Action).state;
    expect(r.actionGrid).toEqual([null, null, null]);
  });
});


describe('段位与邀请函', () => {
  /** 排三格然后结周。 */
  function planWeek(s: GameState, actions: ('rank' | 'rest')[]): GameState {
    let next = s;
    for (let i = 0; i < 3; i++) {
      next = reduce(next, { kind: 'selectAction', slot: i, action: actions[i] ?? 'rest' }).state;
    }
    return reduce(next, { kind: 'endWeek' }).state;
  }

  it('一次上分涨的正好是当前档位的收益', () => {
    let s = newGame(7);
    const before = s.rankPoints;
    const gain = weeklyGain(before);
    s = reduce(s, { kind: 'selectAction', slot: 0, action: 'rank' }).state;
    s = reduce(s, { kind: 'selectAction', slot: 1, action: 'rest' }).state;
    s = reduce(s, { kind: 'selectAction', slot: 2, action: 'rest' }).state;
    s = reduce(s, { kind: 'endWeek' }).state;
    while (s.pendingEvent) s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(s.rankPoints).toBe(before + gain);
    expect(s.placement).toBeGreaterThan(0);
  });

  it('三格没排满不能结周', () => {
    const s = newGame(11);
    const r = reduce(s, { kind: 'endWeek' });
    expect(r.state.week).toBe(1);
    expect(r.state.actionGrid.some((id) => id === null)).toBe(true);
    expect(r.log.some((e) => e.text.includes('三个行动点'))).toBe(true);
  });

  it('清空格子后可以重排', () => {
    let s = newGame(12);
    s = reduce(s, { kind: 'selectAction', slot: 0, action: 'rank' }).state;
    s = reduce(s, { kind: 'clearSlot', slot: 0 }).state;
    expect(s.actionGrid[0]).toBeNull();
    s = reduce(s, { kind: 'selectAction', slot: 0, action: 'rest' }).state;
    expect(s.actionGrid[0]).toBe('rest');
  });

  it('这周没上分，名次被榜上的人超过', () => {
    let s = newGame(13);
    s.week = 5;
    const before = s.placement;
    s = planWeek(s, ['rest', 'rest', 'rest']);
    while (s.pendingEvent) s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(s.rankPoints).toBe(newGame(13).rankPoints);
    expect(s.placement).toBeGreaterThan(before);
  });

  it('到王者，签约窗口必定收到邀请函', () => {
    let s = newGame(14);
    s.year = 1;
    s.week = CONFIG.career.signingWindowWeek;
    // 名次是按分数与周数重算的；给一个远高于榜上任何人的分数才能稳住前 200。
    s.rankPoints = 60000;
    s = planWeek(s, ['rest', 'rest', 'rest']);
    while (s.pendingEvent) s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(s.signed).toBe(true);
  });

  it('没到王者且第 1 年，不计数也不终结', () => {
    let s = newGame(15);
    s.year = 1;
    s.week = CONFIG.career.signingWindowWeek;
    s.rankPoints = 0;
    s = planWeek(s, ['rest', 'rest', 'rest']);
    while (s.pendingEvent) s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(s.signed).toBe(false);
    expect(s.failedWindows).toBe(0);
    expect(s.ended).toBeNull();
  });
});


describe('统一胜负公式', () => {
  it('比赛事件按 (六维均值 − 对手) ÷ 50 + 加成 算胜率', () => {
    const s = newGame(21);
    for (const key of MATCH_ATTRS) s.attrs[key] = 70;
    const event = {
      id: 'X',
      kind: 'match',
      phase: 'growth',
      opponent: 65,
      text: '',
      options: [{ label: 'x', risk: 'roll', bonus: 0 }],
    } as unknown as GameEvent;
    expect(successRateOf(s, event, event.options[0]!)).toBeCloseTo(0.6, 5);

    const buffed = {
      ...event,
      options: [{ label: 'x', risk: 'roll', bonus: 0.3 }],
    } as unknown as GameEvent;
    expect(successRateOf(s, buffed, buffed.options[0]!)).toBeCloseTo(0.9, 5);
  });

  it('胜率被夹在 5%~95%', () => {
    const s = newGame(22);
    for (const key of MATCH_ATTRS) s.attrs[key] = 100;
    const strong = { id:'Y', kind:'match', phase:'growth', opponent: 0, text:'', options:[{label:'x',risk:'roll',bonus:0}] } as unknown as GameEvent;
    expect(successRateOf(s, strong, strong.options[0]!)).toBe(0.95);

    const weak = newGame(23);
    for (const key of MATCH_ATTRS) weak.attrs[key] = 0;
    const hard = { id:'Z', kind:'match', phase:'growth', opponent: 100, text:'', options:[{label:'x',risk:'roll',bonus:0}] } as unknown as GameEvent;
    expect(successRateOf(weak, hard, hard.options[0]!)).toBe(0.05);
  });
});

describe('春决 / 夏决', () => {
  it('只有签约之后才会在决赛周出现', () => {
    const unsigned = newGame(31);
    unsigned.week = CONFIG.league.springFinalWeek;
    expect(drawEvent(unsigned).event?.id).not.toBe('SPR-1');

    const signed = newGame(31);
    signed.signed = true;
    signed.week = CONFIG.league.springFinalWeek;
    expect(drawEvent(signed).event?.id).toBe('SPR-1');
  });

  it('夏决在第 30 周，且按年编号不重复', () => {
    const s = newGame(32);
    s.signed = true;
    s.week = CONFIG.league.summerFinalWeek;
    expect(drawEvent(s).event?.id).toBe('SUM-1');

    s.year = 3;
    s.week = CONFIG.league.summerFinalWeek;
    expect(drawEvent(s).event?.id).toBe('SUM-3');
  });

  it('赢了给联赛冠军', () => {
    const s = newGame(33);
    s.signed = true;
    s.week = CONFIG.league.springFinalWeek;
    for (const key of MATCH_ATTRS) s.attrs[key] = 100;
    const ev = drawEvent(s).event!;
    s.pendingEvent = { eventId: ev.id };
    const after = reduce(s, { kind: 'chooseOption', option: 1 }).state;
    expect(after.honors.map((h) => h.id)).toContain('lpl-champion');
  });
});

describe('邀请函', () => {
  it('到王者那一周触发，接受就直接签约', () => {
    const s = newGame(41);
    s.signed = false;
    s.rankPoints = 4830;
    s.placement = 1;
    s.year = 1;
    s.week = 5;
    const ev = drawEvent(s).event!;
    expect(ev.id).toBe('INV-1');
    s.pendingEvent = { eventId: ev.id };
    const after = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(after.signed).toBe(true);
  });

  it('没到王者不触发', () => {
    const s = newGame(42);
    s.signed = false;
    s.rankPoints = 4515;
    s.placement = 521;
    s.year = 1;
    s.week = 5;
    expect(drawEvent(s).event?.id).not.toBe('INV-1');
  });
});

describe('首发：信任 × 对位差距', () => {
  it('信任刚过 60 且你不弱于同位置，能首发', () => {
    const s = newGame(41);
    s.signed = true;
    s.teamId = 'RNG';
    s.coachTrust = 61;
    for (const key of MATCH_ATTRS) s.attrs[key] = 95; // 均值 95，远强于 Xiaohu 87
    expect(startRequirement(s).ok).toBe(true);
  });

  it('弱 3 点就要 63 点信任：61 不够，64 可以', () => {
    const s = newGame(42);
    s.signed = true;
    s.teamId = 'RNG';
    for (const key of MATCH_ATTRS) s.attrs[key] = 84; // 均值 84，Xiaohu 87 → 差 3
    s.coachTrust = 61;
    expect(startRequirement(s).needTrust).toBe(63);
    expect(isStarting(s)).toBe(false);
    s.coachTrust = 64;
    expect(isStarting(s)).toBe(true);
  });

  it('弱超过 10 点，信任再高也上不了', () => {
    const s = newGame(43);
    s.signed = true;
    s.teamId = 'RNG';
    for (const key of MATCH_ATTRS) s.attrs[key] = 70; // 差 17
    s.coachTrust = 100;
    expect(startRequirement(s).gap).toBeGreaterThan(10);
    expect(isStarting(s)).toBe(false);
  });
});

// ---- 商店 ----

function richState(money = 20000): GameState {
  const s = newGame(20260101, '阿呆', 'MID');
  s.money = money;
  return s;
}

describe('商店', () => {
  it('买断类：扣钱、进 owned、效果立刻生效', () => {
    const s = richState();
    const before = s.money;
    const item = SHOP.find((i) => i.id === 'streamGear')!;
    expect(buyBlocker(s, item)).toBeNull();
    buy(s, 'streamGear');

    expect(s.money).toBe(before - item.price);
    expect(hasOnce(s, 'streamGear')).toBe(true);
    expect(streamIncome(s)).toBe(CONFIG.shop.streamGear.money);
    // 再买一次会被挡住
    expect(buyBlocker(s, item)).toBe('已经买了');
  });

  it('外设让训练多涨 1 点', () => {
    const plain = richState();
    const withPc = richState();
    buy(withPc, 'peripherals');
    expect(trainGain(withPc, 'operation')).toBe(trainGain(plain, 'operation') + CONFIG.shop.peripherals.trainBonus);
  });

  it('年费类：买到明年底，今年都有效', () => {
    const s = richState();
    buy(s, 'trainer');
    expect(subActive(s, 'trainer')).toBe(true);
    expect(subUntil(s, 'trainer')).toBe(2);
    expect(restBonus(s)).toBe(CONFIG.shop.trainer.restBonus);
    // 同样的年费不能重复买
    expect(buyBlocker(s, SHOP.find((i) => i.id === 'trainer')!)).toContain('已买到');
  });

  it('钱不够就买不了', () => {
    const s = richState(100);
    const item = SHOP.find((i) => i.id === 'residence')!;
    expect(buyBlocker(s, item)).toBe('钱不够');
  });

  it('康复只能治有伤的人', () => {
    const s = richState();
    expect(buyBlocker(s, SHOP.find((i) => i.id === 'clinic')!)).toBe('没伤可治');
    s.injury = 2;
    buy(s, 'clinic');
    expect(s.injury).toBe(1);
  });

  it('买了就记一笔支出，收入也会进流水', () => {
    const s = richState();
    buy(s, 'residence');
    expect(s.ledger[s.ledger.length - 1]?.amount).toBe(-CONFIG.shop.residence.price);
    applyAction(s, 'stream', null);
    expect(s.ledger[s.ledger.length - 1]).toEqual({ label: '直播', amount: CONFIG.actions.stream.money });
    expect(weekIncome(s)).toBe(CONFIG.actions.stream.money);
    expect(weekSpend(s)).toBe(-CONFIG.shop.residence.price);
  });
});
