import { describe, expect, it } from 'vitest';
import { CONFIG } from '../src/config';
import { isStarting, startRequirement, fixtureThisWeek, finalOpponentStrength, leagueWeeksFor, opponentStrength, rivalStrength, seasonAverageStrength, seasonStrengths, seasonTopStrength, nextFixture, winChance, scheduleFor } from '../src/core/league';
import { reduce } from '../src/core/reduce';
import { staminaCost } from '../src/core/actions';
import { applyAction, canAfford } from '../src/core/actions';
import { advanceYear, gainExp, gainPoints, trainGain } from '../src/core/growth';
import { autoMatch, applyMatchOutcome, matchRate } from '../src/core/match';
import { normalEnding, specialEnding } from '../src/core/endings';
import { drawEvent, forcedEvent, getEvent, matchPool, randomPool, resolveOption, successRateOf } from '../src/core/events';
import { EVENTS } from '../src/data/events';
import { canPlay, benchReason } from '../src/core/match';
import { createRng } from '../src/rng';
import { fromSaveJson, toSaveJson } from '../src/core/save';
import { loadSaved, persist } from '../src/core/save';
import { newGame, rankTier } from '../src/core/state';
import { placementOf, rankOf, weeklyGain } from '../src/core/ladder';
import { ATTR_KEYS, HONOR_LABEL, MATCH_ATTRS, type Action, type GameEvent, type GameState } from '../src/types';
import { SHOP, buy, buyBlocker, hasOnce, restBonus, streamIncome, subActive, subUntil, weekIncome, weekSpend } from '../src/core/shop';
import { leagueFinal, worldsFinal } from '../src/data/finals';
import { awardHallOfFame, awardSeasonHonors } from '../src/core/honors';
import { applicationOffers, signingFee, transferEvent, transferOffers } from '../src/data/transfer';
import { teamInYear } from '../src/data/teamIdentity';

/** 造一个第 25 周的联赛决赛选手：13 胜、首发、五维 90。 */
function makeLeagueFinalist(seed = 33): GameState {
  const s = newGame(seed);
  s.signed = true;
  s.teamId = 'RNG';
  s.coachTrust = 100;
  s.week = CONFIG.league.leagueFinalWeek;
  for (const key of MATCH_ATTRS) s.attrs[key] = 90;
  s.seasonResults = Array.from({ length: 13 }, (_, i) => ({
    year: 1,
    week: 2 + i,
    rivalId: 'EDG',
    won: true,
    kind: 'regular' as const,
  }));
  return s;
}

/** 造一个第 30 周的 S 赛决赛选手。 */
function makeWorldsFinalist(seed = 34): GameState {
  const s = newGame(seed);
  s.signed = true;
  s.teamId = 'RNG';
  s.coachTrust = 100;
  s.week = CONFIG.league.worldsFinalWeek;
  s.year = 1;
  s.flags = ['#S决赛-1'];
  for (const key of MATCH_ATTRS) s.attrs[key] = 90;
  return s;
}

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
  // 比赛：开赛 → 比赛事件卡 → 演出 → 继续
  guard = 0;
  while (s.pendingMatch && guard++ < 4) {
    const phase = s.pendingMatch.phase;
    if (phase === 'kickoff') s = reduce(s, { kind: 'kickoffMatch' }).state;
    else if (phase === 'event') s = reduce(s, { kind: 'chooseMatchOption', option: 0 }).state;
    else s = reduce(s, { kind: 'finishMatch' }).state;
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

  it('伤停 ≥1 会触发 E05，结算后伤停 +1 并清掉手腕标记', () => {
    const s = newGame(1);
    s.signed = true;
    s.week = 10;
    s.injury = 1;
    s.flags.push('#手腕不适');
    const drawn = drawEvent(s);
    expect(drawn.event?.id).toBe('E05');
    resolveOption(s, drawn.event!, 0);
    expect(s.injury).toBe(2);
    expect(s.flags).not.toContain('#手腕不适');
    // once：整局只结算一次，避免伤停期间每周复发。
    expect(drawEvent(s).event?.id).not.toBe('E05');
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
    for (let w = 1; w <= CONFIG.career.weeksPerYear; w++) {
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

    s.year = 1;
    s.week = CONFIG.league.worldsFinalWeek;
    s.flags = ['#S决赛-1'];
    expect(opponentStrength(s)).toBeCloseTo(seasonTopStrength(1), 6);
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
    const event = leagueFinal(1);
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
      s.year = 1;
      s.week = CONFIG.league.worldsFinalWeek;
      s.flags = ['#S决赛-1'];
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

describe('四维加成与必成选项', () => {
  it('E02 试训成功率 =（四维平均 + 人气）÷ 2 ÷ 100', () => {
    const s = newGame(9);
    s.signed = false;
    s.attrs.operation = 80;
    s.attrs.laning = 60;
    s.attrs.teamfight = 70;
    s.attrs.awareness = 50;
    s.attrs.popularity = 40;
    const e02 = EVENTS.find((e) => e.id === 'E02')!;
    const trial = e02.options.find((o) => o.label === '去试训')!;
    expect(trial.mix).toBe('fourAndPopularity');
    expect(successRateOf(s, e02, trial)).toBeCloseTo(((65 + 40) / 2) / 100, 6);
  });

  it('S 赛决赛选项按当季最强队算', () => {
    const s = makeWorldsFinalist(10);
    const event = worldsFinal(1);
    const option = event.options[0]!;
    expect(successRateOf(s, event, option)).toBeCloseTo(
      matchRate(s, seasonTopStrength(1), option.bonus ?? 0),
      6,
    );
  });

  it('必成/必败选项不带掷骰属性', () => {
    for (const event of EVENTS) {
      for (const option of event.options) {
        if (option.risk === 'roll') continue;
        expect(option.attrs, `${event.id} ${option.label}`).toBeUndefined();
      }
    }
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

  it('第 25 周联赛决赛必出 LPL 事件', () => {
    const s = makeLeagueFinalist(1);
    expect(drawEvent(s).event?.id).toBe('LPL-1');
  });

  it('第 30 周 S 决赛必出 WF 事件', () => {
    const s = makeWorldsFinalist(1);
    expect(drawEvent(s).event?.id).toBe('WF-1');
  });

  it('第 26 周休赛期抽不到比赛事件', () => {
    const s = newGame(3);
    s.week = 26;
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

  it('特殊事件在池里按权重占比抽出', () => {
    const s = newGame(1);
    s.year = 1;
    s.week = 10;
    s.signed = true;
    const pool = randomPool(s);
    const special = pool.find((e) => e.id === 'E04');
    expect(special).toBeDefined();
    const totalWeight = pool.reduce((sum, e) => sum + e.weight, 0);
    const share = (special?.weight ?? 0) / totalWeight;

    let hit = 0;
    const total = 4000;
    for (let i = 0; i < total; i++) {
      const t = newGame(i + 1);
      t.year = 1;
      t.week = 10;
      t.signed = true;
      t.rngState = (i * 2654435761) >>> 0;
      const r = drawEvent(t);
      if (r.event?.id === 'E04') hit++;
    }
    const expected = total * share;
    const sigma = Math.sqrt(total * share * (1 - share));
    expect(Math.abs(hit - expected)).toBeLessThan(4 * sigma + 2);
  });

  it('表内事件条数与 ID 规则', () => {
    const ids = EVENTS.filter((e) => /^[MLSPN]\d\d$/.test(e.id)).map((e) => e.id);
    expect(ids).toHaveLength(219);
    expect(new Set(ids).size).toBe(219);
  });

  it('表内事件：正文 ≤50 字、2~3 个选项、后果字段合法', () => {
    const tableEvents = EVENTS.filter((e) => /^[MLSPN]\d\d$/.test(e.id));
    const consKeys = new Set([
      'attrs', 'temp', 'stamina', 'maxStamina', 'money', 'injury',
      'coachTrust', 'honor', 'flag', 'clearFlag', 'signed', 'teamId',
    ]);
    for (const e of tableEvents) {
      expect(e.text.length, e.id).toBeLessThanOrEqual(CONFIG.events.textMaxLength);
      expect(e.options.length, e.id).toBeGreaterThanOrEqual(2);
      expect(e.options.length, e.id).toBeLessThanOrEqual(3);
      expect(['match', 'life', 'special'], e.id).toContain(e.kind);
      for (const o of e.options) {
        expect(['roll', 'success', 'fail'], e.id).toContain(o.risk);
        for (const c of [o.success, o.fail]) {
          if (!c) continue;
          for (const key of Object.keys(c)) expect(consKeys.has(key), `${e.id} ${key}`).toBe(true);
          for (const key of Object.keys(c.attrs ?? {})) expect(ATTR_KEYS).toContain(key);
          for (const key of Object.keys(c.temp ?? {})) expect(ATTR_KEYS).toContain(key);
        }
        if (o.fail) expect(o.failText?.length ?? 0, `${e.id} ${o.label}`).toBeGreaterThan(0);
      }
    }
  });

  it('每条表内事件都存在能抽到它的状态（随机池或必触发）', () => {
    const reachable = new Set<string>();
    const weeks = [1, 5, 10, 20, 26, 30];
    const flagSets: string[][] = [
      [],
      ['#五十块'],
      ['#坐过替补'],
      ['#手腕不适'],
      ['#偷家'],
      ['#让二追三'],
      ['#丢龙'],
      ['#金句'],
      ['#自嘲'],
      ['#转教练'],
    ];
    for (let year = 1; year <= 8; year++) {
      for (const week of weeks) {
        for (const signed of [false, true]) {
          for (const injury of [0, 1]) {
            for (const trust of [0, 50, 100]) {
              for (const pop of [0, 60]) {
                for (const flags of flagSets) {
                  const s = newGame(1);
                  s.year = year;
                  s.week = week;
                  s.signed = signed;
                  s.injury = injury;
                  s.coachTrust = trust;
                  s.attrs.popularity = pop;
                  s.flags = flags;
                  s.honors = [{ id: 'lpl-champion', year }];
                  s.actionGrid = ['stream', null, null] as GameState['actionGrid'];
                  for (const e of randomPool(s)) reachable.add(e.id);
                  for (const e of matchPool(s)) reachable.add(e.id);
                  const f = forcedEvent(s);
                  if (f) reachable.add(f.id);
                }
              }
            }
          }
        }
      }
    }
    // 决赛按年编号（E05-3），所以按前缀认。
    const ids = [...reachable];
    const missing = EVENTS.filter((e) => !ids.some((id) => id === e.id || id.startsWith(`${e.id}-`))).map(
      (e) => e.id,
    );
    expect(missing).toEqual([]);
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

  it('第 26 周休赛期没有比赛', () => {
    const s = newGame(1);
    s.week = 26;
    s.signed = true;
    expect(canPlay(s)).toBe(false);
  });
});

describe('替补不上场', () => {
  it('没进首发就不弹开赛卡，球队后台打完并记积分榜', () => {
    const s = newGame(3);
    s.signed = true;
    s.teamId = 'RNG';
    const fixture = nextFixture(s);
    expect(fixture).toBeTruthy();
    if (!fixture) throw new Error('no fixture');
    s.week = fixture.week;
    s.coachTrust = CONFIG.match.benchThreshold + 5; // 能上场但不到首发线
    expect(fixtureThisWeek(s)).not.toBeNull();

    let st = s;
    for (let i = 0; i < 3; i++) {
      st = reduce(st, { kind: 'selectAction', slot: i, action: 'rest' }).state;
    }
    st = reduce(st, { kind: 'endWeek' }).state;
    if (st.pendingEvent) st = reduce(st, { kind: 'chooseOption', option: 0 }).state;

    expect(st.pendingMatch).toBeNull();
    expect(st.seasonResults.length).toBe(1);
    expect(st.week).toBe(fixture.week + 1);
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
    s.placement = 1;
    s = planWeek(s, ['rest', 'rest', 'rest']);
    expect(s.pendingEvent?.eventId).toBe('INV-1');
    s = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(s.signed).toBe(true);
    expect(s.teamId).not.toBeNull();
    expect(s.flags).toContain('#签约');
  });

  it('邀请函只有一个「签字进队」选项，必成', () => {
    const s = newGame(20);
    s.signed = false;
    s.year = 1;
    s.week = 5;
    s.rankPoints = 4830;
    s.placement = 1;
    const ev = drawEvent(s).event!;
    expect(ev.id).toBe('INV-1');
    expect(ev.options).toHaveLength(1);
    const opt = ev.options[0]!;
    expect(opt.label).toBe('签字进队');
    expect(opt.risk).toBe('success');
    expect(opt.success?.signed).toBe(true);
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

describe('联赛决赛 / S 赛', () => {
  it('只有前 2 且首发才会打联赛决赛', () => {
    const unsigned = newGame(31);
    unsigned.week = CONFIG.league.leagueFinalWeek;
    expect(drawEvent(unsigned).event?.id).not.toBe('LPL-1');

    const benched = makeLeagueFinalist(31);
    benched.attrs.operation = 0;
    benched.attrs.laning = 0;
    benched.attrs.teamfight = 0;
    benched.attrs.awareness = 0;
    benched.attrs.mentality = 0;
    expect(drawEvent(benched).event?.id).not.toBe('LPL-1');

    expect(drawEvent(makeLeagueFinalist(31)).event?.id).toBe('LPL-1');
  });

  it('联赛决赛按年编号', () => {
    const s = makeLeagueFinalist(32);
    expect(drawEvent(s).event?.id).toBe('LPL-1');
    // 战绩按年隔离：换了年，上一年的 13 胜不算数，得重新打出前 2 名。
    s.year = 3;
    s.seasonResults = s.seasonResults.map((r) => ({ ...r, year: 3 }));
    expect(drawEvent(s).event?.id).toBe('LPL-3');
  });

  it('联赛决赛成功选项写联赛冠军', () => {
    expect(leagueFinal(1).options.some((o) => o.success?.honor === 'lpl-champion')).toBe(true);
  });

  it('S 赛决赛赢下写 S 冠军', () => {
    const s = makeWorldsFinalist(33);
    applyMatchOutcome(s, true, true);
    expect(s.honors.map((h) => h.id)).toContain('worlds-champion');
  });
});

describe('新赛程与荣誉', () => {
  it('联赛周次按当年队数动态铺满 2–24', () => {
    for (let year = 1; year <= CONFIG.career.years; year += 1) {
      const weeks = leagueWeeksFor(year);
      expect(weeks).toHaveLength(seasonStrengths(year).length - 1);
      expect(weeks[0]).toBe(2);
      expect(weeks[weeks.length - 1]).toBe(24);
    }
  });

  it('MSI 荣誉已从标签里删除', () => {
    expect(Object.keys(HONOR_LABEL)).not.toContain('msi-champion');
  });

  it('第 25 周五维 ≥85 拿 MVP + 最佳阵容', () => {
    const s = makeLeagueFinalist(51);
    const logs = awardSeasonHonors(s);
    const ids = s.honors.map((h) => h.id);
    expect(ids).toContain('season-mvp');
    expect(ids).toContain('all-pro');
    expect(logs.length).toBe(2);
    expect(awardSeasonHonors(s)).toEqual([]);
  });

  it('五维 83 只拿最佳阵容', () => {
    const s = makeLeagueFinalist(52);
    for (const key of MATCH_ATTRS) s.attrs[key] = 83;
    awardSeasonHonors(s);
    const ids = s.honors.map((h) => h.id);
    expect(ids).not.toContain('season-mvp');
    expect(ids).toContain('all-pro');
  });

  it('名次不在前 4 不发常规赛荣誉', () => {
    const s = makeLeagueFinalist(53);
    s.seasonResults = [];
    expect(awardSeasonHonors(s)).toEqual([]);
    expect(s.honors).toEqual([]);
  });

  it('荣誉 ≥8 且至少一个 S 冠军才进名人堂，且只进一次', () => {
    const s = makeLeagueFinalist(54);
    s.honors = Array.from({ length: 8 }, (_, i) => ({ id: 'lpl-champion' as const, year: i + 1 }));
    s.honors.push({ id: 'worlds-champion', year: 8 });
    expect(awardHallOfFame(s).length).toBe(1);
    expect(s.honors.map((h) => h.id)).toContain('hall-of-fame');
    expect(awardHallOfFame(s)).toEqual([]);
  });

  it('没有 S 冠军不进名人堂', () => {
    const s = makeLeagueFinalist(55);
    s.honors = Array.from({ length: 8 }, (_, i) => ({ id: 'lpl-champion' as const, year: i + 1 }));
    expect(awardHallOfFame(s)).toEqual([]);
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

describe('转会系统', () => {
  /** 第 30 周的已签约首发：能进任何队的转会窗。 */
  function offerState(seed = 71): GameState {
    const s = newGame(seed);
    s.signed = true;
    s.teamId = 'RNG';
    s.coachTrust = 100;
    s.year = 1;
    s.week = 30;
    s.contractYear = 1;
    for (const k of MATCH_ATTRS) s.attrs[k] = 90;
    return s;
  }

  /** 排三格休息、结周，把随机的本周事件点掉，直到弹出转会卡。 */
  function runWeekToTransfer(s: GameState): GameState {
    let st = s;
    for (let i = 0; i < 3; i++) st = reduce(st, { kind: 'selectAction', slot: i, action: 'rest' }).state;
    st = reduce(st, { kind: 'endWeek' }).state;
    for (let guard = 0; guard < 6 && st.pendingEvent && !st.pendingEvent.eventId.startsWith('TR-'); guard++) {
      st = reduce(st, { kind: 'chooseOption', option: 0 }).state;
    }
    return st;
  }

  it('第 30 周弹转会卡，每个选项都必须落到一支队（没有「都不签」）', () => {
    const s = runWeekToTransfer(offerState());
    expect(s.pendingEvent?.eventId).toBe('TR-2');
    expect(transferEvent(s)?.id).toBe('TR-2');
    const ev = getEvent('TR-2', s)!;
    expect(ev.options.length).toBeGreaterThan(1);
    for (const o of ev.options) {
      if (o.nextEvent) continue;
      expect(o.success?.contract).toBeTruthy();
    }
  });

  it('续约：留队、信任不清零、签字费照发', () => {
    const s = runWeekToTransfer(offerState());
    const fee = signingFee(2, 'RNG');
    const next = reduce(s, { kind: 'chooseOption', option: 0 }).state;
    expect(next.teamId).toBe('RNG');
    expect(next.coachTrust).toBe(100);
    expect(next.contractYear).toBe(2);
    expect(next.money).toBe(s.money + fee);
    expect(next.year).toBe(2);
    expect(next.week).toBe(1);
  });

  it('转会：换队、信任重置 40、签字费到账、战绩清零', () => {
    const s = runWeekToTransfer(offerState());
    const ev = getEvent('TR-2', s)!;
    const contract = ev.options[1]!.success?.contract;
    expect(contract).toBeTruthy();
    expect(contract!.teamId).not.toBe('RNG');
    const next = reduce(s, { kind: 'chooseOption', option: 1 }).state;
    expect(next.teamId).toBe(contract!.teamId);
    expect(next.coachTrust).toBe(CONFIG.transfer.trustAfterTransfer);
    expect(next.contractYear).toBe(2);
    expect(next.money).toBe(s.money + signingFee(2, contract!.teamId));
    expect(next.seasonResults).toEqual([]);
  });

  it('主动申请：走 TRA 卡，只列能首发的队，选中后照样换队', () => {
    const s = runWeekToTransfer(offerState());
    const ev = getEvent('TR-2', s)!;
    const idx = ev.options.findIndex((o) => o.nextEvent);
    expect(idx).toBeGreaterThan(0);
    const asked = reduce(s, { kind: 'chooseOption', option: idx }).state;
    expect(asked.pendingEvent?.eventId).toBe('TRA-2');
    const list = getEvent('TRA-2', asked)!;
    expect(list.options.length).toBeGreaterThan(0);
    for (const o of list.options) expect(o.success?.contract).toBeTruthy();
    const target = list.options[0]!.success!.contract!;
    const next = reduce(asked, { kind: 'chooseOption', option: 0 }).state;
    expect(next.teamId).toBe(target.teamId);
    expect(next.coachTrust).toBe(CONFIG.transfer.trustAfterTransfer);
  });

  it('报价只出 gap≤10 的队；签字费按强度三档', () => {
    const s = offerState();
    const ordered = seasonStrengths(2);
    expect(signingFee(2, ordered[0]!.id)).toBe(CONFIG.transfer.feeStrong);
    expect(signingFee(2, ordered[ordered.length - 1]!.id)).toBe(CONFIG.transfer.feeWeak);
    expect(signingFee(2, ordered[Math.floor(ordered.length / 2)]!.id)).toBe(CONFIG.transfer.feeMid);
    for (const o of transferOffers(s, 2)) expect(o.gap).toBeLessThanOrEqual(CONFIG.league.maxGap);
    for (const o of applicationOffers(s, 2)) expect(o.gap).toBeLessThanOrEqual(CONFIG.league.maxGap);
  });

  it('弱到没有队能首发时，只保底一支弱队（gap 可能超 10，但不会没合同）', () => {
    const s = offerState();
    for (const k of MATCH_ATTRS) s.attrs[k] = 40;
    const offers = transferOffers(s, 2);
    expect(offers.length).toBeGreaterThan(0);
    for (const o of offers) expect(o.gap <= CONFIG.league.maxGap || offers.length === 1).toBe(true);
  });

  it('队名更名跟映射走，RA 在 S15 视为解散', () => {
    // year 1 = S8，year 8 = S15。
    expect(teamInYear('SNG', 2)).toBe('SN');
    expect(teamInYear('SNG', 5)).toBe('WBG');
    expect(teamInYear('RNG', 8)).toBe('RNG');
    expect(teamInYear('RA', 8)).toBeNull();
  });

  it('换年后上一年的 played 不继承，第 2 年常规赛正常打', () => {
    const s = offerState();
    s.seasonResults = [{ year: 1, week: 2, rivalId: 'WE', won: true, kind: 'regular' }];
    s.year = 2;
    expect(scheduleFor(s).every((f) => !f.played)).toBe(true);
    expect(fixtureThisWeek({ ...s, week: 2 })).not.toBeNull();
  });
});
