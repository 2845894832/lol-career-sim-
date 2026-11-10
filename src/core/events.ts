import { CONFIG } from '../config';
import { createRng } from '../rng';
import { matchRate } from './match';
import { finalOpponentStrength, opponentStrength } from './league';
import { EVENTS, FILLER_EVENTS, findEvent } from '../data/events';
import { finalFor, finalById, inviteEvent, inviteById } from '../data/finals';
import { transferById } from '../data/transfer';
import {
  ATTR_LABEL,
  HONOR_LABEL,
  type Consequence,
  type EventOption,
  type GameEvent,
  type GameState,
  type LogEntry,
} from '../types';
import { applyAttrDelta } from './growth';
import { addFlag, addHonor, clamp, effectiveAttr, phaseOfYear } from './state';

export interface DrawResult {
  event: GameEvent | null;
  rngState: number;
}

/**
 * 必触发事件：写死年份/周的（决赛、邀请函）与带 auto 的，不走抽签。
 * 每年生成的决赛按年编号（E04-3），所以「去重」是逐年生效的。
 */
export function forcedEvent(state: GameState): GameEvent | undefined {
  const final = finalFor(state);
  const invite = inviteEvent(state);
  return [...(final ? [final] : []), ...EVENTS, ...(invite ? [invite] : [])].find((e) => {
    // 可重复事件（once: false）不能被 triggeredEvents 永久拉黑。
    if (e.once && state.triggeredEvents.includes(e.id)) return false;
    if (e.year !== undefined && e.year !== state.year) return false;
    if (e.week !== undefined && e.week !== state.week) return false;
    // 既没写年份也没写周次的，只能靠条件触发（如邀请函）
    if (e.year === undefined && e.week === undefined && !e.auto) return false;
    return !e.requires || e.requires(state);
  });
}

/** 随机池：排除写死年份的、填充池的、已触发的一次性事件；比赛事件不占每周事件位。 */
export function randomPool(state: GameState): GameEvent[] {
  const phase = phaseOfYear(state.year);
  return EVENTS.filter(
    (e) =>
      e.year === undefined &&
      !e.filler &&
      !e.auto &&
      e.kind !== 'match' &&
      (e.phase === 'any' || e.phase === phase) &&
      (!e.once || !state.triggeredEvents.includes(e.id)) &&
      (!e.requires || e.requires(state)),
  );
}

/** 比赛事件池：只在赛程里的那场比赛抽，不进每周事件位。 */
export function matchPool(state: GameState): GameEvent[] {
  const phase = phaseOfYear(state.year);
  return EVENTS.filter(
    (e) =>
      e.kind === 'match' &&
      e.year === undefined &&
      !e.filler &&
      !e.auto &&
      (e.phase === 'any' || e.phase === phase) &&
      (!e.once || !state.triggeredEvents.includes(e.id)) &&
      (!e.requires || e.requires(state)),
  );
}

/** 这场比赛抽到的比赛事件；池子空了返回 null。 */
export function drawMatchEvent(state: GameState): DrawResult {
  const ctx = createRng(state.rngState);
  const pool = matchPool(state);
  if (pool.length === 0) return { event: null, rngState: ctx.state() };
  const index = ctx.rng.weighted(pool.map((e) => e.weight));
  const picked = pool[index] ?? null;
  return { event: picked, rngState: ctx.state() };
}

/**
 * 抽本周事件。
 * 顺序：必触发 → 按阶段分桶 → 去掉已触发 → 条件过滤 → 按权重抽 → 空则落回填充池 → 仍空则本周无事件。
 */
export function drawEvent(state: GameState): DrawResult {
  const ctx = createRng(state.rngState);

  // 1. 必触发事件优先。
  const forced = forcedEvent(state);
  if (forced) return { event: forced, rngState: ctx.state() };

  // 2. 随机池。
  const pool = randomPool(state);

  if (pool.length > 0) {
    const index = ctx.rng.weighted(pool.map((e) => e.weight));
    const picked = pool[index];
    if (picked) return { event: picked, rngState: ctx.state() };
  }

  // 3. 兜底：无条件填充池。
  const fillers = FILLER_EVENTS.filter(
    (e) =>
      (!e.once || !state.triggeredEvents.includes(e.id)) && (!e.requires || e.requires(state)),
  );
  if (fillers.length > 0) {
    const index = ctx.rng.int(fillers.length);
    const picked = fillers[index];
    if (picked) return { event: picked, rngState: ctx.state() };
  }

  // 4. 这周就没有事件。
  return { event: null, rngState: ctx.state() };
}

/** 四维：操作 / 对线 / 团战 / 意识（不含心态）。 */
const FOUR_ATTRS = ['operation', 'laning', 'teamfight', 'awareness'] as const;

function fourAvg(state: GameState): number {
  const total = FOUR_ATTRS.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
  return total / FOUR_ATTRS.length;
}

/**
 * 比赛事件里「四维」能加多少胜率。
 * 50 为基准，每高 50 点 +0.2、每低 50 点 −0.2（夹在 ±0.2）。
 * 数值未经用户确认；改这里就改全部 skillBonus 选项。
 */
export function skillBonusOf(state: GameState): number {
  return clamp((fourAvg(state) - CONFIG.attrs.cap / 2) / 250, -0.2, 0.2);
}

/**
 * 比赛事件卡上那一次「这波操作成不成」的成功率：按四维均值算。
 * 和比赛胜负是两次骰子：这一次只决定心态/信任等后果，成功才把选项的
 * 胜率加成带进比赛（见 reduce.ts 的 chooseMatchOption）。
 */
export function matchOptionRate(state: GameState, _option: EventOption): number {
  return clamp(fourAvg(state) / CONFIG.attrs.cap, CONFIG.match.minWinRate, CONFIG.match.maxWinRate);
}

/** 掷骰选项的可见成功率。必成为 1，必败为 0；比赛事件走统一胜负公式。 */
export function successRateOf(state: GameState, event: GameEvent, option: EventOption): number {
  if (option.risk === 'success') return 1;
  if (option.risk === 'fail') return 0;
  if (event.kind === 'match' || event.opponent !== undefined) {
    // 决赛：当季最强队。其它比赛事件：这一周的对手（赛程对手 / 当季平均）。
    // event.opponent 只剩「还没接名单的事件」和 fixed 模式的决赛兜底；E01 已改成按当周对手算。
    const opponent =
      event.opponentRole === 'final'
        ? finalOpponentStrength(state.year, event.opponent ?? CONFIG.match.opponentFinal)
        : event.opponent ?? opponentStrength(state);
    const bonus = (option.bonus ?? 0) + (option.skillBonus ? skillBonusOf(state) : 0);
    return matchRate(state, opponent, bonus);
  }
  let avg: number;
  if (option.mix === 'fourAndPopularity') {
    avg = (fourAvg(state) + effectiveAttr(state, 'popularity')) / 2;
  } else {
    const attrs = option.attrs ?? ['teamfight'];
    const total = attrs.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
    avg = total / attrs.length;
  }
  return clamp(avg / CONFIG.attrs.cap, CONFIG.match.minWinRate, CONFIG.match.maxWinRate);
}

const CONSEQUENCE_TEXT: Record<string, string> = {
  stamina: '体力',
  maxStamina: '体力上限',
  money: '金钱',
  injury: '伤病',
  coachTrust: '教练信任',
};

/** 把一条后果写进状态，并生成「落在哪个数值上」的说明。 */
export function applyConsequence(state: GameState, c: Consequence): string[] {
  const notes: string[] = [];

  if (c.attrs) {
    for (const [key, delta] of Object.entries(c.attrs) as [keyof typeof ATTR_LABEL, number][]) {
      const actual = applyAttrDelta(state, key, delta);
      if (actual !== 0) notes.push(`${ATTR_LABEL[key]} ${actual > 0 ? '+' : ''}${actual}`);
    }
  }
  if (c.temp) {
    for (const [key, delta] of Object.entries(c.temp) as [keyof typeof ATTR_LABEL, number][]) {
      state.temp[key] = (state.temp[key] ?? 0) + delta;
      notes.push(`${ATTR_LABEL[key]} 本场 ${delta > 0 ? '+' : ''}${delta}`);
    }
  }
  if (c.stamina !== undefined) {
    state.stamina = clamp(state.stamina + c.stamina, 0, state.maxStamina);
    notes.push(`${CONSEQUENCE_TEXT.stamina} ${c.stamina > 0 ? '+' : ''}${c.stamina}`);
  }
  if (c.maxStamina !== undefined) {
    state.maxStamina = clamp(
      state.maxStamina + c.maxStamina,
      0,
      CONFIG.actions.fitness.maxStaminaCap,
    );
    notes.push(`${CONSEQUENCE_TEXT.maxStamina} ${c.maxStamina > 0 ? '+' : ''}${c.maxStamina}`);
  }
  if (c.money !== undefined) {
    state.money = Math.max(0, state.money + c.money);
    notes.push(`${CONSEQUENCE_TEXT.money} ${c.money > 0 ? '+' : ''}${c.money}`);
  }
  if (c.injury !== undefined) {
    state.injury = clamp(state.injury + c.injury, 0, CONFIG.match.injuryMax);
    notes.push(`${CONSEQUENCE_TEXT.injury} ${c.injury > 0 ? '+' : ''}${c.injury}`);
  }
  if (c.coachTrust !== undefined) {
    state.coachTrust = clamp(state.coachTrust + c.coachTrust, 0, 100);
    notes.push(`${CONSEQUENCE_TEXT.coachTrust} ${c.coachTrust > 0 ? '+' : ''}${c.coachTrust}`);
  }
  if (c.honor) {
    addHonor(state, c.honor);
    notes.push(`获得${HONOR_LABEL[c.honor]}`);
  }
  if (c.flag) {
    addFlag(state, c.flag);
    notes.push(`标记「${c.flag}」`);
  }
  if (c.clearFlag) {
    state.flags = state.flags.filter((f) => f !== c.clearFlag);
    notes.push(`标记「${c.clearFlag.replace(/^#/, '')}」解除`);
  }
  if (c.teamId) {
    state.teamId = c.teamId;
    notes.push(`加入 ${c.teamId}`);
  }
  if (c.contract) {
    const term = c.contract;
    state.teamId = term.teamId;
    state.signed = true;
    addFlag(state, '#签约');
    if (term.resetTrust) {
      state.coachTrust = CONFIG.transfer.trustAfterTransfer;
      notes.push(`教练信任重置到 ${CONFIG.transfer.trustAfterTransfer}`);
    }
    state.money += term.fee;
    state.contractYear = term.startYear;
    state.freeAgent = false;
  }
  if (c.signed && !state.signed) {
    state.signed = true;
    // 首签没有合同年字段，就按「签到当年」算；之后每年跨年谈一次。
    state.contractYear = state.year;
    addFlag(state, '#签约');
    notes.push('你签约了');
  }

  return notes;
}

export interface OptionOutcome {
  success: boolean;
  logs: LogEntry[];
  /** 比赛事件的胜负；非比赛事件为 null。 */
  win: boolean | null;
  /** 选完接着弹的下一张卡（转会窗 → 主动申请）；没有就是 undefined。 */
  nextEventId?: string;
}

export function resolveOption(
  state: GameState,
  event: GameEvent,
  index: number,
  opts?: { skillRoll?: boolean },
): OptionOutcome {
  const option = event.options[index];
  const logs: LogEntry[] = [];
  if (!option) return { success: false, logs, win: null };

  const ctx = createRng(state.rngState);
  let success: boolean;
  if (option.risk === 'success') {
    success = true;
  } else if (option.risk === 'fail') {
    success = false;
  } else if (opts?.skillRoll && event.kind === 'match') {
    success = ctx.rng.next() < matchOptionRate(state, option);
  } else {
    success = ctx.rng.next() < successRateOf(state, event, option);
  }
  state.rngState = ctx.state();

  const consequence = success ? option.success : option.fail;
  const text = success ? option.successText : option.failText;

  if (text) logs.push({ text, tone: success ? 'good' : 'bad' });
  if (consequence) {
    const notes = applyConsequence(state, consequence);
    if (notes.length > 0) logs.push({ text: notes.join('，'), tone: success ? 'good' : 'bad' });
  }

  let win: boolean | null = null;
  if (event.kind === 'match') {
    win = option.matchResult ? (option.matchResult === 'win') === success : success;
  } else if (event.kind === 'special' && option.matchResult) {
    // 特殊事件可以同时是比赛事件（如决赛）。
    win = (option.matchResult === 'win') === success;
  }

  state.triggeredEvents.push(event.id);
  state.eventDone = true;
  state.pendingEvent = null;

  return { success, logs, win, nextEventId: option.nextEvent };
}

export function getEvent(id: string, state?: GameState): GameEvent | undefined {
  return findEvent(id) ?? finalById(id) ?? inviteById(id) ?? (state ? transferById(id, state) ?? undefined : undefined);
}
