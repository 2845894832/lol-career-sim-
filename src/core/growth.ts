import { CONFIG } from '../config';
import type { AttrKey, GameState, Phase } from '../types';
import { clamp, phaseOfYear } from './state';

/** 涨到下一级所需经验：属性越高越贵。 */
export function expNeeded(attr: number): number {
  return Math.round(CONFIG.attrs.expBase + CONFIG.attrs.expSlope * attr);
}

/** 当前属性距离下一级的进度，界面用。 */
export function expProgress(state: GameState, key: AttrKey): { current: number; needed: number } {
  const needed = expNeeded(state.attrs[key]);
  return { current: Math.min(state.exp[key], needed), needed };
}

export interface GainResult {
  /** 实际涨了几点（受年上限与 100 封顶约束）。 */
  points: number;
  /** 被年上限吃掉的点数。 */
  capped: number;
}

/**
 * 给某项加整数经验，攒够阈值就 +1。
 * 年龄台阶决定每年最多涨多少：成长 8 / 巅峰 6 / 衰退 2。
 */
export function gainExp(state: GameState, key: AttrKey, amount: number): GainResult {
  const cap = CONFIG.attrs.cap;
  const yearCap = CONFIG.attrs.yearGainCap[phaseOfYear(state.year)];
  let points = 0;
  let capped = 0;

  if (state.attrs[key] >= cap || amount <= 0) return { points, capped };

  state.exp[key] += amount;
  while (state.exp[key] >= expNeeded(state.attrs[key])) {
    if (state.attrs[key] >= cap) break;
    if (state.yearGain[key] >= yearCap) {
      capped += 1;
      // 已达年上限：经验不再滚进下一级，避免跨年补涨。
      state.exp[key] = Math.min(state.exp[key], expNeeded(state.attrs[key]) - 1);
      break;
    }
    state.exp[key] -= expNeeded(state.attrs[key]);
    state.attrs[key] += 1;
    state.yearGain[key] += 1;
    points += 1;
  }

  return { points, capped };
}

/** 事件直接加减属性点（不走经验条），结果仍是 0–100 的整数。 */
export function applyAttrDelta(state: GameState, key: AttrKey, delta: number): number {
  const before = state.attrs[key];
  state.attrs[key] = clamp(before + delta, 0, CONFIG.attrs.cap);
  return state.attrs[key] - before;
}

/** 跨年时结算：重置年度涨幅、衰退掉点、心态自然增长。 */
export function advanceYear(state: GameState): string[] {
  const logs: string[] = [];
  const phase = phaseOfYear(state.year);

  if (phase === 'decline') {
    for (const key of ['operation', 'laning', 'teamfight', 'awareness'] as const) {
      const before = state.attrs[key];
      state.attrs[key] = clamp(before - CONFIG.attrs.declineDrop, 0, CONFIG.attrs.cap);
      if (state.attrs[key] !== before) {
        logs.push(`${key} 掉了 ${before - state.attrs[key]} 点——手比脑子慢半拍。`);
      }
    }
  }

  const mentalityGain =
    phase === 'decline' ? CONFIG.attrs.mentalityGrowthDecline : CONFIG.attrs.mentalityGrowth;
  applyAttrDelta(state, 'mentality', mentalityGain);

  for (const key of Object.keys(state.yearGain) as AttrKey[]) {
    state.yearGain[key] = 0;
  }

  return logs;
}

export function phaseLabel(phase: Phase): string {
  return phase === 'growth' ? '成长期' : phase === 'peak' ? '巅峰期' : '衰退期';
}
