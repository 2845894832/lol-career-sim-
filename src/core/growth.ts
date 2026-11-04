import { CONFIG } from '../config';
import { type AttrKey, type GameState, type Phase } from '../types';
import { clamp, phaseOfYear } from './state';

export interface GainResult {
  /** 实际涨了几点（受年上限与 100 封顶约束）。 */
  points: number;
  /** 被年上限吃掉的点数。 */
  capped: number;
}

/** 训练一次，这一维该涨几点：固定基础收益 + 外设加成。 */
import { trainBonus } from './shop';

export function trainGain(state: GameState, key: AttrKey): number {
  void key;
  return CONFIG.attrs.trainGain + trainBonus(state);
}

/** 直接加整数点：练到 100 就停。 */
export function gainPoints(state: GameState, key: AttrKey, amount: number): GainResult {
  const cap = CONFIG.attrs.cap;
  let points = 0;

  if (state.attrs[key] >= cap || amount <= 0) return { points, capped: 0 };

  const want = amount;
  const before = state.attrs[key];
  state.attrs[key] = clamp(before + want, 0, cap);
  points = state.attrs[key] - before;
  state.yearGain[key] += points;
  return { points, capped: want - points };
}

/**
 * 旧的「攒经验换点数」通道，保留给事件与测试调用。
 * 现在没有年度上限，只会撞 100 的硬封顶。
 */
export function gainExp(state: GameState, key: AttrKey, amount: number): GainResult {
  const cap = CONFIG.attrs.cap;
  let points = 0;
  let capped = 0;

  if (state.attrs[key] >= cap || amount <= 0) return { points, capped };

  while (state.exp[key] >= 100 && state.attrs[key] < cap) {
    state.exp[key] -= 100;
    state.attrs[key] += 1;
    state.yearGain[key] += 1;
    points += 1;
  }
  state.exp[key] += amount;
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
    // 四项总和降为 80%，损失平均摊到四项：老的掉得多，年轻的掉得少。
    const keys = ['operation', 'laning', 'teamfight', 'awareness'] as const;
    const total = keys.reduce((sum, key) => sum + state.attrs[key], 0);
    const loss = total * (1 - CONFIG.attrs.declineRatio);
    const each = loss / keys.length;
    let dropped = 0;
    for (const key of keys) {
      const before = state.attrs[key];
      state.attrs[key] = clamp(Math.round(before - each), 0, CONFIG.attrs.cap);
      dropped += before - state.attrs[key];
    }
    if (dropped > 0) {
      logs.push(`身体开始还账了：四项一共掉了 ${dropped} 点，手比脑子慢半拍。`);
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
