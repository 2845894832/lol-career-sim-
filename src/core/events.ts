import { CONFIG } from '../config';
import { createRng } from '../rng';
import { EVENTS, FILLER_EVENTS, findEvent } from '../data/events';
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
import { addFlag, addHonor, clamp, effectiveAttr, isMatchWeek, phaseOfYear } from './state';

export interface DrawResult {
  event: GameEvent | null;
  rngState: number;
}

/**
 * 抽本周事件。
 * 顺序：必触发 → 按阶段分桶 → 去掉已触发 → 条件过滤 → 按权重抽 → 空则落回填充池 → 仍空则本周无事件。
 */
export function drawEvent(state: GameState): DrawResult {
  const ctx = createRng(state.rngState);

  // 1. 写死年份/周的必触发事件（决赛、签约等），不走抽签。
  const forced = EVENTS.find(
    (e) =>
      e.year === state.year &&
      (e.week === undefined || e.week === state.week) &&
      !state.triggeredEvents.includes(e.id),
  );
  if (forced) return { event: forced, rngState: ctx.state() };

  // 2. 随机池：排除写死年份的、填充池的；比赛事件只在本周有比赛时出现。
  const phase = phaseOfYear(state.year);
  const pool = EVENTS.filter(
    (e) =>
      e.year === undefined &&
      !e.filler &&
      (e.phase === 'any' || e.phase === phase) &&
      (e.kind !== 'match' || isMatchWeek(state.week)) &&
      (!e.once || !state.triggeredEvents.includes(e.id)) &&
      (!e.requires || e.requires(state)),
  );

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

/** 掷骰选项的可见成功率。必成为 1，必败为 0。 */
export function successRateOf(state: GameState, option: EventOption): number {
  if (option.risk === 'success') return 1;
  if (option.risk === 'fail') return 0;
  const attrs = option.attrs ?? ['teamfight'];
  const total = attrs.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
  const avg = total / attrs.length;
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
    state.maxStamina = clamp(state.maxStamina + c.maxStamina, 0, 999);
    notes.push(`${CONSEQUENCE_TEXT.maxStamina} ${c.maxStamina > 0 ? '+' : ''}${c.maxStamina}`);
  }
  if (c.money !== undefined) {
    state.money = Math.max(0, state.money + c.money);
    notes.push(`${CONSEQUENCE_TEXT.money} ${c.money > 0 ? '+' : ''}${c.money}`);
  }
  if (c.injury !== undefined) {
    state.injury = clamp(state.injury + c.injury, 0, 3);
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

  return notes;
}

export interface OptionOutcome {
  success: boolean;
  logs: LogEntry[];
  /** 比赛事件的胜负；非比赛事件为 null。 */
  win: boolean | null;
}

export function resolveOption(state: GameState, event: GameEvent, index: number): OptionOutcome {
  const option = event.options[index];
  const logs: LogEntry[] = [];
  if (!option) return { success: false, logs, win: null };

  const ctx = createRng(state.rngState);
  let success: boolean;
  if (option.risk === 'success') {
    success = true;
  } else if (option.risk === 'fail') {
    success = false;
  } else {
    success = ctx.rng.next() < successRateOf(state, option);
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

  return { success, logs, win };
}

export function getEvent(id: string): GameEvent | undefined {
  return findEvent(id);
}
