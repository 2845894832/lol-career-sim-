import { CONFIG } from '../config';
import { fixtureThisWeek, matchLogLine, myTeamStrength, opponentStrength, recordResult, rivalStrength, winChance } from './league';
import { createRng } from '../rng';
import { hasOnce } from './shop';
import type { Action, ActionId, AttrKey, GameState, LogEntry, ReduceResult } from '../types';
import { applyAction, canAfford, isActionUnlocked, staminaCost } from './actions';
import { advanceYear } from './growth';
import { applyMatchOutcome, autoMatch, benchReason, canPlay } from './match';
import { drawEvent, getEvent, resolveOption } from './events';
import { normalEnding, sliceEnding, specialEnding } from './endings';
import { addHonor, attrTotal, cloneState, isFinalWeek, isMatchWeek, isSigningWindow } from './state';
import { placementOf, rankOf, weeksPlayed } from './ladder';

/**
 * 规则核心。纯计算：给一个状态和一个动作，返回新状态和日志。
 * 不读界面、不碰存储、不自己取随机数。
 */
export function reduce(prev: GameState, action: Action): ReduceResult {
  if (prev.ended) {
    return { state: prev, log: [{ text: '生涯已经结束了。', tone: 'plain' }] };
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
    case 'clearSlot':
      clearSlot(state, action.slot, out);
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

  return { state, log: out };
}

function selectAction(
  state: GameState,
  slot: number,
  id: ActionId,
  target: AttrKey | null | undefined,
  out: LogEntry[],
): void {
  if (slot < 0 || slot > 2) {
    out.push({ text: '这个行动点不存在。', tone: 'plain' });
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
    out.push({ text: '体力不够，这个行动点只能安排休息。', tone: 'plain' });
  }

  state.actionGrid[slot] = chosen;
  state.actionTargets[slot] = chosen === 'train' ? (target ?? 'operation') : null;
}

function clearSlot(state: GameState, slot: number, out: LogEntry[]): void {
  if (slot < 0 || slot > 2) return;
  if (state.pendingEvent) {
    out.push({ text: '先把这周的事件处理掉。', tone: 'plain' });
    return;
  }
  if (!state.actionGrid[slot]) return;
  state.actionGrid[slot] = null;
  state.actionTargets[slot] = null;
  out.push({ text: '这一格清空了，可以重排。', tone: 'plain' });
}

function endWeek(state: GameState, out: LogEntry[]): void {
  if (state.pendingEvent) {
    out.push({ text: '先把这周的事件处理掉。', tone: 'plain' });
    return;
  }

  // 三格必须排满才能结周；没排满就不推进。
  if (state.actionGrid.some((id) => id === null)) {
    out.push({ text: '三个行动点都要排上才能结周。', tone: 'plain' });
    return;
  }

  // 三个行动点依次结算，先扣体力再执行。
  for (let i = 0; i < 3; i++) {
    const id = state.actionGrid[i];
    if (!id) continue;
    state.stamina = Math.max(0, state.stamina - staminaCost(state, id, state.actionTargets[i]));
    const lines = applyAction(state, id, state.actionTargets[i]);
    out.push(...lines.map((text) => ({ text, tone: 'plain' as const })));
  }

  // 抽一个事件；有事件就等玩家选，没有就照常比赛结周。
  const drawn = drawEvent(state);
  state.rngState = drawn.rngState;
  if (drawn.event) {
    state.pendingEvent = { eventId: drawn.event.id };
    out.push({ text: `【事件】${drawn.event.text}`, tone: 'plain' });
    return;
  }

  state.eventDone = true;
  settleMatch(state, out);
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
    settleMatch(state, out);
    finishWeek(state, out);
    return;
  }

  const outcome = resolveOption(state, event, index);
  out.push(...outcome.logs);

  // 比赛事件由选项决定胜负；但伤停/下放/没签约时，这场不该算在你头上。
  if (outcome.win !== null) {
    if (canPlay(state)) {
      out.push(...applyMatchOutcome(state, outcome.win, isFinalWeek(state)));
    } else {
      const reason = benchReason(state);
      if (reason) out.push({ text: reason, tone: 'plain' });
    }
  } else {
    settleMatch(state, out);
  }

  finishWeek(state, out);
}

/** 照常打一场：受伤/下放会跳过，休赛期没有比赛。 */
function settleMatch(state: GameState, out: LogEntry[]): void {
  if (!isMatchWeek(state.week)) return;
  if (!canPlay(state)) {
    const reason = benchReason(state);
    if (reason) out.push({ text: reason, tone: 'plain' });
    return;
  }
  // 对手强度来自当季名单：赛程周是那支队，其余周是当季平均，决赛是当季最强。
  const { win } = autoMatch(state, opponentStrength(state));
  out.push(...applyMatchOutcome(state, win, isFinalWeek(state)));
}

function resolveSigningWindow(state: GameState, out: LogEntry[]): void {
  if (state.signed) return;

  // 王者 = 分数到最高档 + 名次进前 200。到了就必定收到邀请函；人气不参与签约。
  const qualified = rankOf(state.rankPoints, state.placement).index === CONFIG.rank.tiers.length - 1;

  if (qualified) {
    state.signed = true;
    state.freeAgent = false;
    state.failedWindows = 0;
    out.push({ text: '有队伍给了你一份合同。你签字的时候手有点抖。', tone: 'good' });
    return;
  }

  // 第 1 年没到王者只是路人期，不计数。
  if (state.year < CONFIG.career.rookieSeason) {
    state.freeAgent = true;
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

/** 一个行动点用完后的清理：临场值、伤病、签约窗口、跨年。 */
function finishWeek(state: GameState, out: LogEntry[]): void {
  // 临场加减只在当场有效。
  state.temp = {};

  // 伤病每周有概率好转；停在 3 就是赛季报销。
  if (state.injury > 0) {
    const ctx = createRng(state.rngState);
    if (ctx.rng.next() < CONFIG.weekly.injuryHealChance) {
      state.injury -= 1;
      out.push({ text: '伤好了一点。', tone: 'good' });
    }
    state.rngState = ctx.state();
  }

  // 名次每周重算：榜上的人还在爬，你这周没动，名次就会往下掉。
  // 先算名次再判签约——邀请函看的是这一刻的名次。
  const before = state.placement;
  state.placement = placementOf(state.rankPoints, weeksPlayed(state.year, state.week) + 1);
  if (!state.actionGrid.includes('rank') && state.placement > before && before > 0) {
    out.push({ text: `这周没打排位，掉到第 ${state.placement} 名了。`, tone: 'bad' });
  }

  // 签约之后，到了比赛周就打一场。
  if (state.signed && state.injury < CONFIG.match.injuryBench) {
    const fixture = fixtureThisWeek(state);
    if (fixture) {
      const ctx = createRng(state.rngState);
      const won = ctx.rng.next() < winChance(state, fixture.rivalId);
      state.rngState = ctx.state();
      recordResult(state, fixture, won);
      out.push({
        text: matchLogLine(
          fixture,
          won,
          Math.round(myTeamStrength(state)),
          Math.round(rivalStrength(state.year, fixture.rivalId)),
        ),
        tone: won ? 'good' : 'bad',
      });
      state.temp = {};
    }
  }

  if (isSigningWindow(state.week)) resolveSigningWindow(state, out);
  if (state.ended) return;

  // 切片版：这一周打完就停，不再推进周次。
  if (CONFIG.career.sliceAtWeek > 0 && state.year === 1 && state.week === CONFIG.career.sliceAtWeek) {
    state.ended = sliceEnding(state);
    out.push({ text: '切片到此为止。', tone: 'plain' });
    return;
  }

  resetWeek(state);

  if (state.week < CONFIG.career.weeksPerYear) {
    state.week += 1;
    return;
  }

  advanceToNextYear(state, out);
}

function resetWeek(state: GameState): void {
  state.actionGrid = [null, null, null];
  state.actionTargets = [null, null, null];
  state.eventDone = false;
  state.pendingEvent = null;
  state.lastLedger = state.ledger;
  state.ledger = [];
  // 住处升级：每周开始自动恢复一点体力。
  if (hasOnce(state, 'residence') && state.stamina < state.maxStamina) {
    state.stamina = Math.min(
      state.maxStamina,
      state.stamina + CONFIG.shop.residence.stamina,
    );
  }
}

function advanceToNextYear(state: GameState, out: LogEntry[]): void {
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

  if (state.year === CONFIG.career.rookieSeason) {
    addHonor(state, 'rookie-of-year');
    out.push({ text: '赛季末，你拿了最佳新秀。', tone: 'good' });
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
  resetWeek(state);
  advanceToNextYear(state, out);
  if (!state.ended) {
    out.push({ text: `跳到第 ${state.year} 年。`, tone: 'plain' });
  }
}
