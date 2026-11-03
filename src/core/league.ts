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
import type { GameState } from '../types';

export interface Fixture {
  week: number;
  rivalId: string;
  rivalName: string;
  /** 春决 / 夏决 是写死的周次，不进常规赛轮转。 */
  kind: 'regular' | 'spring' | 'summer';
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

/** 该年联盟里除我以外的队，按「种子 + 年份」打散，前 13 个当对手。 */
export function rivalsFor(year: number, myTeamId: string, seed: number): RosterTeam[] {
  const others = rosterOf(year).filter((t) => t.id !== myTeamId);
  return others
    .map((t, i) => ({ t, k: hash01(seed + year * 31, i + 1) }))
    .sort((a, b) => a.k - b.k)
    .map((x) => x.t);
}

/** 整年赛程：常规赛按双周排，春决第 15 周、夏决第 30 周。 */
export function scheduleFor(state: GameState): Fixture[] {
  const teamId = state.teamId;
  if (!teamId) return [];
  const year = state.year;
  const rivals = rivalsFor(year, teamId, state.seed);
  const weeks: readonly number[] = CONFIG.league.regularWeeks;
  const out: Fixture[] = [];
  weeks.forEach((week, i) => {
    const r = rivals[i];
    if (!r) return;
    const rec = state.seasonResults.find((x) => x.week === week);
    out.push({
      week,
      rivalId: r.id,
      rivalName: r.name,
      kind: 'regular',
      played: Boolean(rec),
      won: rec?.won,
    });
  });
  // 决赛是事件（SPR-* / SUM-*），不进赛程表；这里只出常规赛。
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
  state.seasonResults.push({ week: f.week, rivalId: f.rivalId, won, kind: 'regular' });
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

/** 教练信任过了阈值才算首发。 */
export function isStarting(state: GameState): boolean {
  return state.coachTrust > CONFIG.league.startThreshold;
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

/** 对手全队强度：用名单原值。 */
export function rivalStrength(year: number, rivalId: string): number {
  const t = rosterOf(year).find((x) => x.id === rivalId);
  return t ? teamStrength(t) : 77;
}

/** 我这一side的胜率：全队口径。 */
export function winChance(state: GameState, rivalId: string): number {
  const mine = myTeamStrength(state);
  const theirs = rivalStrength(state.year, rivalId);
  const raw = 0.5 + (mine - theirs) / 50;
  return Math.min(0.95, Math.max(0.05, raw));
}

/**
 * 积分榜。我的战绩来自 seasonResults；别人的战绩按强度抽个数。
 * 已打轮次 = 常规赛周里已经过去的周数。
 */
export function standings(state: GameState): StandingRow[] {
  const teams = rosterOf(state.year);
  if (!state.teamId || teams.length === 0) return [];
  const total = CONFIG.league.regularWeeks.filter((w) => w <= state.week).length;
  const avg = teams.reduce((s, t) => s + teamStrength(t), 0) / teams.length;
  const rows: StandingRow[] = teams.map((t) => {
    if (t.id === state.teamId) {
      const done = state.seasonResults.filter((r) => r.kind === 'regular');
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
