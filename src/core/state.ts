import { CONFIG } from '../config';
import { createRng } from '../rng';
import { ATTR_KEYS, type AttrKey, type GameState, type Phase, type Stats } from '../types';

export const clamp = (v: number, lo: number, hi: number): number => (v < lo ? lo : v > hi ? hi : v);

export function emptyStats(value = 0): Stats {
  return {
    operation: value,
    laning: value,
    teamfight: value,
    awareness: value,
    mentality: value,
    popularity: value,
  };
}

/** 状态是纯数据，可以整份复制；reduce 只改副本。 */
export function cloneState(state: GameState): GameState {
  return structuredClone(state) as GameState;
}

/** 成长期 1–2 年、巅峰期 3–6 年、衰退期 7–8 年。 */
export function phaseOfYear(year: number): Phase {
  if (year <= 2) return 'growth';
  if (year <= 6) return 'peak';
  return 'decline';
}

export function ageOf(state: GameState): number {
  return CONFIG.career.startAge + state.year - 1;
}

/** 26 个比赛周之后是休赛期。 */
export function isMatchWeek(week: number): boolean {
  return week <= CONFIG.career.matchWeeksPerYear;
}

export function isSigningWindow(week: number): boolean {
  return week === CONFIG.career.signingWindowWeek;
}

const RANK_TIERS = ['黑铁', '青铜', '白银', '黄金', '铂金', '翡翠', '钻石', '大师', '宗师', '王者'] as const;

export function rankTier(points: number): { name: string; index: number; progress: number } {
  const size = CONFIG.rank.tierSize;
  const index = clamp(Math.floor(points / size), 0, RANK_TIERS.length - 1);
  const base = index * size;
  const progress = clamp((points - base) / size, 0, 1);
  return { name: RANK_TIERS[index] ?? '黑铁', index, progress };
}

/** 段位越高，上分给的经验越多。 */
export function rankExpMultiplier(state: GameState): number {
  return 1 + (state.rankPoints / CONFIG.rank.max) * 0.5;
}

export function newGame(seed: number): GameState {
  const { rng } = createRng(seed);
  const attrs = emptyStats();
  for (const key of ATTR_KEYS) {
    if (key === 'popularity') {
      attrs[key] = CONFIG.start.popularity;
    } else {
      attrs[key] = CONFIG.start.attrMin + rng.int(CONFIG.start.attrMax - CONFIG.start.attrMin + 1);
    }
  }

  return {
    version: CONFIG.version,
    seed,
    rngState: seed,
    year: 1,
    week: 1,
    attrs,
    exp: emptyStats(),
    yearGain: emptyStats(),
    stamina: CONFIG.start.stamina,
    maxStamina: CONFIG.start.maxStamina,
    rankPoints: 0,
    money: CONFIG.start.money,
    injury: 0,
    coachTrust: CONFIG.start.coachTrust,
    honors: [],
    flags: [],
    triggeredEvents: [],
    signed: false,
    freeAgent: false,
    failedWindows: 0,
    actionGrid: [null, null, null],
    actionTargets: [null, null, null],
    pendingEvent: null,
    eventDone: false,
    temp: {},
    log: [{ text: `第 1 周，你 18 岁，坐在训练室的最后一排。`, tone: 'plain' }],
    ended: null,
    retired: false,
    peakYear: 1,
    peakScore: 0,
  };
}

/** 六维总和，结局与统计用。 */
export function attrTotal(state: GameState): number {
  return ATTR_KEYS.reduce((sum, key) => sum + state.attrs[key], 0);
}

export function addFlag(state: GameState, flag: string): void {
  if (!state.flags.includes(flag)) state.flags.push(flag);
}

export function addHonor(state: GameState, honor: GameState['honors'][number]): void {
  if (!state.honors.includes(honor)) state.honors.push(honor);
}

/** 临时加减：只在本场比赛内有效。 */
export function effectiveAttr(state: GameState, key: AttrKey): number {
  return clamp(state.attrs[key] + (state.temp[key] ?? 0), 0, CONFIG.attrs.cap);
}
