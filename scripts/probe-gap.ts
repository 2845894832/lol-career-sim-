import { rosterOf, teamStrength } from '../src/data/rosters';

const teams = [...rosterOf(1)].sort((a, b) => teamStrength(a) - teamStrength(b));
console.log('最弱三支的队均与中单：');
for (const t of teams.slice(0, 3)) {
  const mid = t.players.find((p) => p.pos === 'MID');
  console.log(` ${t.id} 队均 ${Math.round(teamStrength(t))} 中单 ${mid?.name} ${mid?.ovr}`);
}
const mids = rosterOf(1)
  .map((t) => ({ id: t.id, mid: t.players.find((p) => p.pos === 'MID')?.ovr ?? 0 }))
  .sort((a, b) => a.mid - b.mid);
console.log('全联盟中单最低三档', mids.slice(0, 3));
