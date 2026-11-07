# 把 events-live.json 渲染成可逐条看的 xlsx。不写 src。
# 用法：npx vite-node scripts/06-events/dump_live.ts
#       PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_all_xlsx.py
import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-204条.xlsx'

NAVY = '1F3B57'
HEAD_FILL = PatternFill('solid', fgColor=NAVY)
HEAD_FONT = Font(color='FFFFFF', bold=True, size=10)
BODY = Font(size=10)
THIN = Side(style='thin', color='D6DCE5')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')

ATTR = {'operation': '操作', 'laning': '对线', 'teamfight': '团战',
        'awareness': '意识', 'mentality': '心态', 'popularity': '人气'}
KIND = {'match': '比赛', 'life': '生活', 'special': '特殊'}
PHASE = {'growth': '成长', 'peak': '巅峰', 'decline': '衰退', 'any': '任何'}
RISK = {'roll': '掷骰', 'success': '必成', 'fail': '必败'}


def cons(c):
    if not c:
        return '—'
    bits = []
    for k, v in (c.get('attrs') or {}).items():
        bits.append(f'{ATTR.get(k, k)}{v:+d}')
    for k, name in (('temp', '临时'), ('stamina', '体力'), ('maxStamina', '体力上限'),
                    ('money', '金钱'), ('injury', '伤病'), ('coachTrust', '信任'),
                    ('honor', '荣誉'), ('signed', '签约'), ('teamId', '队伍')):
        if k in c and c[k] is not None:
            v = c[k]
            if k in ('honor', 'signed', 'teamId'):
                bits.append(f'{name}={v}')
            else:
                bits.append(f'{name}{v:+d}')
    if c.get('flag'):
        bits.append(f'标记 {c["flag"]}')
    if c.get('clearFlag'):
        bits.append(f'清标记 {c["clearFlag"]}')
    return ' '.join(bits) or '—'


def cond_of(e):
    if e.get('filler'):
        return '兜底池（当年没有别的可抽时）'
    if e.get('year') and e.get('week'):
        return f"第 {e['year']} 年 · 第 {e['week']} 周（写死）"
    if e.get('year'):
        return f"第 {e['year']} 年（写死）"
    r = e.get('requires')
    if not r:
        return '无额外条件'
    if 'benchThreshold' in r:
        return '已签约且能上场（信任 ≥25）'
    parts = []
    r = r.split('=>', 1)[-1]
    if re.search(r'!s\.signed', r):
        parts.append('未签约')
    elif 'signed' in r:
        parts.append('已签约')
    m = re.search(r"coachTrust\s*>=\s*(\d+)", r)
    if m:
        parts.append(f'信任 ≥{m.group(1)}')
    m = re.search(r"popularity\s*>=\s*(\d+)", r)
    if m:
        parts.append(f'人气 ≥{m.group(1)}')
    m = re.search(r"injury\s*>=\s*(\d+)", r)
    if m:
        parts.append(f'伤停 ≥{m.group(1)}')
    m = re.search(r"year\s*===\s*(\d+)", r)
    if m:
        parts.append(f'第 {m.group(1)} 年')
    for f in re.findall(r"flags\.includes\('([^']+)'\)", r):
        parts.append(f'标记 {f}')
    if 'honors.some' in r:
        parts.append('有冠军荣誉')
    return ' · '.join(parts) or '（表达式）'


def style(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for c in row:
            c.border = BORDER
            c.alignment = WRAP
            if c.row == 1:
                c.fill = HEAD_FILL
                c.font = HEAD_FONT
            else:
                c.font = BODY
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


def main():
    events = json.loads((HERE / 'events-live.json').read_text(encoding='utf-8'))

    wb = Workbook()
    ws = wb.active
    ws.title = '事件'
    ws.append(['ID', '类型', '阶段', '触发条件', '标签', '正文', '一次', '权重', '选项数', '审查'])
    for e in events:
        ws.append([e['id'], KIND[e['kind']], PHASE[e['phase']], cond_of(e), ' '.join(e['tags']),
                   e['text'], '是' if e['once'] else '', e['weight'], len(e['options']), ''])
    style(ws, [7, 7, 7, 30, 18, 40, 6, 6, 7, 10])

    wo = wb.create_sheet('选项')
    wo.append(['事件ID', '#', '选项', '风险', '加成', '成功后果', '失败后果', '成功文案', '失败文案', '审查'])
    for e in events:
        for i, o in enumerate(e['options'], 1):
            extra = []
            if o['attrs']:
                extra.append('/'.join(ATTR.get(a, a) for a in o['attrs']))
            if o['mix']:
                extra.append('四维+人气÷2')
            if o['bonus']:
                extra.append(f'对手加成{o["bonus"]:+.2f}')
            if o['skillBonus']:
                extra.append('四维加成')
            if o['matchResult']:
                extra.append(f'赛果={o["matchResult"]}')
            wo.append([e['id'], i, o['label'], RISK[o['risk']], '；'.join(extra) or '—',
                       cons(o['success']), cons(o['fail']),
                       o['successText'] or '', o['failText'] or '', ''])
    style(wo, [7, 4, 18, 6, 16, 28, 28, 44, 44, 10])

    wn = wb.create_sheet('说明')
    kinds, phases = {}, {}
    for e in events:
        kinds[KIND[e['kind']]] = kinds.get(KIND[e['kind']], 0) + 1
        phases[PHASE[e['phase']]] = phases.get(PHASE[e['phase']], 0) + 1
    table = [e for e in events if not e['filler']]
    notes = [
        ['项目', '内容'],
        ['总数', f'{len(events)} 条（含兜底 F01/F02；表内事件 {len(table)} 条）'],
        ['类型', ' / '.join(f'{k} {v}' for k, v in kinds.items())],
        ['阶段', ' / '.join(f'{k} {v}' for k, v in phases.items())],
        ['可重复', f"{len([e for e in table if not e['once']])} 条可重复 / {len([e for e in table if e['once']])} 条一次"],
        ['来源', 'E01–E05 早期手写；M/L/S/P 来自 `P1-事件库-梗驱动-初审.xlsx` / `P1-事件库-人物梗-初审.xlsx`；N01–N20 人物梗试写（2026-11-07 审核通过）'],
        ['触发条件', '按代码里的 `requires` 翻译；「任意比赛周/阶段」= 运行时再看阶段和比赛周'],
        ['审查列', '填「通过 / 改 / 删」；要改就直接写怎么改'],
        ['复跑', 'npx vite-node scripts/06-events/dump_live.ts && PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_all_xlsx.py'],
    ]
    for r in notes:
        wn.append(r)
    style(wn, [12, 110])

    wb.save(OUT)
    print('saved', OUT, 'events', len(events), 'options', sum(len(e['options']) for e in events))


if __name__ == '__main__':
    main()
