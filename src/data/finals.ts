import { CONFIG } from '../config';
import { invitations, isStarting, myPlace } from '../core/league';
import { canPlay } from '../core/match';
import { rankOf } from '../core/ladder';
import type { GameEvent, GameState } from '../types';

/**
 * 联赛决赛与 S 赛：每年按年份生成，不写进 EVENTS。
 *
 * 为什么按年生成：triggeredEvents 是整局去重，静态事件只会触发一次。
 * 这里用 LPL-1 / WQF-1 / WSF-1 / WF-1 这样的 id，去重自然按年生效。
 *
 * 赛程：24 周常规赛；第 25 周联赛决赛；第 26 周休赛；
 * 27 周 S 小组赛（自动模拟）；28/29/30 周八强/四强/决赛。
 */

const LEAGUE_WEEK = CONFIG.league.leagueFinalWeek;
const WORLDS_QF_WEEK = CONFIG.league.worldsQuarterfinalWeek;
const WORLDS_SF_WEEK = CONFIG.league.worldsSemifinalWeek;
const WORLDS_F_WEEK = CONFIG.league.worldsFinalWeek;

function sFlag(year: number, stage: string): string {
  return `#S${stage}-${year}`;
}

/** 第 25 周：常规赛前 2 名的单场联赛决赛。 */
export function leagueFinal(year: number): GameEvent {
  return {
    id: `LPL-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: LEAGUE_WEEK,
    opponent: 70,
    opponentRole: 'final',
    tags: ['#联赛决赛', '#联赛', '#决赛'],
    text: '联赛决赛。对面是常规赛第一，你们输过一次。BP 还没开始，场馆已经满了。',
    once: true,
    weight: 1,
    requires: (s) => canPlay(s) && isStarting(s) && myPlace(s) <= 2,
    options: [
      {
        label: '让中单先拿绝活',
        risk: 'roll',
        bonus: 0.15,
        success: { honor: 'lpl-champion', attrs: { mentality: 3, popularity: 4 } },
        successText: '对面三 ban 中单，你的绝活放出来了。团战第一秒你就知道能赢。',
        fail: { attrs: { mentality: -4, popularity: -2 } },
        failText: '绝活被针对了。你在水晶爆炸前就摘了耳机。',
      },
      {
        label: '抢版本最强阵容',
        risk: 'roll',
        bonus: 0.3,
        success: { honor: 'lpl-champion', attrs: { popularity: 5 } },
        successText: '版本答案就是版本答案。三局两胜，第三局二十三分钟结束。',
        fail: { attrs: { mentality: -3 } },
        failText: '对面用你最熟的阵容赢了你。',
      },
      {
        label: '打自己这套',
        risk: 'roll',
        bonus: 0.0,
        success: { honor: 'lpl-champion', attrs: { teamfight: 2, popularity: 3 } },
        successText: '你们打了一整年的东西，今天终于对上了。',
        fail: { attrs: { mentality: -2, teamfight: 1 } },
        failText: '差一点。你在回来的车上把这场看了三遍。',
      },
    ],
  };
}

/** 第 28 周：S 赛八强。 */
export function worldsQuarterfinal(year: number): GameEvent {
  return {
    id: `WQF-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: WORLDS_QF_WEEK,
    opponent: 70,
    opponentRole: 'final',
    tags: ['#S赛', '#八强'],
    text: 'S 赛八强。对面是另一组的头名，训练赛里你们互有胜负。',
    once: true,
    weight: 1,
    requires: (s) => canPlay(s) && isStarting(s) && s.flags.includes(sFlag(year, '八强')),
    options: [
      {
        label: '第一局抢开局',
        risk: 'roll',
        bonus: 0.15,
        success: { flag: sFlag(year, '四强'), attrs: { popularity: 4 } },
        successText: '你们把比赛拖进自己最熟的节奏，三比一进四强。',
        fail: { attrs: { mentality: -4 } },
        failText: '开局没抢到，后面每一局都在追。',
      },
      {
        label: '放对面绝活，打团',
        risk: 'roll',
        bonus: 0.05,
        success: { flag: sFlag(year, '四强'), attrs: { teamfight: 2, popularity: 3 } },
        successText: '对面拿了绝活，但你们的团战阵型一直没散。',
        fail: { attrs: { mentality: -3, teamfight: 1 } },
        failText: '绝活还是绝活。你们在龙坑前被一波带走。',
      },
      {
        label: '拼个人能力',
        risk: 'roll',
        bonus: 0.2,
        success: { flag: sFlag(year, '四强'), attrs: { operation: 2, popularity: 4 } },
        successText: '第五局你赢了每一次该赢的对线。',
        fail: { attrs: { mentality: -2 } },
        failText: '你赢了对线，输了比赛。',
      },
    ],
  };
}

/** 第 29 周：S 赛四强。 */
export function worldsSemifinal(year: number): GameEvent {
  return {
    id: `WSF-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: WORLDS_SF_WEEK,
    opponent: 70,
    opponentRole: 'final',
    tags: ['#S赛', '#四强'],
    text: 'S 赛四强。再赢一场就是决赛，场馆外面已经有人在喊你的名字。',
    once: true,
    weight: 1,
    requires: (s) => canPlay(s) && isStarting(s) && s.flags.includes(sFlag(year, '四强')),
    options: [
      {
        label: '按训练赛那套打',
        risk: 'roll',
        bonus: 0.15,
        success: { flag: sFlag(year, '决赛'), attrs: { awareness: 2, popularity: 4 } },
        successText: '你们把训练赛练了两个月的东西原样搬上舞台，三比二。',
        fail: { attrs: { mentality: -4 } },
        failText: '训练赛的东西被对面读透了。',
      },
      {
        label: '临时变阵',
        risk: 'roll',
        bonus: 0.25,
        success: { flag: sFlag(year, '决赛'), attrs: { popularity: 5 } },
        successText: '变阵赌对了。对面到第三局还没反应过来。',
        fail: { attrs: { mentality: -3, awareness: 1 } },
        failText: '变阵没打出来，你们把自己绕进去了。',
      },
      {
        label: '让选手自己发挥',
        risk: 'roll',
        bonus: 0.0,
        success: { flag: sFlag(year, '决赛'), attrs: { operation: 2, teamfight: 2, popularity: 3 } },
        successText: '最后一波团，五个人都知道该干什么。',
        fail: { attrs: { mentality: -2 } },
        failText: '最后一波团，五个人各干各的。',
      },
    ],
  };
}

/** 第 30 周：S 赛决赛。赢了由 applyMatchOutcome 写 worlds-champion。 */
export function worldsFinal(year: number): GameEvent {
  return {
    id: `WF-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: WORLDS_F_WEEK,
    opponent: 70,
    opponentRole: 'final',
    tags: ['#S赛', '#决赛'],
    text: 'S 赛决赛。舞台比你想象的大，奖杯就放在通道尽头。',
    once: true,
    weight: 1,
    requires: (s) => canPlay(s) && isStarting(s) && s.flags.includes(sFlag(year, '决赛')),
    options: [
      {
        label: '拿最稳的阵容',
        risk: 'roll',
        bonus: 0.1,
        success: { attrs: { popularity: 8, mentality: 3 } },
        successText: '你们没有给对面任何一次机会。三比零。',
        fail: { attrs: { mentality: -5 } },
        failText: '最稳的阵容也没能稳住。',
      },
      {
        label: '把绝活全放出来',
        risk: 'roll',
        bonus: 0.2,
        success: { attrs: { popularity: 10, operation: 2 } },
        successText: '最后一局你选了那个英雄。全场站起来的时候，你知道自己赌对了。',
        fail: { attrs: { mentality: -4, popularity: -2 } },
        failText: '绝活没能救你。',
      },
      {
        label: '相信队友',
        risk: 'roll',
        bonus: 0.05,
        success: { attrs: { popularity: 7, teamfight: 2 } },
        successText: '最后一波团，队友把你托了起来。',
        fail: { attrs: { mentality: -3 } },
        failText: '你相信了他们，他们没能接住。',
      },
    ],
  };
}

/** 本周是不是必触发赛事周，是就返回那场。 */
export function finalFor(state: GameState): GameEvent | null {
  if (state.week === LEAGUE_WEEK) return leagueFinal(state.year);
  if (state.week === WORLDS_QF_WEEK) return worldsQuarterfinal(state.year);
  if (state.week === WORLDS_SF_WEEK) return worldsSemifinal(state.year);
  if (state.week === WORLDS_F_WEEK) return worldsFinal(state.year);
  return null;
}

/** 从 id 还原（LPL-3 / WQF-3 / WSF-3 / WF-3）。结算事件时用。 */
export function finalById(id: string): GameEvent | null {
  const m = /^(LPL|WQF|WSF|WF)-(\d+)$/.exec(id);
  if (!m) return null;
  const year = Number(m[2]);
  if (m[1] === 'LPL') return leagueFinal(year);
  if (m[1] === 'WQF') return worldsQuarterfinal(year);
  if (m[1] === 'WSF') return worldsSemifinal(year);
  return worldsFinal(year);
}

/**
 * 签约事件：到王者后收到邀请函，只有一个「签字进队」选项，必定成功。
 * 队伍取当年最弱的三支里的第一支——具体签哪支还要你定。
 */
function inviteOptions(state: GameState) {
  const team = invitations(state.year)[0];
  if (!team) return [];
  return [{
    label: '签字进队',
    risk: 'success' as const,
    success: { signed: true, teamId: team.id, coachTrust: 10, attrs: { popularity: 4 } },
    successText: `你在 ${team.name} 的合同上签了字，第二天搬进了基地。`,
  }];
}

export function inviteEvent(state: GameState): GameEvent | null {
  if (state.signed) return null;
  const top = rankOf(state.rankPoints, state.placement).index;
  if (top < 9) return null;
  return {
    id: `INV-${state.year}`,
    kind: 'special',
    phase: 'any',
    year: undefined,
    auto: true,
    tags: ['#邀请函', '#签约', '#王者'],
    text: '桌上放着一封邀请函，战队经理在等你答复。',
    once: true,
    weight: 1,
    requires: (s) => !s.signed && rankOf(s.rankPoints, s.placement).index >= 9,
    options: inviteOptions(state),
  };
}

/** 结算邀请函时从 id 还原（INV-1 = 第 1 年的邀请函）。 */
export function inviteById(id: string): GameEvent | null {
  const m = /^INV-(\d+)$/.exec(id);
  if (!m) return null;
  const year = Number(m[1]);
  return inviteEvent({
    signed: false,
    year,
    rankPoints: 4500,
    placement: 1,
  } as unknown as GameState);
}
