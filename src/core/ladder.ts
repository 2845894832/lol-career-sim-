import { CONFIG } from '../config';

/**
 * 段位换算成「名次」。
 *
 * 规则来自原型 prototype/rank-by-placement.html：
 * - 榜上有一万个对手，每人有自己的起点和每周增速；
 * - 对手也按段位减速，所以越往上越挤；
 * - 你的名次 = 分数比你高的人数 + 1；
 * - 最高档（王者）要看名次（前 200），第二档看前 1%，其余只看分数。
 *
 * 对手不存进存档：他们的起点与增速由 (序号, 种子) 决定，随时可以重算。
 */

export interface Tier {
  name: string;
  /** 到这个分数算这一档。 */
  at: number;
}

const TIERS = CONFIG.rank.tiers as readonly Tier[];

/** 取第 i 档；越界就退回最后一档。 */
export function tierAt(i: number): Tier {
  const idx = Math.max(0, Math.min(i, TIERS.length - 1));
  return TIERS[idx] as Tier;
}

export function tierCount(): number {
  return TIERS.length;
}

/** 当前分数落在第几档（0 起）。 */
export function tierIndex(lp: number): number {
  let idx = 0;
  for (let i = 0; i < TIERS.length; i++) {
    if (lp >= tierAt(i).at) idx = i;
  }
  return idx;
}

export function tierOf(lp: number): Tier {
  return tierAt(tierIndex(lp));
}

export function tierName(lp: number): string {
  return tierOf(lp).name;
}

/** 分数 + 名次一起决定档位；名次不够就往下压一档。 */
export function rankOf(
  lp: number,
  place: number,
  population: number = CONFIG.ladder.population,
): { name: string; index: number } {
  const top = TIERS.length - 1;
  let idx = tierIndex(lp);

  if (idx >= top && place > CONFIG.rank.kingGate) idx = top - 1;
  else if (idx >= top - 1 && place > population * CONFIG.rank.secondGate) idx = Math.min(idx, top - 2);

  return { name: tierAt(Math.max(0, idx)).name, index: idx };
}

/** 某一档每周能上多少分：档位越高越慢。 */
function gainAt(idx: number, base: number): number {
  const n = Math.max(1, TIERS.length - 1);
  const factor = 1 - (1 - CONFIG.rank.perWeek.keep) * Math.min(idx, n) / n;
  return Math.max(1, Math.round(base * factor));
}

/** 你现在这一档，每周上分会给多少分。 */
export function weeklyGain(lp: number): number {
  return gainAt(tierIndex(lp), CONFIG.rank.perWeek.start);
}

/** 确定性伪随机：同样的 (序号, 种子) 永远得到同一个数。 */
function hash01(i: number, seed: number): number {
  let h = Math.imul(i + 1, 0x9e3779b1) ^ seed;
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/** 第 i 个对手的起点与基础增速。 */
export function rival(i: number): { start: number; rate: number } {
  const a = hash01(i, CONFIG.ladder.seed);
  const b = hash01(i + 50021, CONFIG.ladder.seed);
  const start = CONFIG.ladder.baseLp + (a - 0.5) * 2 * CONFIG.ladder.spreadLp;
  const rate = CONFIG.ladder.baseRate * (1 + (b - 0.5) * 2 * CONFIG.ladder.rateSpread);
  return { start: Math.max(0, Math.round(start)), rate };
}

/** 一个人走了 weeks 周之后的分数；按段位逐档减速。 */
export function advance(lp: number, rate: number, weeks: number): number {
  let cur = lp;
  let left = weeks;

  while (left > 0) {
    const idx = tierIndex(cur);
    const g = gainAt(idx, rate);
    const next: Tier | undefined = TIERS[idx + 1];
    if (!next) {
      cur += g * left;
      break;
    }
    const need = Math.ceil((next.at - cur) / g);
    if (need >= left) {
      cur += g * left;
      break;
    }
    cur = next.at;
    left -= need;
  }

  return cur;
}

const cache = new Map<string, number>();

/** 你在全服排第几（1 起）。结果按 (分数, 周数) 缓存。 */
export function placementOf(lp: number, weeks: number): number {
  const key = `${Math.round(lp)}|${weeks}`;
  const hit = cache.get(key);
  if (hit !== undefined) return hit;

  let ahead = 0;
  for (let i = 0; i < CONFIG.ladder.population; i++) {
    const r = rival(i);
    if (advance(r.start, r.rate, weeks) > lp) ahead += 1;
  }

  const place = ahead + 1;
  if (cache.size > 400) cache.clear();
  cache.set(key, place);
  return place;
}

/** 生涯走到第几周（第 1 年第 1 周 = 0）。 */
export function weeksPlayed(year: number, week: number): number {
  return (year - 1) * CONFIG.career.weeksPerYear + (week - 1);
}
