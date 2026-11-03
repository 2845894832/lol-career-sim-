# -*- coding: utf-8 -*-
"""把 .scratch/roster-check/rosters_normalized.csv 里的 LPL 名单压成 src/data/rosters.ts。
只取每个赛季的 Spring（S15 取 Split 1）；一队 5 人，按位置排序；数值取五维均值（整数）。"""
import csv, io, json, re, collections, os

SRC = r'D:\deepseek-harness\default-workspace\.scratch\roster-check\rosters_normalized.csv'
OUT = r'D:\deepseek-harness\default-workspace\vibe-game-producer\src\data\rosters.ts'
POS = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUP']
ALIAS = {'SUPPORT': 'SUP', 'JUNGLER': 'JUNGLE', 'BOT': 'ADC', 'ADCARRY': 'ADC'}

rows = list(csv.DictReader(io.open(SRC, encoding='utf-8-sig')))
rows = [r for r in rows if r['league'] == 'LPL']
spring = {}
for r in rows:
    s = r['season']
    keep = r['split'] in ('Spring', 'Split 1')
    spring.setdefault((s, keep), collections.defaultdict(list))[r['team']].append(r)

seasons = sorted({r['season'] for r in rows}, key=lambda x: int(x[1:]))
data = {}
for s in seasons:
    teams = spring.get((s, True), {})
    if not all(len(v) >= 5 for v in teams.values()):
        teams = spring.get((s, False), teams)
    out = []
    for team, players in sorted(teams.items()):
        players = sorted(players, key=lambda p: POS.index(ALIAS.get(p['position'], p['position'])) if ALIAS.get(p['position'], p['position']) in POS else 9)
        if len({ALIAS.get(p['position'], p['position']) for p in players}) != 5:
            continue
        squad = []
        for p in players:
            vals = [int(p[k]) for k in ('laning', 'teamfight', 'sense', 'mentality', 'coop')]
            pos = ALIAS.get(p['position'], p['position'])
            squad.append({'pos': pos, 'name': p['player'], 'ovr': round(sum(vals) / 5)})
        out.append({'id': team, 'name': team, 'players': squad})
    data[s] = out

def strength(t):
    return sum(p['ovr'] for p in t['players']) / 5

lines = []
lines.append('// 由 scripts/build_rosters.py 生成，别手改。')
lines.append('// 来源：.scratch/roster-check/rosters_normalized.csv（LPL · 该赛季 Spring）')
lines.append('export type RosterPos = \'TOP\' | \'JUNGLE\' | \'MID\' | \'ADC\' | \'SUP\';')
lines.append('export interface RosterPlayer { pos: RosterPos; name: string; ovr: number }')
lines.append('export interface RosterTeam { id: string; name: string; players: RosterPlayer[] }')
lines.append('')
lines.append('export const ROSTERS: Record<string, RosterTeam[]> = {')
for s, teams in data.items():
    lines.append(f'  {s}: [')
    for t in teams:
        ps = ', '.join('{ pos: \'%s\', name: \'%s\', ovr: %d }' % (p['pos'], p['name'].replace("'", "\'"), p['ovr']) for p in t['players'])
        lines.append('    { id: \'%s\', name: \'%s\', players: [%s] },' % (t['id'], t['name'], ps))
    lines.append('  ],')
lines.append('}')
lines.append('')
lines.append('export function seasonOf(year: number): string {')
lines.append('  return \'S\' + (7 + year);')
lines.append('}')
lines.append('')
lines.append('export function rosterOf(year: number): RosterTeam[] {')
lines.append("  return ROSTERS[seasonOf(year)] ?? ROSTERS['S8'] ?? [];")
lines.append('}')
lines.append('')
lines.append('export function teamStrength(t: RosterTeam): number {')
lines.append("  return t.players.reduce((s, p) => s + p.ovr, 0) / t.players.length;")
lines.append('}')
lines.append('')
lines.append('export function weakestTeams(year: number, n: number): RosterTeam[] {')
lines.append('  return [...rosterOf(year)].sort((a, b) => teamStrength(a) - teamStrength(b)).slice(0, n);')
lines.append('}')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('teams per season:', {s: len(v) for s, v in data.items()})
print('bytes:', os.path.getsize(OUT))
