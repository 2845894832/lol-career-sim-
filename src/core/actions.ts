import { CONFIG } from '../config';
import { ATTR_LABEL, DECLINE_ATTRS, type ActionId, type AttrKey, type GameState } from '../types';
import { applyAttrDelta, gainExp } from './growth';
import { createRng } from '../rng';
import { FEEDBACK } from '../data/feedback';
import { clamp, rankExpMultiplier } from './state';
import { placementOf, rankOf, weeklyGain, weeksPlayed } from './ladder';

export interface ActionInfo {
  label: string;
  /** 预期收益的短说明，界面上直接显示。 */
  hint: string;
  /** 需要签约才能用。 */
  needsContract: boolean;
}

export const ACTION_INFO: Record<ActionId, ActionInfo> = {
  rank: { label: '上分', hint: '操作/对线/团战/意识 ↑，累积段位', needsContract: false },
  train: { label: '专项训练', hint: '指定一项 ↑（比上分集中）', needsContract: false },
  review: { label: '复盘录像', hint: '意识 ↑，便宜稳定', needsContract: false },
  scrim: { label: '训练赛', hint: '团战/意识 ↑，教练信任 +', needsContract: true },
  fitness: { label: '健身', hint: '体力上限 ↑', needsContract: false },
  stream: { label: '直播', hint: '金钱 ↑，人气 ↑', needsContract: false },
  business: { label: '商业活动', hint: '金钱 ↑↑，人气 ↑，更耗体力', needsContract: true },
  rest: { label: '休息', hint: '恢复体力', needsContract: false },
};

export function staminaCost(action: ActionId): number {
  switch (action) {
    case 'rank':
      return CONFIG.actions.rank.stamina;
    case 'train':
      return CONFIG.actions.train.stamina;
    case 'review':
      return CONFIG.actions.review.stamina;
    case 'scrim':
      return CONFIG.actions.scrim.stamina;
    case 'fitness':
      return CONFIG.actions.fitness.stamina;
    case 'stream':
      return CONFIG.actions.stream.stamina;
    case 'business':
      return CONFIG.actions.business.stamina;
    case 'rest':
      return CONFIG.actions.rest.stamina;
  }
}

/** 未签约时训练赛与商业活动不出现在选项里。 */
export function isActionUnlocked(state: GameState, action: ActionId): boolean {
  return !ACTION_INFO[action].needsContract || state.signed;
}

/** 本周还剩下的体力（扣掉已排的格子）。 */
export function remainingStamina(state: GameState, ignoreSlot = -1): number {
  let spent = 0;
  for (let i = 0; i < state.actionGrid.length; i++) {
    if (i === ignoreSlot) continue;
    const action = state.actionGrid[i];
    if (action) spent += staminaCost(action);
  }
  return state.stamina - spent;
}

/**
 * 这一格能不能付得起这个行动。
 * 体力不够支付时，该格只能选休息——UI 用这个把别的按钮禁掉。
 */
export function canAfford(state: GameState, slot: number, action: ActionId): boolean {
  if (action === 'rest') return true;
  return remainingStamina(state, slot) >= staminaCost(action);
}

/** 人气增长有递减：越高越难涨，避免一直直播就把人气顶满。 */
function gainPopularity(state: GameState, base: number): number {
  const factor = 1 - state.attrs.popularity / CONFIG.attrs.cap;
  const delta = Math.round(base * factor);
  if (delta <= 0) return 0;
  return applyAttrDelta(state, 'popularity', delta);
}

/** 从反馈池里抽一句；池子空就退回原来的固定文案。 */
function say(state: GameState, action: ActionId, fallback: string): string {
  const pool = FEEDBACK[action];
  if (!pool || pool.length === 0) return fallback;
  const ctx = createRng(state.rngState);
  const line = pool[ctx.rng.int(pool.length)] ?? fallback;
  state.rngState = ctx.state();
  return line;
}

/** 执行一个行动，返回给玩家看的反馈行。 */
export function applyAction(
  state: GameState,
  action: ActionId,
  target: AttrKey | null | undefined,
): string[] {
  const logs: string[] = [];

  switch (action) {
    case 'rank': {
      const mult = rankExpMultiplier(state);
      for (const key of DECLINE_ATTRS) {
        gainExp(state, key, Math.round(CONFIG.actions.rank.exp[key] * mult));
      }
      // 一周打包的排位：收益按当前档位递减，档位越高涨得越慢。
      const gained = weeklyGain(state.rankPoints);
      // 不封顶：封顶之后名次就成了死局，谁到 9999 都是并列。
      state.rankPoints += gained;
      state.placement = placementOf(state.rankPoints, weeksPlayed(state.year, state.week));
      const tier = rankOf(state.rankPoints, state.placement);
      logs.push(`你上分了，现在是${tier.name}，第 ${state.placement} 名。`);
      logs.push(say(state, 'rank', '这一周都在排位。'));
      break;
    }
    case 'train': {
      const key = target ?? 'operation';
      gainExp(state, key, CONFIG.actions.train.exp);
      logs.push(say(state, 'train', `这一周只练${ATTR_LABEL[key]}。`));
      break;
    }
    case 'review':
      gainExp(state, 'awareness', CONFIG.actions.review.exp.awareness);
      logs.push(say(state, 'review', '你逐帧看了自己的团战，越看越沉默。'));
      break;
    case 'scrim':
      gainExp(state, 'teamfight', CONFIG.actions.scrim.exp.teamfight);
      gainExp(state, 'awareness', CONFIG.actions.scrim.exp.awareness);
      state.coachTrust = clamp(state.coachTrust + CONFIG.actions.scrim.coachTrust, 0, 100);
      logs.push(say(state, 'scrim', '训练赛打完，教练在本子上记了两笔。'));
      break;
    case 'fitness':
      state.maxStamina = clamp(
        state.maxStamina + CONFIG.actions.fitness.maxStamina,
        0,
        CONFIG.actions.fitness.maxStaminaCap,
      );
      logs.push(say(state, 'fitness', '你去了健身房，第二天楼梯都下不了。'));
      break;
    case 'stream':
      state.money += CONFIG.actions.stream.money;
      gainPopularity(state, CONFIG.actions.stream.popularity);
      logs.push(say(state, 'stream', '直播间飘过一句「不去打职业扬名立万」。'));
      break;
    case 'business':
      state.money += CONFIG.actions.business.money;
      gainPopularity(state, CONFIG.actions.business.popularity);
      logs.push(say(state, 'business', '商业活动结束，你记不清自己笑了多少次。'));
      break;
    case 'rest':
      state.stamina = clamp(state.stamina + CONFIG.actions.rest.restore, 0, state.maxStamina);
      logs.push(say(state, 'rest', '你睡了一整天。'));
      break;
  }

  return logs;
}
