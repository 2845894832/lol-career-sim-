import type { GameState, LogEntry } from '../types';
import { isStarting, myOvr, myPlace } from './league';
import { addHonor, hasHonor, hasHonorThisYear } from './state';

/** 名人堂门槛：荣誉总数与至少一个 S 冠军。 */
const HALL_OF_FAME_HONORS = 8;

/**
 * 第 25 周联赛决赛前结算常规赛荣誉。
 * 只发一次：同一年重复调用不会重复写入。
 */
export function awardSeasonHonors(state: GameState): LogEntry[] {
  const out: LogEntry[] = [];
  if (!state.signed || !isStarting(state) || myPlace(state) <= 0 || myPlace(state) > 4) {
    return out;
  }

  const ovr = myOvr(state);
  if (ovr >= 85 && !hasHonorThisYear(state, 'season-mvp')) {
    addHonor(state, 'season-mvp');
    out.push({ text: '赛季末，你当选常规赛 MVP。', tone: 'good' });
  }
  if (ovr >= 82 && !hasHonorThisYear(state, 'all-pro')) {
    addHonor(state, 'all-pro');
    out.push({ text: '你入选了赛季最佳阵容。', tone: 'good' });
  }
  return out;
}

/** 退役或第 8 年到期时结算一次名人堂。 */
export function awardHallOfFame(state: GameState): LogEntry[] {
  if (hasHonor(state, 'hall-of-fame')) return [];
  if (state.honors.length < HALL_OF_FAME_HONORS) return [];
  if (!hasHonor(state, 'worlds-champion')) return [];

  addHonor(state, 'hall-of-fame');
  return [{ text: '你入选了名人堂。', tone: 'good' }];
}
