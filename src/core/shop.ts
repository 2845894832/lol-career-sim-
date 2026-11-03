import { CONFIG } from '../config';
import type { GameState } from '../types';

export type ShopShape = 'once' | 'year' | 'use';

export interface ShopItem {
  id: string;
  label: string;
  effect: string;
  shape: ShopShape;
  price: number;
  /** 需要签约才能买（商业代理、分析师这类队里才给用的东西）。 */
  needsContract?: boolean;
}

/** 商店：每一条的效果都只落在已有状态上，不新增系统。 */
export const SHOP: ShopItem[] = [
  {
    id: 'residence',
    label: '住处升级',
    effect: `每周开始自动恢复 ${CONFIG.shop.residence.stamina} 体力`,
    shape: 'once',
    price: CONFIG.shop.residence.price,
  },
  {
    id: 'peripherals',
    label: '外设',
    effect: `训练类行动额外 +${CONFIG.shop.peripherals.trainBonus} 点`,
    shape: 'once',
    price: CONFIG.shop.peripherals.price,
  },
  {
    id: 'streamGear',
    label: '直播设备',
    effect: `直播收益 ${CONFIG.actions.stream.money} → ${CONFIG.shop.streamGear.money}`,
    shape: 'once',
    price: CONFIG.shop.streamGear.price,
  },
  {
    id: 'clinic',
    label: '康复与医疗',
    effect: '伤病 −1',
    shape: 'use',
    price: CONFIG.shop.clinic.price,
  },
  {
    id: 'trainer',
    label: '体能师',
    effect: `休息恢复 +${CONFIG.shop.trainer.restBonus}（一年）`,
    shape: 'year',
    price: CONFIG.shop.trainer.price,
  },
  {
    id: 'coach',
    label: '私人教练',
    effect: `训练赛额外 +${CONFIG.shop.coach.scrimTrust} 信任（一年）`,
    shape: 'year',
    price: CONFIG.shop.coach.price,
  },
  {
    id: 'sparring',
    label: '陪练团队',
    effect: `复盘与训练赛额外 +${CONFIG.shop.sparring.awarenessBonus} 意识（一年）`,
    shape: 'year',
    price: CONFIG.shop.sparring.price,
  },
  {
    id: 'agent',
    label: '商业代理',
    effect: `商业活动收益 +${Math.round((CONFIG.shop.agent.businessMultiplier - 1) * 100)}%（一年）`,
    shape: 'year',
    price: CONFIG.shop.agent.price,
    needsContract: true,
  },
];

export function itemOf(id: string): ShopItem | undefined {
  return SHOP.find((i) => i.id === id);
}

export function hasOnce(state: GameState, id: string): boolean {
  return state.owned.includes(id);
}

/** 年费买到第几年年底；0 表示没买过。 */
export function subUntil(state: GameState, id: string): number {
  return state.subs.find((s) => s.id === id)?.untilYear ?? 0;
}

export function subActive(state: GameState, id: string): boolean {
  return subUntil(state, id) >= state.year;
}

/* ---------- 收支流水 ---------- */

/** 记一笔收入和支出，第四屏的「本周收支」就是这张表。 */
export function earn(state: GameState, label: string, amount: number): void {
  state.money += amount;
  state.ledger.push({ label, amount });
}

export function spend(state: GameState, label: string, amount: number): void {
  state.money -= amount;
  state.ledger.push({ label, amount: -amount });
}

export function weekIncome(state: GameState): number {
  return state.ledger.filter((e) => e.amount > 0).reduce((a, b) => a + b.amount, 0);
}

export function weekSpend(state: GameState): number {
  return state.ledger.filter((e) => e.amount < 0).reduce((a, b) => a + b.amount, 0);
}

/* ---------- 效果查询（行动与周结算读这里） ---------- */

export function streamIncome(state: GameState): number {
  return hasOnce(state, 'streamGear') ? CONFIG.shop.streamGear.money : CONFIG.actions.stream.money;
}

export function businessIncome(state: GameState): number {
  const base = CONFIG.actions.business.money;
  return subActive(state, 'agent') ? Math.round(base * CONFIG.shop.agent.businessMultiplier) : base;
}

export function trainBonus(state: GameState): number {
  return hasOnce(state, 'peripherals') ? CONFIG.shop.peripherals.trainBonus : 0;
}

export function restBonus(state: GameState): number {
  return subActive(state, 'trainer') ? CONFIG.shop.trainer.restBonus : 0;
}

export function scrimTrustBonus(state: GameState): number {
  return subActive(state, 'coach') ? CONFIG.shop.coach.scrimTrust : 0;
}

export function awarenessBonus(state: GameState): number {
  return subActive(state, 'sparring') ? CONFIG.shop.sparring.awarenessBonus : 0;
}

/** 这条能不能买，返回 null 表示能买。 */
export function buyBlocker(state: GameState, item: ShopItem): string | null {
  if (item.shape === 'once' && hasOnce(state, item.id)) return '已经买了';
  if (item.shape === 'year' && subActive(state, item.id)) return `已买到第 ${subUntil(state, item.id)} 年`;
  if (item.needsContract && !state.signed) return '签约后才能买';
  if (item.id === 'clinic' && state.injury <= 0) return '没伤可治';
  if (state.money < item.price) return '钱不够';
  return null;
}

/** 买一件，返回日志行。调用前先确认 buyBlocker 为 null。 */
export function buy(state: GameState, id: string): string[] {
  const item = itemOf(id);
  if (!item) return [];
  spend(state, item.label, item.price);

  switch (item.shape) {
    case 'once':
      state.owned.push(item.id);
      break;
    case 'year':
      state.subs = state.subs.filter((s) => s.id !== item.id);
      state.subs.push({ id: item.id, untilYear: state.year + 1 });
      break;
    case 'use':
      if (item.id === 'clinic') state.injury = Math.max(0, state.injury - 1);
      break;
  }

  return [`你买了${item.label}，花掉 ${item.price}。`];
}
