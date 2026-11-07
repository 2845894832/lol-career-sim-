# 把 out-after224.json 里「重复 >3 次」的事件渲染成临时表。
# 用法：npx vite-node scripts/06-events/sim.ts after184
#       PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_hot_xlsx.py
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-高频事件-临时.xlsx'

NAVY = '1F3B57'
HEAD_FILL = PatternFill('solid', fgColor=NAVY)
HEAD_FONT = Font(color='FFFFFF', bold=True, size=10)
BODY = Font(size=10)
THIN = Side(style='thin', color='D6DCE5')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')

KIND = {'match': '比赛', 'life': '生活', 'special': '特殊'}
PHASE = {'growth': '成长', 'peak': '巅峰', 'decline': '衰退', 'any': '任何'}
COLS = ['#', 'ID', '类型', '阶段', '权重', '每局平均', '出现局数', '超过3次的局数/24', '总次数', '正文']
WIDTHS = [5, 7, 8, 8, 7, 9, 9, 15, 8, 70]


def load():
    data = json.loads((HERE / 'out-after224.json').read_text(encoding='utf-8'))
    live = json.loads((HERE / 'events-live.json').read_text(encoding='utf-8'))
    meta = {e['id']: e for e in live}
    over = {}
    for run in data['runs']:
        for eid, n in run['counts'].items():
            if n > 3:
                over[eid] = over.get(eid, 0) + 1
    rows = []
    for r in data['table']:
        e = meta.get(r['id'], {})
        rows.append({
            'id': r['id'],
            'kind': KIND.get(r['kind'], r['kind']),
            'phase': PHASE.get(e.get('phase', ''), e.get('phase', '')),
            'weight': e.get('weight', ''),
            'avg': r['avgPerRun'],
            'runs': r['runs'],
            'over3': over.get(r['id'], 0),
            'total': r['total'],
            'max': r['maxRepeat'],
            'text': e.get('text', ''),
        })
    return data, rows


def sheet(wb, title, rows):
    ws = wb.create_sheet(title)
    ws.append(COLS)
    for i, r in enumerate(rows, 1):
        ws.append([i, r['id'], r['kind'], r['phase'], r['weight'], r['avg'],
                   r['runs'], r['over3'], r['total'], r['text']])
    for c in range(1, len(COLS) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.column_dimensions[cell.column_letter].width = WIDTHS[c - 1]
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(COLS)):
        for cell in row:
            cell.font = BODY
            cell.border = BORDER
            cell.alignment = WRAP if cell.column >= 10 else Alignment(vertical='top', horizontal='center')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{ws.cell(row=1, column=len(COLS)).column_letter}{ws.max_row}'
    return ws


def main():
    data, rows = load()
    avg3 = sorted([r for r in rows if r['avg'] > 3], key=lambda r: -r['avg'])
    max3 = sorted([r for r in rows if r['max'] > 3], key=lambda r: (-r['max'], -r['avg']))

    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, f'平均>{3}次', avg3)
    sheet(wb, '单局曾超3次', max3)

    s = wb.create_sheet('说明')
    s.append(['口径', '8 种子 × 3 策略 = 24 局；每局 240 次抽事件；224 条事件库'])
    s.append(['平均>3次', f'{len(avg3)} 条（24 局总次数 ÷ 24 > 3）'])
    s.append(['单局曾超3次', f'{len(max3)} 条（某一局里出现 >3 次；均值可能 ≤3）'])
    s.append(['为什么生活事件多', '生活事件 240 周都能进池；比赛事件只在每年 26 个比赛周、且要已签约+教练信任≥25'])
    s.append(['备注', '只统计被抽到的事件；改权重是重新分配，不会降低总量'])
    for row in s.iter_rows(min_row=1, max_row=s.max_row, max_col=2):
        for cell in row:
            cell.font = BODY
            cell.alignment = WRAP
    s.column_dimensions['A'].width = 20
    s.column_dimensions['B'].width = 90
    wb.save(OUT)
    print('saved', OUT, 'avg>3', len(avg3), 'max>3', len(max3),
          'maxRepeat', data['summary']['maxRepeatInRun'])


if __name__ == '__main__':
    main()
