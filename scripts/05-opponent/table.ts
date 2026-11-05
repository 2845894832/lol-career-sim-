/**
 * 05 号用：把 rosters.ts 里的名单换算成队伍强度表（只读，不改 src）。
 *
 * 运行：npx vite-node scripts/05-opponent/table.ts
 * 输出：每个赛季 14–17 队的强度（五人 ovr 均值），以及赛季均值 / 中位 / 最强 / 最弱。
 * 口径与 src/data/rosters.ts:165-167 的 teamStrength() 完全一致。
 */
import { ROSTERS, seasonOf, teamStrength } from '../../src/data/rosters';

const years = [1, 2, 3, 4, 5, 6, 7, 8] as const;

function avg(xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
function median(xs: number[]): number {
  const a = [...xs].sort((x, y) => x - y);
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid]! : (a[mid - 1]! + a[mid]!) / 2;
}
const f2 = (x: number) => x.toFixed(2);

const all: { season: string; id: string; name: string; strength: number; rank: number }[] = [];

console.log('| 赛季 | 队数 | 均值 | 中位 | 最强 | 最弱 |');
console.log('|---|---|---|---|---|---|');
for (const year of years) {
  const season = seasonOf(year);
  const teams = [...ROSTERS[season]!].sort((a, b) => teamStrength(b) - teamStrength(a));
  const strengths = teams.map((t) => teamStrength(t));
  teams.forEach((t, i) => all.push({ season, id: t.id, name: t.name, strength: teamStrength(t), rank: i + 1 }));
  console.log(
    `| ${season} | ${teams.length} | ${f2(avg(strengths))} | ${f2(median(strengths))} | ${teams[0]!.name} ${f2(strengths[0]!)} | ${teams[teams.length - 1]!.name} ${f2(strengths[strengths.length - 1]!)} |`,
  );
}

console.log('');
console.log(`全部 ${all.length} 队：均值 ${f2(avg(all.map((x) => x.strength))) }，中位 ${f2(median(all.map((x) => x.strength)))}，范围 ${f2(Math.min(...all.map((x) => x.strength)))}–${f2(Math.max(...all.map((x) => x.strength)))}`);

// 冠军 / 中位 / 垫底 各 5 队（按强度排序取）
const sorted = [...all].sort((a, b) => b.strength - a.strength);
const picks = [...sorted.slice(0, 5), ...sorted.slice(Math.floor(sorted.length / 2) - 2, Math.floor(sorted.length / 2) + 3), ...sorted.slice(-5)];
console.log('');
console.log('| 档位 | 赛季 | 队伍 | 强度 | 赛季内排名 |');
console.log('|---|---|---|---|---|');
for (const [i, p] of picks.entries()) {
  const tier = i < 5 ? '冠军档' : i < 10 ? '中位档' : '垫底档';
  console.log(`| ${tier} | ${p.season} | ${p.name} | ${f2(p.strength)} | ${p.rank} |`);
}

// 全量 md，交给文档脚本读
console.log('');
console.log('FULL_TABLE_BEGIN');
console.log('| 赛季 | 排名 | 队伍 | 强度 |');
console.log('|---|---|---|---|');
for (const season of years.map(seasonOf)) {
  const rows = all.filter((x) => x.season === season).sort((a, b) => a.rank - b.rank);
  for (const r of rows) console.log(`| ${r.season} | ${r.rank} | ${r.name} | ${f2(r.strength)} |`);
}
console.log('FULL_TABLE_END');

const fs = await import('node:fs');
fs.writeFileSync(
  new URL('./table.json', import.meta.url),
  JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      note: 'strength = 该队 5 名选手 ovr 的算术平均，来源 src/data/rosters.ts',
      seasons: years.map((year) => {
        const season = seasonOf(year);
        const rows = all.filter((x) => x.season === season).sort((a, b) => a.rank - b.rank);
        return {
          year,
          season,
          count: rows.length,
          average: avg(rows.map((r) => r.strength)),
          median: median(rows.map((r) => r.strength)),
          teams: rows.map((r) => ({ rank: r.rank, id: r.id, name: r.name, strength: r.strength })),
        };
      }),
    },
    null,
    2,
  ),
);
console.log('已写出 scripts/05-opponent/table.json');
