import { CONFIG } from '../config';
import { createRng } from '../rng';
import { type GameState, type LogEntry, DECLINE_ATTRS, MATCH_ATTRS } from '../types';
import { gainExp } from './growth';
import { myTeamStrength } from './league';
import { clamp, effectiveAttr, isMatchWeek } from './state';

/** 能不能上场：签约、伤病、教练信任、是否在比赛周。 */
export function canPlay(state: GameState): boolean {
  if (!isMatchWeek(state.week)) return false;
  if (!state.signed) return false;
  if (state.injury >= CONFIG.match.injuryBench) return false;
  if (state.coachTrust < CONFIG.match.benchThreshold) return false;
  return true;
}

/** 没上场时的说明；返回 null 表示不必解释（比如还在路人期）。 */
export function benchReason(state: GameState): string | null {
  if (!state.signed) return null;
  if (state.injury >= CONFIG.match.injuryMax) return '你伤停了，这赛季剩下的时间都在康复室。';
  if (state.injury >= CONFIG.match.injuryBench) return '伤到这个程度上不了场，这周只能养。';
  if (state.coachTrust < CONFIG.match.demoteThreshold) return '你被下放了，没有比赛可打。';
  if (state.coachTrust < CONFIG.match.benchThreshold) return '你坐替补席，看完了整场。';
  return null;
}

/**
 * 自动比赛：没有比赛事件时也照常打一场。
 * 读的是「当前有效值」——事件给的临场加减在这里生效。
 */
/**
 * 所有比赛共用的胜率公式。
 * 0.5 +（六维均值 − 对手强度）÷ K + 选项加成 + 教练信任微调，夹在 5%～95%。
 */
export function matchRate(state: GameState, opponent: number, bonus = 0): number {
  const total = MATCH_ATTRS.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
  const solo = total / MATCH_ATTRS.length;
  // 签了约就是全队口径：五个人一起算，替补时算的是场上的五个人。
  const avg = state.signed ? myTeamStrength(state) : solo;
  const trustBonus = (state.coachTrust - CONFIG.match.trustPivot) * CONFIG.match.coachTrustFactor;
  const p = 0.5 + (avg - opponent) / CONFIG.match.formulaK + bonus + trustBonus;
  return clamp(p, CONFIG.match.minWinRate, CONFIG.match.maxWinRate);
}

/** 自动比赛：没有比赛事件时也照常打一场。 */
export function autoMatch(state: GameState, opponent: number): { win: boolean; logs: LogEntry[] } {
  const ctx = createRng(state.rngState);
  const win = ctx.rng.next() < matchRate(state, opponent);
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
