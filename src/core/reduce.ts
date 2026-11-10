import { CONFIG } from '../config';
import { fixtureThisWeek, isStarting, matchLogLine, myMatchStrength, myTeamStrength, recordResult, rivalStrength, seasonStrengths, startRequirement } from './league';
import { createRng } from '../rng';
import { hasOnce } from './shop';
import type { Action, ActionId, AttrKey, GameState, LogEntry, ReduceResult, ShowGame } from '../types';
import { applyAction, canAfford, isActionUnlocked, staminaCost } from './actions';
import { advanceYear } from './growth';
import { applyMatchOutcome, benchReason, canPlay } from './match';
import { drawEvent, drawMatchEvent, getEvent, resolveOption, skillBonusOf } from './events';
import { winProbability } from './odds';
import { normalEnding, sliceEnding, specialEnding } from './endings';
import { addHonor, attrTotal, cloneState, isFinalWeek, isSigningWindow } from './state';
import { awardHallOfFame, awardSeasonHonors } from './honors';
import { resolveWorldsGroup } from './worlds';
import { placementOf, rankOf, weeksPlayed } from './ladder';
import { transferEvent } from '../data/transfer';
import { teamInYear } from '../data/teamIdentity';

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
    case 'kickoffMatch':
      kickoffMatch(state, out);
      break;
    case 'chooseMatchOption':
      chooseMatchOption(state, action.option, out);
      break;
    case 'finishMatch':
      finishMatch(state, out);
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
  if (state.pendingMatch) {
    out.push({ text: '先把这周的比赛打完。', tone: 'plain' });
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
  if (state.pendingEvent || state.pendingMatch) {
    out.push({ text: '先把这周的事处理掉。', tone: 'plain' });
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
  if (state.pendingMatch) {
    out.push({ text: '先把这周的比赛打完。', tone: 'plain' });
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

  // 第 25 周先评常规赛荣誉，再打联赛决赛。
  if (state.week === CONFIG.league.leagueFinalWeek) {
    out.push(...awardSeasonHonors(state));
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
  beginMatch(state, out);
}

function chooseOption(state: GameState, index: number, out: LogEntry[]): void {
  if (!state.pendingEvent) {
    out.push({ text: '这周没有待选的事件。', tone: 'plain' });
    return;
  }
  const event = getEvent(state.pendingEvent.eventId, state);
  if (!event) {
    state.pendingEvent = null;
    state.eventDone = true;
    beginMatch(state, out);
    return;
  }

  const outcome = resolveOption(state, event, index);
  out.push(...outcome.logs);

  // 转会窗里选了「主动申请」：接着弹第二张卡，不结周。
  if (outcome.nextEventId) {
    const next = getEvent(outcome.nextEventId, state);
    if (next) {
      state.pendingEvent = { eventId: next.id };
      state.eventDone = false;
      return;
    }
  }

  // 周事件本身就是一场比赛（决赛）：沿用老规则，选项成败即胜负；
  // 结果先交给演出，等玩家点「继续」再结周。
  if (outcome.win !== null) {
    if (!canPlay(state) || !isStarting(state)) {
      out.push({ text: benchReason(state) ?? notStartingNote(state), tone: 'plain' });
      finishWeek(state, out);
      return;
    }
    out.push(...applyMatchOutcome(state, outcome.win, isFinalWeek(state)));
    if (event.opponentRole === 'final' || event.year !== undefined) {
      startShow(state, finalRival(state), outcome.win);
    } else {
      finishWeek(state, out);
    }
    return;
  }

  beginMatch(state, out);
}

/** 决赛对手队名：当季最强队。 */
function finalRival(state: GameState): { rivalId: string; rivalName: string } {
  const top = seasonStrengths(state.year)[0];
  return { rivalId: top?.id ?? '', rivalName: top?.name ?? '对手' };
}

/**
 * 结周后的比赛入口。
 * - 没赛程 / 没签约：这周没有你的比赛，直接结周。
 * - 有赛程但上不了场（伤停/替补）：球队照打，后台掷一次，无演出。
 * - 能上场：先出「开赛」卡，抽一张比赛事件，再进演出。
 */
/** 能上场但没进首发时的说明。 */
function notStartingNote(state: GameState): string {
  const req = startRequirement(state);
  const gap = req.gap > 0 ? `，对位差 ${req.gap}` : '';
  return `你还没进首发（信任 ${state.coachTrust}，要大于 ${req.needTrust}${gap}），这场球队自己打。`;
}

function beginMatch(state: GameState, out: LogEntry[]): void {
  const fixture = fixtureThisWeek(state);
  if (!fixture || !state.signed) {
    finishWeek(state, out);
    return;
  }

  if (!canPlay(state) || !isStarting(state)) {
    out.push({ text: benchReason(state) ?? notStartingNote(state), tone: 'plain' });
    const won = rollWin(state, fixture.rivalId, 0);
    recordResult(state, fixture, won);
    out.push({
      text: matchLogLine(fixture, won, Math.round(myTeamStrength(state)), Math.round(rivalStrength(state.year, fixture.rivalId))),
      tone: won ? 'good' : 'bad',
    });
    finishWeek(state, out);
    return;
  }

  const drawn = drawMatchEvent(state);
  state.rngState = drawn.rngState;
  state.pendingMatch = {
    phase: 'kickoff',
    rivalId: fixture.rivalId,
    rivalName: fixture.rivalName,
    eventId: drawn.event?.id ?? null,
    bestOf: seriesBestOf(state),
  };
  out.push({ text: `【比赛】第 ${fixture.week} 周，对 ${fixture.rivalName}。`, tone: 'plain' });
}

/** 点「开赛」：有比赛事件就弹卡，没有就直接掷。 */
function kickoffMatch(state: GameState, out: LogEntry[]): void {
  const pm = state.pendingMatch;
  if (!pm || pm.phase !== 'kickoff') return;
  if (pm.eventId) {
    pm.phase = 'event';
    return;
  }
  settleRegularMatch(state, out, 0, false);
}

/** 比赛事件卡选完：先算这次操作成没成，再由比赛掷一次定胜负。 */
function chooseMatchOption(state: GameState, index: number, out: LogEntry[]): void {
  const pm = state.pendingMatch;
  if (!pm || pm.phase !== 'event') return;
  const event = pm.eventId ? getEvent(pm.eventId, state) : null;
  if (!event) {
    settleRegularMatch(state, out, 0, false);
    return;
  }

  const outcome = resolveOption(state, event, index, { skillRoll: true });
  out.push(...outcome.logs);

  const option = event.options[index];
  const bonus =
    (option?.skillBonus ? skillBonusOf(state) : 0) + (outcome.success ? (option?.bonus ?? 0) : 0);
  settleRegularMatch(state, out, bonus, outcome.success);
}

/** 掷比赛胜负、记积分榜、写后果，然后进演出。 */
function settleRegularMatch(state: GameState, out: LogEntry[], bonus: number, optionSuccess: boolean): void {
  const pm = state.pendingMatch;
  if (!pm) return;
  pm.optionSuccess = optionSuccess;
  const fixture = fixtureThisWeek(state);
  const won = rollWin(state, pm.rivalId, bonus);
  if (fixture) {
    recordResult(state, fixture, won);
    out.push({
      text: matchLogLine(fixture, won, Math.round(myTeamStrength(state)), Math.round(rivalStrength(state.year, fixture.rivalId))),
      tone: won ? 'good' : 'bad',
    });
  }
  out.push(...applyMatchOutcome(state, won, isFinalWeek(state)));
  startShow(state, { rivalId: pm.rivalId, rivalName: pm.rivalName }, won);
}

/** 把结果扩成一场系列赛，放进状态里给演出用。 */
function startShow(state: GameState, rival: { rivalId: string; rivalName: string }, win: boolean): void {
  const bestOf = seriesBestOf(state);
  const { score, games } = buildSeries(state, win, bestOf);
  state.pendingMatch = {
    phase: 'show',
    rivalId: rival.rivalId,
    rivalName: rival.rivalName,
    eventId: null,
    win,
    score,
    games,
    bestOf,
  };
}

/** 常规赛 bo3，联赛决赛与 S 八强/四强/决赛 bo5。 */
function seriesBestOf(state: GameState): 3 | 5 {
  if (state.week === CONFIG.league.leagueFinalWeek) return 5;
  if (state.week >= CONFIG.league.worldsQuarterfinalWeek) return 5;
  return 3;
}

function rollWin(state: GameState, rivalId: string, bonus: number): boolean {
  const ctx = createRng(state.rngState);
  const win = ctx.rng.next() < winProbability(myMatchStrength(state), rivalStrength(state.year, rivalId), bonus, state.coachTrust);
  state.rngState = ctx.state();
  return win;
}

/**
 * 一局的比分与顺序：赢家先拿够局数，输家随机 0..need-1 局；
 * 顺序打乱成「有起伏」的剧本（如 2:1 → 输/赢/赢）。
 */
function buildSeries(state: GameState, win: boolean, bestOf: 3 | 5): { score: [number, number]; games: ShowGame[] } {
  const need = bestOf === 5 ? 3 : 2;
  const ctx = createRng(state.rngState);
  const loserGames = ctx.rng.int(need);
  const flags: boolean[] = [
    ...Array.from({ length: need }, () => true),
    ...Array.from({ length: loserGames }, () => false),
  ];
  for (let i = flags.length - 1; i > 0; i -= 1) {
    const j = ctx.rng.int(i + 1);
    [flags[i], flags[j]] = [flags[j]!, flags[i]!];
  }
  const games: ShowGame[] = flags.map((won) => {
    const hi = 11 + ctx.rng.int(4);
    const lo = 4 + ctx.rng.int(3);
    return won ? { win: true, kills: [hi, lo] } : { win: false, kills: [lo, hi] };
  });
  state.rngState = ctx.state();
  const score: [number, number] = win ? [need, loserGames] : [loserGames, need];
  return { score, games };
}

/** 演出看完，点「继续」才真正结周。 */
function finishMatch(state: GameState, out: LogEntry[]): void {
  if (!state.pendingMatch) return;
  state.pendingMatch = null;
  finishWeek(state, out);
}

function resolveSigningWindow(state: GameState, out: LogEntry[]): void {
  if (state.signed) return;

  // 王者 = 分数到最高档 + 名次进前 200。到了就必定收到邀请函；人气不参与签约。
  const qualified = rankOf(state.rankPoints, state.placement).index === CONFIG.rank.tiers.length - 1;

  if (qualified) {
    // 达标不再直接签字：下一周由 S16「邀请函」事件接手，选完才 signed。
    state.failedWindows = 0;
    state.freeAgent = true;
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

  // 第 27 周：S 赛小组赛自动模拟，出线才拿八强 flag。
  if (state.week === CONFIG.league.worldsGroupWeek) resolveWorldsGroup(state, out);

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

  // 第 30 周打完：签约球员先开转会窗，谈完才换年。
  // 以 triggeredEvents 里的 TR-id 做幂等键：卡结算完再走到这里就直接换年。
  if (!state.triggeredEvents.includes(`TR-${state.year + 1}`)) {
    const card = transferEvent(state);
    if (card) {
      state.pendingEvent = { eventId: card.id };
      state.eventDone = false;
      out.push({ text: '【转会窗】合同年到了，先谈下一份合同。', tone: 'plain' });
      return;
    }
  }

  advanceToNextYear(state, out);
}

function resetWeek(state: GameState): void {
  state.actionGrid = [null, null, null];
  state.actionTargets = [null, null, null];
  state.eventDone = false;
  state.pendingEvent = null;
  state.pendingMatch = null;
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
  // 战绩按年隔离：不清零的话，第 2 年的赛程会把上一年同周次的比赛当成已打完。
  state.seasonResults = [];
  state.eventDone = false;

  if (state.year > CONFIG.career.years) {
    state.year = CONFIG.career.years;
    out.push(...awardHallOfFame(state));
    state.ended = normalEnding(state, 'expired');
    out.push({ text: '八年过去了。', tone: 'plain' });
    return;
  }

  out.push(...advanceYear(state).map((text) => ({ text, tone: 'plain' as const })));

  // 合同挂在席位上：队名换了就跟着换；没有后继 = 解散（正常流程里转会窗已经拦住了）。
  if (state.signed) {
    const next = teamInYear(state.teamId, state.year);
    if (!next) {
      state.teamId = null;
      state.signed = false;
      state.freeAgent = true;
      state.contractYear = null;
      out.push({ text: '老东家的席位没了，你成了自由人。', tone: 'bad' });
    } else if (next !== state.teamId) {
      state.teamId = next;
      out.push({ text: `队伍更名为 ${next}，合同跟着席位走。`, tone: 'plain' });
    }
  }

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
  out.push(...awardHallOfFame(state));
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
