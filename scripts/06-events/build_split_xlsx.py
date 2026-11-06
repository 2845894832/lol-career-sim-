# 按 v2 草稿把「日常/特殊事件」拆成掷骰表和必成表，各含汇总+明细两个 sheet。
# 用法（仓库根）：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_split_xlsx.py
import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((Path(__file__).with_name('draft80.json')).read_text(encoding='utf-8'))

SKILL = ('operation', 'laning', 'teamfight', 'awareness', 'popularity', 'mentality')
NAME = {'operation': '操作', 'laning': '对线', 'teamfight': '团战',
        'awareness': '意识', 'popularity': '人气', 'mentality': '心态'}

HEAD_FILL = PatternFill('solid', fgColor='1F4E79')
HEAD_FONT = Font(color='FFFFFF', bold=True, size=10)
ALT_FILL = PatternFill('solid', fgColor='EAF1F8')


def p_of(attrs, value):
    keys = attrs or ['teamfight']
    avg = sum(value for _ in keys) / len(keys)
    return max(0.05, min(0.95, avg / 100))


def cons_text(c):
    if not c:
        return ''
    parts = []
    for k, v in (c.get('attrs') or {}).items():
        parts.append(f'{NAME.get(k, k)}{v:+d}')
    for k, label in (('coachTrust', '信任'), ('stamina', '体力'), ('money', '钱'),
                     ('injury', '伤病'), ('maxStamina', '体力上限')):
        if k in c:
            parts.append(f'{label}{c[k]:+d}')
    if c.get('flag'):
        parts.append(f"标记{c['flag']}")
    return '，'.join(parts)


def style_sheet(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cell in ws[1]:
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical='top', wrap_text=True)


def sheet_summary(wb, rows, title):
    ws = wb.create_sheet('汇总')
    ws.append([title, '事件数', '掷骰选项', '必成选项', '必败选项', '总选项'])
    per = {}
    for eid, kind, phase, text, label, risk, attrs, *_ in rows:
        s = per.setdefault(eid, dict(kind=kind, phase=phase, text=text, roll=0, ok=0, bad=0))
        if risk == 'roll':
            s['roll'] += 1
        elif risk == 'success':
            s['ok'] += 1
        else:
            s['bad'] += 1
    for eid, s in per.items():
        ws.append([f"{eid}  {s['text']}", s['kind'], s['roll'], s['ok'], s['bad'],
                   s['roll'] + s['ok'] + s['bad']])
    style_sheet(ws, [52, 10, 10, 10, 10, 10])
    return ws


def sheet_detail(wb, rows, roll):
    ws = wb.create_sheet('明细')
    head = ['事件ID', '类型', '阶段', '事件正文', '选项', '掷骰/必成', '掷骰属性',
            '成功率(开局55)', '成功率(中期70)', '成功率(后期85)',
            '成功后果', '成功文案', '失败后果', '失败文案']
    ws.append(head)
    for eid, kind, phase, text, label, risk, attrs, succ, fail, stext, ftext in rows:
        if roll:
            p1, p2, p3 = (f'{p_of(attrs, v) * 100:.0f}%' for v in (55, 70, 85))
            kindtxt = '掷骰'
            attrtxt = '/'.join(NAME.get(a, a) for a in (attrs or ['teamfight']))
        else:
            # 必成/必败从不掷骰，没有「掷骰属性」，也不该有成功率。
            p1 = p2 = p3 = '—'
            kindtxt = '必成' if risk == 'success' else '必败'
            attrtxt = '—'
        ws.append([eid, kind, phase, text, label, kindtxt, attrtxt,
                   p1, p2, p3, cons_text(succ), stext or '', cons_text(fail), ftext or ''])
    style_sheet(ws, [8, 8, 8, 46, 18, 10, 12, 10, 10, 10, 30, 34, 30, 34])
    return ws


def collect(roll):
    out = []
    for e in DATA:
        # 有对手的事件（决赛等）走 matchRate，不是「日常掷骰」，单独看。
        if e['kind'] == 'match' or e.get('opponent') is not None:
            continue
        for o in e['options']:
            if (o['risk'] == 'roll') != roll:
                continue
            out.append([e['id'], e['kind'], e['phase'], e['text'], o['label'], o['risk'],
                        o.get('attrs'), o.get('success'), o.get('fail'),
                        o.get('successText'), o.get('failText')])
    return out


def build(fname, rows, roll, title):
    wb = Workbook()
    wb.remove(wb.active)
    sheet_detail(wb, rows, roll)
    sheet_summary(wb, rows, title)
    wb.move_sheet('汇总', offset=-1)
    path = ROOT / fname
    wb.save(path)
    print(f'{fname}: {len(rows)} 选项')
    return path


rolls = collect(True)
fixes = collect(False)
build('P1-掷骰选项-日常特殊-v2.xlsx', rolls, True, '掷骰事件（日常/特殊）')
build('P1-必成选项-日常特殊-v2.xlsx', fixes, False, '必成事件（日常/特殊）')
