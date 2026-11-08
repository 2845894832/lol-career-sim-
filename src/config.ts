/**
 * 所有数值集中在这里。改手感只动这个文件，不碰逻辑。
 * 全部是占位值，等试玩后再调。
 */
export const CONFIG = {
  /** 存档版本；不匹配时安全重开。改成名次制后必须加一。 */
  version: 3,
  storageKey: 'lpl-career-proto',

  career: {
    /** 8 年生涯。 */
    years: 8,
    startAge: 18,
    /** 每年 30 周：24 周联赛 + 第 25 周联赛决赛 + 第 26 周休赛 + 27–30 周 S 赛。 */
    weeksPerYear: 30,
    /** 常规赛与联赛决赛的最晚周；S 赛单独判定。 */
    matchWeeksPerYear: 25,
    /**
     * 切片构建专用：打完这一周就出「切片到此为止」的结算页。
     * 0 = 不截断（正式版）。由 vite define 的 __SLICE_AT__ 注入。
     */
    sliceAtWeek: typeof __SLICE_AT__ === 'number' ? __SLICE_AT__ : 0,
    /** 第 26 周没有比赛，作为签约窗口。 */
    signingWindowWeek: 26,
    /** 第 1 年结束（进入第 2 年）时评最佳新秀。 */
    rookieSeason: 2,
  },

  start: {
    attrMin: 40,
    attrMax: 70,
    popularity: 20,
    maxStamina: 100,
    stamina: 60,
    coachTrust: 40,
    /** 开局就是大师 2800：高分路人王，还没人认识。 */
    rankPoints: 2800,
    money: 0,
  },

  attrs: {
    cap: 100,
    /**
     * 练一次的收益固定 1 点（专训 2 点）。
     * 「越练越慢」不放在收益侧，放在体力成本侧（见 actions.cost），
     * 所以对外看到的永远是整数。
     */
    trainGain: 1,
    /** 衰退期年初：四项总和降为原来的 80%（损失平均摊到四项）。 */
    declineRatio: 0.8,
    /** 每年自然增长的心态。 */
    mentalityGrowth: 2,
    mentalityGrowthDecline: 3,
  },

  /** 商店：只卖条件，不卖属性点与胜利。价格按「一年约 2.6 万」定。 */
  shop: {
    residence: { price: 4000, stamina: 6 },
    peripherals: { price: 5000, trainBonus: 1 },
    streamGear: { price: 3000, money: 600 },
    clinic: { price: 600 },
    trainer: { price: 2000, restBonus: 6 },
    coach: { price: 3500, scrimTrust: 1 },
    sparring: { price: 6000, awarenessBonus: 1 },
    agent: { price: 3000, businessMultiplier: 1.5 },
  },

  /**
   * 每个行动的体力消耗与收益。
   * 四项训练的实际体力 = 基础价 + step × ⌊max(0, 属性 − from) ÷ 10⌋：
   * 属性越高越贵，这是「越练越慢」的唯一来源。
   */
  actions: {
    cost: { from: 40, step: 3 },
    rank: { stamina: 14, gain: { laning: 1, operation: 1 } },
    /** 数字 = 指定一维涨几点。 */
    train: { stamina: 12, gain: 2 },
    review: { stamina: 8, gain: { awareness: 1 } },
    scrim: { stamina: 16, gain: { teamfight: 1, awareness: 1 }, coachTrust: 2 },
    fitness: { stamina: 8, maxStamina: 4, maxStaminaCap: 999 },
    stream: { stamina: 10, money: 400, popularity: 2 },
    business: { stamina: 25, money: 800, popularity: 5 },
    /** 休息按体力上限的比例恢复，所以健身从「纯亏」变成投资。 */
    rest: { stamina: 0, restoreRatio: 0.25 },
  },

  /**
   * 段位：不再靠「点数到了就升」，而是分数 + 名次一起决定。
   * 分档表来自原型调参后的结果（prototype/rank-by-placement.html）。
   * - 每档一条，`at` 是进入这一档所需分数；
   * - 最高档（王者）还要名次进前 kingGate；
   * - 第二档（宗师）要进前 secondGate（6% = 前 600 名）。
   */
  rank: {
    max: 9999,
    tiers: [
      { name: '黑铁', at: 0 },
      { name: '青铜', at: 400 },
      { name: '白银', at: 900 },
      { name: '黄金', at: 1500 },
      { name: '铂金', at: 2100 },
      { name: '翡翠', at: 2500 },
      { name: '钻石', at: 2700 },
      { name: '大师', at: 2800 },
      { name: '宗师', at: 3800 },
      { name: '王者', at: 4500 },
    ],
    /** 上分收益按档位递减：黑铁时每周 900，最高档只剩 35%。 */
    perWeek: { start: 900, keep: 0.35 },
    kingGate: 200,
    secondGate: 0.06,
  },

  /** 榜上对手：不存进存档，由 (序号, 种子) 推出来。 */
  ladder: {
    population: 10000,
    baseLp: 3200,
    spreadLp: 1000,
    baseRate: 250,
    rateSpread: 0.1,
    seed: 20261101,
  },

  /** 联赛：赛程、签约、首发。 */
  league: {
    /** 第 25 周：常规赛前 2 名的单场联赛决赛。 */
    leagueFinalWeek: 25,
    /** 第 26 周休赛；27 周 S 赛小组赛，28/29/30 周八强/四强/决赛。 */
    worldsGroupWeek: 27,
    worldsQuarterfinalWeek: 28,
    worldsSemifinalWeek: 29,
    worldsFinalWeek: 30,
    /** 上王者后给几个邀请。 */
    invitations: 3,
    /** 教练信任超过这个数才首发（底线一）。 */
    startThreshold: 60,
    /** 对位差距（同位置首发 − 你）超过这个数就上不了场，信任再高也不行（底线二）。 */
    maxGap: 10,
  },

  /** 比赛结算。 */
  match: {
    /** 胜率 = 相关属性均值 / 100 + 教练信任修正。 */
    coachTrustFactor: 0.001,
    /** 教练信任 40 视为中性（开局值）。 */
    trustPivot: 40,
    minWinRate: 0.05,
    maxWinRate: 0.95,
    /** 统一胜负公式：胜率 = 0.5 + (六维均值 − 对手) / K + 选项加成。 */
    formulaK: 50,
    /**
     * 对手强度的来源。
     * - 'roster'（正式）：按当季名单的 ovr 真算，见 core/league.ts 的 opponentStrength()。
     * - 'fixed'（仅对比模拟）：回到下面两个手写常量，用来复跑 05 号的新旧对照。
     */
    opponentSource: 'roster' as OpponentSource,
    /** 兜底对手强度：名单缺失，或 opponentSource='fixed' 时用。 */
    opponentDefault: 60,
    /** 兜底的决赛对手强度：同上，只在 opponentSource='fixed' 时生效。 */
    opponentFinal: 78,
    winCoachTrust: 2,
    lossCoachTrust: 4,
    /** 胜场只给人气：属性只来自训练与事件，比赛不给。 */
    winPopularity: 1,
    /** 输比赛有一定概率挂上「手腕不适」，下周由事件 E05 结算伤病。 */
    injuryChance: 0.12,
    /** 伤病上限，到这个数就是赛季报销。 */
    injuryMax: 3,
    /** 伤到这个数就上不了场（还能做别的行动）。 */
    injuryBench: 2,
    /** 替补席与下放的教练信任阈值。 */
    benchThreshold: 25,
    demoteThreshold: 10,
  },

  /** 结周时的自然变化。 */
  weekly: {
    /** 伤病每周有概率好转；不设自然体力恢复，休息是唯一补给。 */
    injuryHealChance: 0.2,
  },

  /** 签约。 */
  signing: {
    /** 段位到王者就必定收到邀请函（判定见 reduce 的签约窗口）；人气不参与签约。 */
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

/** 对手强度来源，见 CONFIG.match.opponentSource。 */
export type OpponentSource = 'roster' | 'fixed';
