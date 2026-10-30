import { CONFIG } from '../config';
import { randomSeed } from '../rng';
import type { Action, AttrKey, GameState, LogEntry, ReduceResult } from '../types';
import { applyAction, canAfford, isActionUnlocked, staminaCost } from './actions';
import { advanceYear } from './growth';
import { applyMatchOutcome, autoMatch, benchReason, canPlay } from './match';
import { drawEvent, getEvent, resolveOption } from './events';
import { normalEnding, specialEnding } from './endings';
import { attrTotal, cloneState, isMatchWeek, isSigningWindow, newGame } from './state';

/** 那场决赛：第 3 年 S 赛。 */
export function isFinalWeek(state: GameState): boolean {
  return state.year === 3 && state.week === CONFIG.career.finalWeek;
}

/**
 * 规则核心。纯计算：给一个状态和一个动作，返回新状态和日志。
 * 不读界面、不碰存储、不自己取随机数。
 */
export function reduce(prev: GameState, action: Action): ReduceResult {
  if (action.kind === 'reset') {
    return { state: newGame(randomSeed()), log: ['新的生涯。'] };
  }
  if (prev.ended) {
    return { state: prev, log: ['生涯已经结束了。'] };
  }

  const state = cloneState(prev);
  const out: LogEntry[] = [];

  switch (action.kind) {
    case 'selectAction':
      selectAction(state, action.slot, action.action, action.target, out);
      break;
    case 'chooseOption':
      chooseOption(state, action.option, out);
      break;
    case 'endWeek':
      endWeek(state, out);
      break;
    case 'retire':
      retire(state, out);
      break;
    case 'skipYear':
      skipYear(state, out);
      break;
  }

  if (out.length > 0) {
    state.log = [...state.log, ...out].slice(-60);
  }

  return { state, log: out.map((e) => e.text) };
}

function selectAction(
  state: GameState,
  slot: number,
  id: Parameters<typeof staminaCost>[0],
  target: AttrKey | null | undefined,
  out: LogEntry[],
): void {
  if (slot < 0 || slot > 2) {
    out.push({ text: '这一格不存在。', tone: 'plain' });
    return;
  }
  if (state.pendingEvent) {
    out.push({ text: '先把这周的事件处理掉。', tone: 'plain' });
    return;
  }
  if (!isActionUnlocked(state, id)) {
    out.push({ text: '还没签约，用不了这个。', tone: 'plain' });
    return;
  }

  let chosen = id;
  if (!canAfford(state, slot, id)) {
    chosen = 'rest';
    out.push({ text: '体力不够，这一格只能安排休息。', tone: 'plain' });
  }

  state.actionGrid[slot] = chosen;
  state.actionTargets[slot] = chosen === 'train' ? (target ?? 'operation') : null;
}

function endWeek(state: GameState, out: LogEntry[]): void {
  if (state.pendingEvent) {
    out.push({ text: '先把这周的事件处理掉。', tone: 'plain' });
    return;
  }

  // 没排的格子自动补休息。
  for (let i = 0; i < 3; i++) {
    if (!state.actionGrid[i]) {
      state.actionGrid[i] = 'rest';
      state.actionTargets[i] = null;
    }
  }

  // 三格依次结算，先扣体力再执行。
  for (let i = 0; i < 3; i++) {
    const id = state.actionGrid[i];
    if (!id) continue;
    state.stamina = Math.max(0, state.stamina - staminaCost(id));
    const lines = applyAction(state, id, state.actionTargets[i]);
    out.push(...lines.map((text) => ({ text, tone: 'plain' as const })));
  }

  // 抽一个事件；有事件就等玩家选，没有就照常比赛结周。
  const drawn = drawEvent(state);
  state.rngState = drawn.rngState;
  if (drawn.event) {
    state.pendingEvent = {
      eventId: drawn.event.id,
      isMatch: drawn.event.kind === 'match',
    };
    out.push({ text: `【事件】${drawn.event.text}`, tone: 'plain' });
    return;
  }

  state.eventDone = true;
  settleMatch(state, null, out);
  finishWeek(state, out);
}

function chooseOption(state: GameState, index: number, out: LogEntry[]): void {
  if (!state.pendingEvent) {
    out.push({ text: '这周没有待选的事件。', tone: 'plain' });
    return;
  }
  const event = getEvent(state.pendingEvent.eventId);
  if (!event) {
    state.pendingEvent = null;
    state.eventDone = true;
    settleMatch(state, null, out);
    finishWeek(state, out);
    return;
  }

  const outcome = resolveOption(state, event, index);
  out.push(...outcome.logs);

  if (outcome.win !== null) {
    out.push(...applyMatchOutcome(state, outcome.win, isFinalWeek(state)));
  } else {
    settleMatch(state, null, out);
  }

  finishWeek(state, out);
}

/** 有比赛事件时用事件结果；否则照常自动打一场。 */
function settleMatch(state: GameState, forcedWin: boolean | null, out: LogEntry[]): void {
  if (forcedWin !== null) {
    out.push(...applyMatchOutcome(state, forcedWin, isFinalWeek(state)));
    return;
  }
  if (!isMatchWeek(state.week)) return;
  if (!canPlay(state)) {
    const reason = benchReason(state);
    if (reason) out.push({ text: reason, tone: 'plain' });
    return;
  }
  const { win } = autoMatch(state);
  out.push(...applyMatchOutcome(state, win, isFinalWeek(state)));
}

function resolveSigningWindow(state: GameState, out: LogEntry[]): void {
  if (state.signed) return;

  // 第 1 年只是路人期，不计数。
  if (state.year <= 1) {
    state.freeAgent = true;
    return;
  }

  const hasTrial = state.flags.includes('试训通过');
  const qualified =
    hasTrial ||
    state.attrs.popularity >= CONFIG.signing.popularityNeeded ||
    state.rankPoints >= CONFIG.signing.rankPointsNeeded;

  if (qualified) {
    state.signed = true;
    state.freeAgent = false;
    state.failedWindows = 0;
    out.push({ text: '有队伍给了你一份合同。你签字的时候手有点抖。', tone: 'good' });
    return;
  }

  state.failedWindows += 1;
  state.freeAgent = true;
  if (state.failedWindows >= CONFIG.signing.failedWindowsToEnd) {
    state.ended = specialEnding(state);
    out.push({ text: '第二个窗口，还是没有消息。', tone: 'bad' });
  } else {
    out.push({ text: '这个窗口没人找你。你成了自由人，还能等。', tone: 'bad' });
  }
}

function finishWeek(state: GameState, out: LogEntry[]): void {
  // 临场加减只在当场有效。
  state.temp = {};

  state.stamina = Math.min(state.maxStamina, state.stamina + CONFIG.weekly.staminaRegen);

  if (isSigningWindow(state.week)) resolveSigningWindow(state, out);
  if (state.ended) return;

  state.actionGrid = [null, null, null];
  state.actionTargets = [null, null, null];
  state.eventDone = false;
  state.matchDone = false;
  state.pendingEvent = null;

  if (state.week >= CONFIG.career.weeksPerYear) {
    state.week = 1;
    state.year += 1;

    if (state.year > CONFIG.career.years) {
      state.year = CONFIG.career.years;
      state.ended = normalEnding(state, 'expired');
      out.push({ text: '八年过去了。', tone: 'plain' });
      return;
    }

    out.push(...advanceYear(state).map((text) => ({ text, tone: 'plain' as const })));
    const total = attrTotal(state);
    if (total > state.peakScore) {
      state.peakScore = total;
      state.peakYear = state.year;
    }
    if (state.year === 2) {
      state.honors.push('rookie-of-year');
      out.push({ text: '赛季末，你拿了最佳新秀。', tone: 'good' });
    }
  } else {
    state.week += 1;
  }
}

function retire(state: GameState, out: LogEntry[]): void {
  state.retired = true;
  state.ended = normalEnding(state, 'retired');
  out.push({ text: '你发了条微博：「退役了，谢谢大家。」', tone: 'plain' });
}

function skipYear(state: GameState, out: LogEntry[]): void {
  if (state.pendingEvent) {
    out.push({ text: '先把这周的事件处理掉。', tone: 'plain' });
    return;
  }
  state.year += 1;
  state.week = 1;
  state.actionGrid = [null, null, null];
  state.actionTargets = [null, null, null];
  state.eventDone = false;
  state.matchDone = false;

  if (state.year > CONFIG.career.years) {
    state.ended = normalEnding(state, 'expired');
    out.push({ text: '八年过去了。', tone: 'plain' });
    return;
  }

  out.push(...advanceYear(state).map((text) => ({ text, tone: 'plain' as const })));
  out.push({ text: `跳到第 ${state.year} 年。`, tone: 'plain' });
}
