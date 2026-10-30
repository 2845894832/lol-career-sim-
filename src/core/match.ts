import { CONFIG } from '../config';
import { createRng } from '../rng';
import { type GameState, type LogEntry, DECLINE_ATTRS, MATCH_ATTRS } from '../types';
import { gainExp } from './growth';
import { clamp, effectiveAttr, isMatchWeek } from './state';

/** 能不能上场：签约、伤病、教练信任、是否在比赛周。 */
export function canPlay(state: GameState): boolean {
  if (!isMatchWeek(state.week)) return false;
  if (!state.signed) return false;
  if (state.injury >= CONFIG.match.injuryMax) return false;
  if (state.coachTrust < CONFIG.match.benchThreshold) return false;
  return true;
}

/** 没上场时的说明；返回 null 表示不必解释（比如还在路人期）。 */
export function benchReason(state: GameState): string | null {
  if (!state.signed) return null;
  if (state.injury >= CONFIG.match.injuryMax) return '你伤停了，这赛季剩下的时间都在康复室。';
  if (state.coachTrust < CONFIG.match.demoteThreshold) return '你被下放了，没有比赛可打。';
  if (state.coachTrust < CONFIG.match.benchThreshold) return '你坐替补席，看完了整场。';
  return null;
}

/**
 * 自动比赛：没有比赛事件时也照常打一场。
 * 读的是「当前有效值」——事件给的临场加减在这里生效。
 */
export function autoMatch(state: GameState): { win: boolean; logs: LogEntry[] } {
  const ctx = createRng(state.rngState);
  const total = MATCH_ATTRS.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
  const avg = total / MATCH_ATTRS.length;
  const trustBonus = (state.coachTrust - CONFIG.match.trustPivot) * CONFIG.match.coachTrustFactor;
  const rate = clamp(avg / CONFIG.attrs.cap + trustBonus, CONFIG.match.minWinRate, CONFIG.match.maxWinRate);
  const win = ctx.rng.next() < rate;
  state.rngState = ctx.state();
  return { win, logs: [] };
}

/** 把一场比赛的胜负写进状态。 */
export function applyMatchOutcome(state: GameState, win: boolean, isFinal: boolean): LogEntry[] {
  const logs: LogEntry[] = [];
  const ctx = createRng(state.rngState);

  if (win) {
    state.coachTrust = clamp(state.coachTrust + CONFIG.match.winCoachTrust, 0, 100);
    state.attrs.popularity = clamp(state.attrs.popularity + CONFIG.match.winPopularity, 0, 100);
    for (const key of DECLINE_ATTRS) {
      gainExp(state, key, CONFIG.match.winExp[key]);
    }
    logs.push({ text: '赢了。', tone: 'good' });
  } else {
    state.coachTrust = clamp(state.coachTrust - CONFIG.match.lossCoachTrust, 0, 100);
    if (ctx.rng.next() < CONFIG.match.injuryChance) {
      state.injury = clamp(state.injury + 1, 0, CONFIG.match.injuryMax);
      logs.push({ text: '输了，而且你的手腕又响了。', tone: 'bad' });
    } else {
      logs.push({ text: '输了。', tone: 'bad' });
    }
  }
  state.rngState = ctx.state();

  if (isFinal && win) {
    state.honors.push('worlds-champion');
    logs.push({ text: '你捧起了 S 赛奖杯。', tone: 'good' });
  }
  if (isFinal && !win) {
    logs.push({ text: '决赛的灯灭了，你站在台上看别人捧杯。', tone: 'bad' });
  }

  return logs;
}
