/**
 * 转会：一年一签，跨年弹一张卡。
 *
 * 规则（用户已定，见《24-转会系统-待审.xlsx》）：
 * - 每年第 30 周打完，必弹一张转会卡；没有「都不签」的出口。
 * - 报价只出「同位置球员能力低于你」的队：换过去结构上就该顶掉他。
 * - 签字费按目标队首发五人 ovr 均值分三档：强 5000 / 中 2000 / 弱 1000。
 * - 续约也发签字费；转会才把教练信任重置到 65（刚好越过 60 的首发线）。
 * - 玩家可以被动接报价，也可以主动申请（同样的 gap 过滤，另给最多 3 支）。
 * - 队名按 data/teamIdentity.ts 跟随席位；没有后继 = 解散，只给保底弱队。
 */
import { CONFIG } from '../config';
import { myOvr } from '../core/league';
import { rosterOf, teamStrength, type RosterTeam } from './rosters';
import { teamInYear } from './teamIdentity';
import type { EventOption, GameEvent, GameState } from '../types';

const POS_LABEL: Record<GameState['role'], string> = {
  TOP: '上单',
  JUNGLE: '打野',
  MID: '中单',
  ADC: '射手',
  SUP: '辅助',
};

const POS_SHORT: Record<string, string> = {
  TOP: '上',
  JUNGLE: '野',
  MID: '中',
  ADC: '射',
  SUP: '辅',
};

export interface TransferOffer {
  teamId: string;
  name: string;
  /** 该队同位置的球员；没有这个人就是缺口。 */
  posName: string | null;
  posOvr: number | null;
  /** 对位差 = 该位置 ovr − 我；没有这个人算 0。 */
  gap: number;
  strength: number;
  fee: number;
  /** 次年首发五人，一句话。 */
  lineup: string;
  /** 能力上能不能顶掉对位（gap < 0，或该队这个位置空着）。 */
  startable: boolean;
}

/** 三档签字费：按当年所有队的首发均值排序，前 1/3 强、后 1/3 弱。 */
export function signingFee(year: number, teamId: string): number {
  const teams = [...rosterOf(year)].sort((a, b) => teamStrength(b) - teamStrength(a));
  const at = teams.findIndex((t) => t.id === teamId);
  if (at < 0) return CONFIG.transfer.feeWeak;
  const third = Math.ceil(teams.length / 3);
  if (at < third) return CONFIG.transfer.feeStrong;
  if (at >= teams.length - third) return CONFIG.transfer.feeWeak;
  return CONFIG.transfer.feeMid;
}

function lineupOf(team: RosterTeam): string {
  return team.players
    .map((p) => `${POS_SHORT[p.pos] ?? p.pos} ${p.name} ${p.ovr}`)
    .join(' · ');
}

function offerFor(state: GameState, team: RosterTeam, year: number): TransferOffer {
  const mine = myOvr(state);
  const player = team.players.find((p) => p.pos === state.role) ?? null;
  const gap = player ? player.ovr - mine : 0;
  return {
    teamId: team.id,
    name: team.name,
    posName: player?.name ?? null,
    posOvr: player?.ovr ?? null,
    gap,
    strength: teamStrength(team),
    fee: signingFee(year, team.id),
    lineup: lineupOf(team),
    startable: gap < 0,
  };
}

/** 能力上能顶掉对位的队：同位置球员 ovr 比你低，或这个位置空着。 */
function eligibleTeams(state: GameState, year: number): RosterTeam[] {
  const cur = teamInYear(state.teamId, year);
  const mine = myOvr(state);
  return rosterOf(year)
    .filter((t) => t.id !== cur)
    .filter((t) => {
      const player = t.players.find((p) => p.pos === state.role);
      return !player || player.ovr < mine;
    })
    .sort((a, b) => teamStrength(b) - teamStrength(a));
}

/** 从长名单里均匀取几支：最强、中间、最弱，让三份报价不是同一档。 */
function spread<T>(list: T[], n: number): T[] {
  if (list.length <= n) return list;
  const picked: T[] = [];
  for (let i = 0; i < n; i += 1) {
    const at = Math.round((i * (list.length - 1)) / Math.max(1, n - 1));
    const item = list[at];
    if (item !== undefined && !picked.includes(item)) picked.push(item);
  }
  return picked;
}

/** 球队主动发来的报价：2–3 支，且都能争首发。 */
export function transferOffers(state: GameState, year: number): TransferOffer[] {
  const teams = eligibleTeams(state, year);
  const offers = spread(teams, CONFIG.transfer.offers).map((t) => offerFor(state, t, year));
  if (offers.length > 0) return offers;

  // 保底：一支弱队也给报价（用户定的「跨年必须落在某支队伍上」）。
  const cur = teamInYear(state.teamId, year);
  const weak = [...rosterOf(year)]
    .filter((t) => t.id !== cur)
    .sort((a, b) => teamStrength(a) - teamStrength(b))[0];
  return weak ? [offerFor(state, weak, year)] : [];
}

/** 玩家主动申请时能谈的队：同样按 gap 过滤，避开已经报过价的。 */
export function applicationOffers(state: GameState, year: number): TransferOffer[] {
  const offered = new Set(transferOffers(state, year).map((o) => o.teamId));
  const teams = eligibleTeams(state, year).filter((t) => !offered.has(t.id));
  return spread(teams, CONFIG.transfer.applyOffers).map((t) => offerFor(state, t, year));
}

function contractOption(state: GameState, offer: TransferOffer, year: number, renew: boolean): EventOption {
  const needTrust = CONFIG.league.startThreshold + Math.max(0, offer.gap);
  const postTrust = renew ? state.coachTrust : CONFIG.transfer.trustAfterTransfer;
  const posLine = offer.posOvr === null
    ? `${POS_LABEL[state.role]}：名单上没有这个人（缺口）`
    : `${POS_LABEL[state.role]}：${offer.posName ?? '?'} ${offer.posOvr} · 你 ${myOvr(state)}（${offer.gap > 0 ? `差 ${offer.gap}` : `强 ${-offer.gap}`}）`;
  const trustLine = offer.gap > CONFIG.league.maxGap
    ? `对位差 ${offer.gap}，超过 10 点上不了场；先签下来再练。`
    : postTrust > needTrust
      ? `首发要信任 > ${needTrust}（${renew ? `现在 ${postTrust}` : `转会后 ${postTrust}`}），能上`
      : `首发要信任 > ${needTrust}，${renew ? `现在 ${postTrust}` : `转会后只有 ${postTrust}`}——转会当年从替补打起`;
  const detail = [
    posLine,
    `首发五人：${offer.lineup}`,
    `签字费 +${offer.fee} · 合同 1 年 · ${renew ? '信任不动' : `信任重置到 ${CONFIG.transfer.trustAfterTransfer}`}`,
    trustLine,
  ].join('\n');
  return {
    label: renew ? `${offer.name} 续约 1 年` : `去 ${offer.name}`,
    risk: 'success',
    detail,
    success: {
      contract: {
        teamId: offer.teamId,
        fee: offer.fee,
        resetTrust: !renew,
        startYear: year,
      },
    },
    successText: renew
      ? `你在 ${offer.name} 的续约合同上签了字，签字费 ${offer.fee}。`
      : `你转会去了 ${offer.name}，签字费 ${offer.fee}。`,
  };
}

/** 转会卡：续约 / 接一份报价 / 主动申请。 */
function buildTransferEvent(state: GameState, year: number): GameEvent {
  const options: EventOption[] = [];
  const curId = teamInYear(state.teamId, year);
  const curTeam = curId ? rosterOf(year).find((t) => t.id === curId) : undefined;
  if (curTeam) options.push(contractOption(state, offerFor(state, curTeam, year), year, true));

  for (const offer of transferOffers(state, year)) {
    options.push(contractOption(state, offer, year, false));
  }

  const applies = applicationOffers(state, year);
  if (applies.length > 0) {
    options.push({
      label: '我想去别队试试',
      risk: 'success',
      detail: `还有 ${applies.length} 支能谈：${applies.map((o) => o.name).join('、')}`,
      nextEvent: `TRA-${year}`,
    });
  }

  return {
    id: `TR-${year}`,
    kind: 'special',
    phase: 'any',
    title: `转会窗 · ${state.year} 年结束`,
    tags: ['#转会', '#合同年'],
    text: '合同年了。留下、换队，还是主动去谈一支？',
    once: true,
    weight: 1,
    auto: true,
    options,
  };
}

/** 主动申请的第二张卡：只列能谈的队，没有留队选项。 */
function buildApplyEvent(state: GameState, year: number): GameEvent | null {
  const offers = applicationOffers(state, year);
  if (offers.length === 0) return null;
  return {
    id: `TRA-${year}`,
    kind: 'special',
    phase: 'any',
    title: '主动申请',
    tags: ['#转会', '#主动申请'],
    text: '经理把你的简历递出去了，这几支队伍回了话。',
    once: true,
    weight: 1,
    auto: true,
    options: offers.map((offer) => contractOption(state, offer, year, false)),
  };
}

/** 第 30 周要不要开转会窗。 */
export function transferEvent(state: GameState): GameEvent | null {
  if (!state.signed) return null;
  const year = state.year + 1;
  if (year > CONFIG.career.years) return null;
  const event = buildTransferEvent(state, year);
  return event.options.length > 0 ? event : null;
}

/** 从 id 还原（TR-3 = 第 3 年合同窗前的卡）。 */
export function transferById(id: string, state: GameState): GameEvent | null {
  const m = /^(TR|TRA)-(\d+)$/.exec(id);
  if (!m) return null;
  const year = Number(m[2]);
  if (!Number.isFinite(year)) return null;
  return m[1] === 'TR' ? buildTransferEvent(state, year) : buildApplyEvent(state, year);
}
