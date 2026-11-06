import { CONFIG } from '../config';
import { clamp } from './state';

/**
 * 唯一的胜率公式。
 *
 * p = 0.5 +（我方强度 − 对手强度）÷ formulaK + 临场加成 + 教练信任微调，
 * 最后夹在 minWinRate–maxWinRate（5%–95%）。
 *
 * matchRate（信任主线那一场）和 winChance（赛程/积分榜）都只从这里出数；
 * 以前两个文件各写了一份，分母写死 50，改 config 也改不动另一份。
 */
export function winProbability(
  mine: number,
  opponent: number,
  bonus = 0,
  coachTrust: number = CONFIG.match.trustPivot,
): number {
  const trustBonus = (coachTrust - CONFIG.match.trustPivot) * CONFIG.match.coachTrustFactor;
  const p = 0.5 + (mine - opponent) / CONFIG.match.formulaK + bonus + trustBonus;
  return clamp(p, CONFIG.match.minWinRate, CONFIG.match.maxWinRate);
}
