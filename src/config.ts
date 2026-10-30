/**
 * 所有数值集中在这里。改手感只动这个文件，不碰逻辑。
 * 全部是占位值，等试玩后再调。
 */
export const CONFIG = {
  /** 存档版本；不匹配时安全重开。 */
  version: 1,
  storageKey: 'lpl-career-proto',

  career: {
    /** 8 年生涯。 */
    years: 8,
    startAge: 18,
    /** 每年 26 个比赛周 + 4 个休赛期周。 */
    weeksPerYear: 30,
    matchWeeksPerYear: 26,
    /** 休赛期最后一周是签约窗口。 */
    signingWindowWeek: 30,
    /** 每年 S 赛决赛周。 */
    finalWeek: 26,
  },

  start: {
    attrMin: 40,
    attrMax: 70,
    popularity: 20,
    maxStamina: 100,
    stamina: 60,
    coachTrust: 50,
    money: 0,
  },

  attrs: {
    cap: 100,
    /** 涨到下一级所需经验 = base + slope × 当前值。 */
    expBase: 24,
    expSlope: 1.4,
    /** 每项每年最多涨多少点真值。 */
    yearGainCap: { growth: 8, peak: 6, decline: 2 },
    /** 衰退期每年掉点（只掉四项）。 */
    declineDrop: 3,
    /** 每年自然增长的心态。 */
    mentalityGrowth: 2,
    mentalityGrowthDecline: 3,
  },

  /** 每个行动的体力消耗与收益。 */
  actions: {
    rank: { stamina: 12, rankPoints: 26, exp: { operation: 6, laning: 6, teamfight: 6, awareness: 6 } },
    train: { stamina: 10, exp: 14 },
    review: { stamina: 6, exp: { awareness: 10 } },
    scrim: { stamina: 14, exp: { teamfight: 8, awareness: 8 }, coachTrust: 1 },
    fitness: { stamina: 8, maxStamina: 4, maxStaminaCap: 150 },
    stream: { stamina: 10, money: 90, popularity: 3 },
    business: { stamina: 18, money: 320, popularity: 5 },
    rest: { stamina: 0, restore: 18 },
  },

  /** 段位：十档，每档 1000 点。 */
  rank: { max: 9999, tierSize: 1000 },

  /** 比赛结算。 */
  match: {
    /** 胜率 = 相关属性均值 / 100 + 教练信任修正。 */
    coachTrustFactor: 0.001,
    minWinRate: 0.05,
    maxWinRate: 0.95,
    winCoachTrust: 3,
    lossCoachTrust: 4,
    /** 胜场人气与经验。 */
    winPopularity: 1,
    winExp: { operation: 4, laning: 4, teamfight: 4, awareness: 4 },
    /** 输比赛有一定概率受伤。 */
    injuryChance: 0.12,
    /** 替补席与下放的教练信任阈值。 */
    benchThreshold: 25,
    demoteThreshold: 10,
  },

  /** 结周时的自然恢复。 */
  weekly: {
    staminaRegen: 8,
    injuryHealChance: 0.2,
  },

  /** 签约。 */
  signing: {
    /** 有试训标记时必签；否则看人气与段位。 */
    popularityNeeded: 35,
    rankPointsNeeded: 600,
    /** 连续几个窗口无人可签就终结。 */
    failedWindowsToEnd: 2,
  },

  /** 事件抽取。 */
  events: {
    specialWeight: 1,
    normalWeight: 10,
    textMaxLength: 50,
  },
} as const;

export type PhaseConfigKey = 'growth' | 'peak' | 'decline';
