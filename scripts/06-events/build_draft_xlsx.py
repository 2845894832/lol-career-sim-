# 把 draft80.json 渲染成可逐条审阅的 xlsx。不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_draft_xlsx.py
import json
import importlib.util
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-84条-重写稿-v5.xlsx'

spec = importlib.util.spec_from_file_location('rd', HERE / 'rebuild_draft.py')
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

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


def cons(c):
    if not c:
        return ''
    bits = []
    for k, v in (c.get('attrs') or {}).items():
        bits.append(f'{ATTR.get(k, k)}{v:+d}')
    if 'coachTrust' in c:
        bits.append(f'信任{c["coachTrust"]:+d}')
    if 'stamina' in c:
        bits.append(f'体力{c["stamina"]:+d}')
    if 'money' in c:
        bits.append(f'金钱{c["money"]:+d}')
    if 'injury' in c:
        bits.append(f'伤病{c["injury"]:+d}')
    if c.get('flag'):
        bits.append(f'标记{c["flag"]}')
    return ' '.join(bits) or '—'


def cond_of(e):
    eid = e['id']
    if eid in rd.NEW_EVENTS:
        return rd.NEW_EVENTS[eid]['cond']
    if eid in rd.COND:
        return rd.COND[eid][1]
    if eid == 'E01' or eid.startswith('M') or eid in ('P01', 'P02', 'P07', 'P10', 'P11'):
        return '已签约 · 能上场（信任 ≥25）'
    return '（未改）'


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


def main():
    events = json.loads((HERE / 'draft80.json').read_text(encoding='utf-8'))

    wb = Workbook()
    ws = wb.active
    ws.title = '事件'
    ws.append(['ID', '类型', '阶段', '触发条件', '标签', '正文', '一次', '权重', '选项数', '审查'])
    for e in events:
        ws.append([e['id'], KIND[e['kind']], PHASE[e['phase']], cond_of(e), ' '.join(e['tags']),
                   e['text'], '是' if e['once'] else '', e['weight'], len(e['options']), ''])
    style(ws, [7, 8, 7, 26, 22, 44, 6, 6, 7, 10])

    wo = wb.create_sheet('选项')
    wo.append(['事件ID', '#', '选项', '风险', '属性', '成功后果', '失败后果', '成功文案', '失败文案', '审查'])
    for e in events:
        for i, o in enumerate(e['options'], 1):
            wo.append([e['id'], i, o['label'], o['risk'],
                       '/'.join(ATTR.get(a, a) for a in (o['attrs'] or [])),
                       cons(o['success']), cons(o['fail']),
                       o['successText'] or '', o['failText'] or '', ''])
    style(wo, [7, 4, 16, 6, 12, 26, 26, 40, 40, 10])

    wn = wb.create_sheet('说明')
    total = len(events)
    kinds = {}
    phases = {}
    for e in events:
        kinds[KIND[e['kind']]] = kinds.get(KIND[e['kind']], 0) + 1
        phases[PHASE[e['phase']]] = phases.get(PHASE[e['phase']], 0) + 1
    notes = [
        ['项目', '内容'],
        ['总数', f'{total} 条（原来那批“80 条”实际是 85 条：34 条表 + E01–E05 + 46 条；这次删 8 补 8）'],
        ['类型', ' / '.join(f'{k} {v}' for k, v in kinds.items())],
        ['阶段', ' / '.join(f'{k} {v}' for k, v in phases.items())],
        ['删除', '、'.join(sorted(rd.DELETE)) + '（转教练、合同/转会/换队、换位置/换人）'],
        ['新增', '、'.join(rd.NEW_EVENTS.keys())],
        ['条件规则', '比赛事件：已签约且信任 ≥25（能上场）；队内/基地/职业场景：已签约；个人生活：不设门槛；人气类：人气阈值'],
        ['事件链', '全部拆掉：L04 改人气 ≥50；E05 改伤停 ≥1；M22/M23/L29/L30/L31 改回普通比赛/生活条件'],
        ['待你确认', '1) 比赛门槛用 25（你 Q1 选保留 <25 替补线）；你 Q6 写的 45 与 25 冲突，我按 25 做'],
        ['待你确认', '2) 签约事件还没做：要把它改成「达标必定触发的单选项事件」，需要动 reduce.ts，等这批事件审完再做'],
        ['审查列', '填「通过 / 改 / 删」；改的话直接写要怎么改'],
    ]
    for r in notes:
        wn.append(r)
    style(wn, [12, 100])

    wb.save(OUT)
    print('saved', OUT, 'events', total, 'options', sum(len(e['options']) for e in events))


if __name__ == '__main__':
    main()
