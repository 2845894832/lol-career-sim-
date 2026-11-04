import { CONFIG } from '../config';
import { ATTR_LABEL, type ActionId, type AttrKey, type GameState } from '../types';
import { applyAttrDelta, gainPoints, trainGain } from './growth';
import { createRng } from '../rng';
import { FEEDBACK } from '../data/feedback';
import { clamp } from './state';
import { placementOf, rankOf, weeklyGain, weeksPlayed } from './ladder';
import {
  awarenessBonus,
  businessIncome,
  earn,
  restBonus,
  scrimTrustBonus,
  streamIncome,
} from './shop';

export interface ActionInfo {
  label: string;
  /** 预期收益的短说明，界面上直接显示。 */
  hint: string;
  /** 需要签约才能用。 */
  needsContract: boolean;
}

export const ACTION_INFO: Record<ActionId, ActionInfo> = {
  rank: { label: '上分', hint: '对线、操作各 +1；段位分数 ↑', needsContract: false },
  train: { label: '专项训练', hint: '选一维 +2', needsContract: false },
  review: { label: '复盘录像', hint: '意识 +1', needsContract: false },
  scrim: { label: '训练赛', hint: '团战、意识各 +1；信任 +2', needsContract: true },
  fitness: { label: '健身', hint: '体力上限 +4', needsContract: false },
  stream: { label: '直播', hint: '钱 +400、人气 +2', needsContract: false },
  business: { label: '商业活动', hint: '钱 +800、人气 +5', needsContract: true },
  rest: { label: '休息', hint: '按上限的 20% 回体力', needsContract: false },
};

/** 递增成本：属性越高，这一格越贵。 */
function escalate(base: number, value: number): number {
  const { from, step } = CONFIG.actions.cost;
  return base + step * Math.max(0, Math.floor((value - from) / 10));
}

/**
 * 这一格要花多少体力。
 * 四项训练按「这次练的那一维现在多少」算价，所以必须传 state；
 * target 只对专训有意义（练哪一维就按哪一维收费）。
 */
export function staminaCost(
  state: GameState,
  action: ActionId,
  target?: AttrKey | null,
): number {
  const a = state.attrs;
  switch (action) {
    case 'rank':
      return escalate(CONFIG.actions.rank.stamina, Math.min(a.laning, a.operation));
    case 'train': {
      // 不指定这一维时（选项页还没选），报最便宜那一维的价，界面标「起」。
      const v = target
        ? a[target]
        : Math.min(a.operation, a.laning, a.teamfight, a.awareness, a.mentality);
      return escalate(CONFIG.actions.train.stamina, v);
    }
    case 'review':
      return escalate(CONFIG.actions.review.stamina, a.awareness);
    case 'scrim':
      return escalate(CONFIG.actions.scrim.stamina, Math.min(a.teamfight, a.awareness));
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
    if (action) spent += staminaCost(state, action, state.actionTargets[i]);
  }
  return state.stamina - spent;
}

/**
 * 这一格能不能付得起这个行动。
 * 体力不够支付时，该格只能选休息——UI 用这个把别的按钮禁掉。
 */
export function canAfford(state: GameState, slot: number, action: ActionId): boolean {
  if (action === 'rest') return true;
  return remainingStamina(state, slot) >= staminaCost(state, action);
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
      gainPoints(state, 'laning', trainGain(state, 'laning'));
      gainPoints(state, 'operation', trainGain(state, 'operation'));
      // 一周打包的排位：收益按当前档位递减，档位越高涨得越慢。
      const gained = weeklyGain(state.rankPoints);
      // 不封顶：封顶之后名次就成了死局，谁到 9999 都是并列。
      state.rankPoints += gained;
      // 收益和对手在同一周结算：按「本周打完」的周数算名次，否则会先虚高再回落。
      state.placement = placementOf(state.rankPoints, weeksPlayed(state.year, state.week) + 1);
      const tier = rankOf(state.rankPoints, state.placement);
      logs.push(`你上分了，现在是${tier.name}，第 ${state.placement} 名。`);
      logs.push(say(state, 'rank', '这一周都在排位。'));
      break;
    }
    case 'train': {
      const key = target ?? 'operation';
      gainPoints(state, key, trainGain(state, key));
      logs.push(say(state, 'train', `这一周只练${ATTR_LABEL[key]}。`));
      break;
    }
    case 'review':
      gainPoints(state, 'awareness', trainGain(state, 'awareness') + awarenessBonus(state));
      logs.push(say(state, 'review', '你逐帧看了自己的团战，越看越沉默。'));
      break;
    case 'scrim':
      gainPoints(state, 'teamfight', trainGain(state, 'teamfight'));
      gainPoints(state, 'awareness', trainGain(state, 'awareness') + awarenessBonus(state));
      state.coachTrust = clamp(
        state.coachTrust + CONFIG.actions.scrim.coachTrust + scrimTrustBonus(state),
        0,
        100,
      );
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
      earn(state, '直播', streamIncome(state));
      gainPopularity(state, CONFIG.actions.stream.popularity);
      logs.push(say(state, 'stream', '直播间飘过一句「不去打职业扬名立万」。'));
      break;
    case 'business':
      earn(state, '商业活动', businessIncome(state));
      gainPopularity(state, CONFIG.actions.business.popularity);
      logs.push(say(state, 'business', '商业活动结束，你记不清自己笑了多少次。'));
      break;
    case 'rest':
      state.stamina = clamp(
        state.stamina +
          Math.round(state.maxStamina * CONFIG.actions.rest.restoreRatio) +
          restBonus(state),
        0,
        state.maxStamina,
      );
      logs.push(say(state, 'rest', '你睡了一整天。'));
      break;
  }

  return logs;
}
