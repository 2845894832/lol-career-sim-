/**
 * 联赛：赛程、积分榜、我方阵容。
 *
 * 三个原则：
 * 1. 名单是真名单（src/data/rosters.ts，按年取该赛季）。
 * 2. 赛程只算位置，不算结果；结果记在 GameState.seasonResults 里。
 * 3. 别人的战绩是模拟出来的，不是真打——他们的 13 场只用强度算个数，
 *    所以积分榜是「你在真打、别人在同分布里抽」。够用，但不是对局推演。
 */
import { CONFIG } from '../config';
import { ROSTERS, rosterOf, seasonOf, teamStrength, weakestTeams, type RosterTeam } from '../data/rosters';
import { effectiveAttr, isFinalWeek } from './state';
import { winProbability } from './odds';
import { MATCH_ATTRS, type GameState } from '../types';

export interface Fixture {
  week: number;
  rivalId: string;
  rivalName: string;
  /** 联赛决赛与 S 赛是事件，不进常规赛轮转。 */
  kind: 'regular';
  played: boolean;
  won?: boolean;
}

export interface StandingRow {
  teamId: string;
  name: string;
  wins: number;
  losses: number;
  isMe: boolean;
}

function hash01(a: number, b: number): number {
  let h = (a * 374761393 + b * 668265263) >>> 0;
  h = (h ^ (h >>> 13)) * 1274126177;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/** 该年联盟里除我以外的队，按「种子 + 年份」打散，每队各碰一次。 */
export function rivalsFor(year: number, myTeamId: string, seed: number): RosterTeam[] {
  const others = rosterOf(year).filter((t) => t.id !== myTeamId);
  return others
    .map((t, i) => ({ t, k: hash01(seed + year * 31, i + 1) }))
    .sort((a, b) => a.k - b.k)
    .map((x) => x.t);
}

/** 单循环周次：第 1 场第 2 周、最后一场第 24 周，中间均匀铺开。 */
export function leagueWeeksFor(year: number): number[] {
  const n = rosterOf(year).length - 1;
  if (n <= 1) return [2];
  return Array.from({ length: n }, (_, i) => 2 + Math.round((i * 22) / (n - 1)));
}

/** 整年常规赛：按当年队数动态排单循环，联赛决赛与 S 赛走事件。 */
export function scheduleFor(state: GameState): Fixture[] {
  const teamId = state.teamId;
  if (!teamId) return [];
  const year = state.year;
  const rivals = rivalsFor(year, teamId, state.seed);
  const weeks = leagueWeeksFor(year);
  const out: Fixture[] = [];
  weeks.forEach((week, i) => {
    const r = rivals[i];
    if (!r) return;
    const rec = state.seasonResults.find((x) => x.year === year && x.week === week);
    out.push({
      week,
      rivalId: r.id,
      rivalName: r.name,
      kind: 'regular',
      played: Boolean(rec),
      won: rec?.won,
    });
  });
  // 联赛决赛与 S 赛是事件，不进赛程表；这里只出常规赛。
  return out.sort((a, b) => a.week - b.week);
}

/** 下一场没打的常规赛。 */
export function nextFixture(state: GameState): Fixture | null {
  return scheduleFor(state).find((f) => !f.played) ?? null;
}

/** 下一场之后的几场（列表用，不含下一场自己）。 */
export function upcomingFixtures(state: GameState, n: number): Fixture[] {
  const fx = scheduleFor(state).filter((f) => !f.played);
  return fx.slice(1, n + 1);
}

/** 这一周有没有常规赛（且还没打）。 */
export function fixtureThisWeek(state: GameState): Fixture | null {
  return scheduleFor(state).find((f) => f.week === state.week && !f.played) ?? null;
}

/** 记一场结果；比分是编的，只为日志好看。 */
export function recordResult(state: GameState, f: Fixture, won: boolean): void {
  state.seasonResults.push({ year: state.year, week: f.week, rivalId: f.rivalId, won, kind: 'regular' });
}

/** 一场常规赛的文字结果，日志用。 */
export function matchLogLine(f: Fixture, won: boolean, mine: number, theirs: number): string {
  const score = won ? '2:0' : '1:2';
  const detail = won
    ? `你们 ${score} 拿下 ${f.rivalName}，${mine} 比 ${theirs} 的账面差距没在比分上出现。`
    : `对面 ${score} 赢了。${mine} 对 ${theirs}，赢面本来就不大。`;
  return `第 ${f.week} 周 · 常规赛：${detail}`;
}

/** 打完这一周之后，下一场之前还有几周。 */
export function weeksUntil(state: GameState, week: number): number {
  return week - state.week;
}

/** 我在场上的数值（六维均值）。 */
export function myOvr(state: GameState): number {
  const a = state.attrs;
  return Math.round((a.operation + a.laning + a.teamfight + a.awareness + a.mentality) / 5);
}

/** 队里同位置的那个首发；没签约或名单里没人打这个位置就返回 null。 */
export function rivalAtMySlot(state: GameState): { name: string; ovr: number } | null {
  if (!state.teamId) return null;
  const team = rosterOf(state.year).find((t) => t.id === state.teamId);
  const p = team?.players.find((x) => x.pos === state.role);
  return p ? { name: p.name, ovr: p.ovr } : null;
}

/**
 * 首发条件：信任与对位差距互相拉扯，但有两条底线。
 * - 底线一：教练信任必须 > 60。
 * - 底线二：对位差距（首发 − 你）不得 > 10；弱超过 10 点，信任再高也上不了。
 * - 互补：你比他弱几点，就要多几点信任（1 点差距 = 1 点信任）。
 */
export function startRequirement(state: GameState): { needTrust: number; gap: number; ok: boolean } {
  const rival = rivalAtMySlot(state);
  const mine = myOvr(state);
  const gap = rival ? rival.ovr - mine : 0;
  const needTrust = CONFIG.league.startThreshold + Math.max(0, gap);
  const ok = state.coachTrust > needTrust && gap <= CONFIG.league.maxGap;
  return { needTrust, gap, ok };
}

/** 教练信任与对位差距都过了才算首发。 */
export function isStarting(state: GameState): boolean {
  return startRequirement(state).ok;
}

/** 我这边的 5 个人：首发时是「名单 4 人 + 我」，替补时是名单原班。 */
export function mySquad(state: GameState): { pos: string; name: string; ovr: number; me: boolean }[] {
  const team = state.teamId ? rosterOf(state.year).find((t) => t.id === state.teamId) : undefined;
  if (team && !isStarting(state)) {
    const order = { TOP: 0, JUNGLE: 1, MID: 2, ADC: 3, SUP: 4 } as Record<string, number>;
    return team.players
      .map((p) => ({ pos: p.pos, name: p.name, ovr: p.ovr, me: false }))
      .sort((a, b) => (order[a.pos] ?? 9) - (order[b.pos] ?? 9));
  }
  const me = {
    pos: state.role,
    name: state.playerName || '你',
    ovr: Math.round((state.attrs.operation + state.attrs.laning + state.attrs.teamfight + state.attrs.awareness + state.attrs.mentality) / 5),
    me: true,
  };
  const mates = (team?.players ?? []).filter((p) => p.pos !== state.role).map((p) => ({ pos: p.pos, name: p.name, ovr: p.ovr, me: false }));
  const out = [...mates.slice(0, 4), me];
  const order = { TOP: 0, JUNGLE: 1, MID: 2, ADC: 3, SUP: 4 } as Record<string, number>;
  return out.sort((a, b) => (order[a.pos] ?? 9) - (order[b.pos] ?? 9));
}

/** 我方全队强度（含我）。 */
export function myTeamStrength(state: GameState): number {
  const squad = mySquad(state);
  return squad.reduce((s, p) => s + p.ovr, 0) / squad.length;
}

/**
 * 我这一侧上场时的强度：签约后 = 场上五人 ovr 均值；路人期 = 六维均值。
 * 和 matchRate 用的是同一把尺子，赛程表与真正结算才对得上。
 */
export function myMatchStrength(state: GameState): number {
  if (state.signed) return myTeamStrength(state);
  const total = MATCH_ATTRS.reduce((sum, key) => sum + effectiveAttr(state, key), 0);
  return total / MATCH_ATTRS.length;
}

/** 对手全队强度：用名单原值。 */
export function rivalStrength(year: number, rivalId: string): number {
  const t = rosterOf(year).find((x) => x.id === rivalId);
  return t ? teamStrength(t) : 77;
}

/** 当季每支队的名单强度，按强弱降序（全部来自 rosters.ts 的 ovr 均值）。 */
export function seasonStrengths(year: number): { id: string; name: string; strength: number }[] {
  return rosterOf(year)
    .map((t) => ({ id: t.id, name: t.name, strength: teamStrength(t) }))
    .sort((a, b) => b.strength - a.strength);
}

/** 当季平均强度：没有排到具体对手的比赛周用它。 */
export function seasonAverageStrength(year: number): number {
  const rows = seasonStrengths(year);
  if (rows.length === 0) return CONFIG.match.opponentDefault;
  return rows.reduce((sum, r) => sum + r.strength, 0) / rows.length;
}

/** 当季最强队的强度。 */
export function seasonTopStrength(year: number): number {
  return seasonStrengths(year)[0]?.strength ?? CONFIG.match.opponentFinal;
}

/**
 * 这一场的对手强度（信任主线那一场）。
 * - S 赛决赛：当季最强队（这一周还有最后一场常规赛，优先级低于决赛）。
 * - 常规赛：赛程里那支队的名单强度（和积分榜用同一条线）。
 * - 其余比赛周：当季平均强度。
 * 名单缺失或 opponentSource='fixed' 时回落到 CONFIG 的两个兜底常量。
 */
export function opponentStrength(state: GameState): number {
  if (CONFIG.match.opponentSource === 'fixed') {
    return isFinalWeek(state) ? CONFIG.match.opponentFinal : CONFIG.match.opponentDefault;
  }
  // 决赛周也有最后一场常规赛，但信任主线打的是决赛，所以决赛优先。
  if (isFinalWeek(state)) return seasonTopStrength(state.year);
  const fixture = fixtureThisWeek(state);
  if (fixture) return rivalStrength(state.year, fixture.rivalId);
  return seasonAverageStrength(state.year);
}

/**
 * 决赛对手：当季最强队。
 * 春决文案写的是「对面是常规赛第一」，所以这里也用第一，而不是两队里较强的一侧
 * （这一代没有四强/半决赛，进决赛的两支队没有单独建模）。
 * fallback 是改之前手写的老常量，只在 opponentSource='fixed' 时生效。
 */
export function finalOpponentStrength(year: number, fallback: number): number {
  if (CONFIG.match.opponentSource === 'fixed') return fallback;
  return seasonStrengths(year)[0]?.strength ?? fallback;
}

/** 赛程表上这一场的胜率：和 matchRate 同一个公式、同一侧强度。 */
export function winChance(state: GameState, rivalId: string): number {
  return winProbability(myMatchStrength(state), rivalStrength(state.year, rivalId), 0, state.coachTrust);
}

/**
 * 积分榜。我的战绩来自 seasonResults；别人的战绩按强度抽个数。
 * 已打轮次 = 常规赛周里已经过去的周数。
 */
export function standings(state: GameState): StandingRow[] {
  const teams = rosterOf(state.year);
  if (!state.teamId || teams.length === 0) return [];
  const total = leagueWeeksFor(state.year).filter((w) => w <= state.week).length;
  const avg = teams.reduce((s, t) => s + teamStrength(t), 0) / teams.length;
  const rows: StandingRow[] = teams.map((t) => {
    if (t.id === state.teamId) {
      const done = state.seasonResults.filter(
        (r) => r.kind === 'regular' && r.year === state.year,
      );
      const wins = done.filter((r) => r.won).length;
      return { teamId: t.id, name: t.name, wins, losses: done.length - wins, isMe: true };
    }
    const s = teamStrength(t);
    const p = Math.min(0.85, Math.max(0.15, 0.5 + (s - avg) / 40));
    let wins = 0;
    for (let i = 0; i < total; i += 1) {
      if (hash01(state.seed + state.year * 7 + i, t.id.length * 131 + s) < p) wins += 1;
    }
    return { teamId: t.id, name: t.name, wins, losses: total - wins, isMe: false };
  });
  return rows.sort((a, b) => b.wins - a.wins || a.losses - b.losses || a.teamId.localeCompare(b.teamId));
}

export function myPlace(state: GameState): number {
  const rows = standings(state);
  const i = rows.findIndex((r) => r.isMe);
  return i < 0 ? 0 : i + 1;
}

/** 上王者之后给的三个邀请：当年最弱的 3 支。 */
export function invitations(year: number): RosterTeam[] {
  return weakestTeams(year, CONFIG.league.invitations);
}

/** 队伍某个位置是不是有缺口（名单里没人打这个位置）。 */
export function needsRole(year: number, teamId: string, role: string): boolean {
  const t = rosterOf(year).find((x) => x.id === teamId);
  if (!t) return false;
  return !t.players.some((p) => p.pos === role);
}

export { seasonOf, ROSTERS };
