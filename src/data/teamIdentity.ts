/**
 * 队名继承：同一 LPL 席位改名 / 被收购之后，下一支队伍接着算。
 *
 * 只在「换年」时用：名单一年一换，队名也换。玩家合同挂在席位上，
 * 不是挂在名字上，所以 S8 在 SNG 签的字，S9 就是 SN。
 * 对应关系见仓库根的《24-队伍更名映射.xlsx》。
 */
import { rosterOf } from './rosters';

/** 旧 id → 同一席位的新 id。链可以走多跳（SDG → DMO → TT）。 */
export const TEAM_SUCCESSOR: Record<string, string> = {
  SNG: 'SN',
  SN: 'WBG',
  TOP: 'TES',
  SS: 'LNG',
  SDG: 'DMO',
  DMO: 'TT',
  VG: 'RA',
  eStar: 'ES',
  ES: 'UP',
  RW: 'AL',
  V5: 'NIP',
};

/** 这个 id 在那一年的名单里叫什么；解散（没有后继）返回 null。 */
export function teamInYear(teamId: string | null, year: number): string | null {
  if (!teamId) return null;
  const roster = rosterOf(year);
  let id: string | null = teamId;
  // 最多跳 8 次，防映射表写出环。
  for (let i = 0; i < 8 && id; i += 1) {
    if (roster.some((t) => t.id === id)) return id;
    id = TEAM_SUCCESSOR[id] ?? null;
  }
  return null;
}
