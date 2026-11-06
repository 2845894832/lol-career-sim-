# 事件链建议表（未进代码）。用法（仓库根）：
#   PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_chains_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'P1-事件链-建议.xlsx'

HEAD_FILL = PatternFill('solid', fgColor='1F4E79')
HEAD_FONT = Font(color='FFFFFF', bold=True, size=10)
ALT = PatternFill('solid', fgColor='EAF1F8')

ATTR = {'operation': '操作', 'laning': '对线', 'teamfight': '团战',
        'awareness': '意识', 'mentality': '心态', 'popularity': '人气'}


def cons(c):
    if not c:
        return '—'
    parts = []
    for k, v in (c.get('attrs') or {}).items():
        parts.append(f'{ATTR.get(k, k)}{v:+d}')
    for k, label in (('coachTrust', '信任'), ('stamina', '体力'), ('money', '钱'),
                     ('injury', '伤病'), ('maxStamina', '体力上限')):
        if k in c:
            parts.append(f'{label}{c[k]:+d}')
    if c.get('flag'):
        parts.append(f"置{c['flag']}")
    if c.get('clearFlag'):
        parts.append(f"清{c['clearFlag']}")
    return '，'.join(parts)


def o(label, risk, attrs=None, success=None, fail=None, st=None, ft=None):
    return dict(label=label, risk=risk, attrs=attrs or [], success=success, fail=fail, st=st, ft=ft)


# ---------------- 链定义 ----------------
CHAINS = [
    dict(
        id='C1', name='手腕', idea='伤病不是一次性结算，而是一条能走到退役的线',
        path='L19 → #手腕不适 → E05 → #伤停 → L37',
        edits='E05 两个选项都加 flag: \'#伤停\'（原本只 clearFlag）',
        nodes=[
            dict(stage='入口', eid='L19', status='现有', kind='life', phase='decline',
                 cond='已签约', text='手腕的旧伤在阴天又开始疼。',
                 note='「打封闭上场」成败都置 #手腕不适；「瞒着不说」失败则 injury+2，不进链',
                 opts=[]),
            dict(stage='中段', eid='E05', status='改造', kind='special', phase='any',
                 cond='#手腕不适', text='上周那下没缓过来。队医按了按你的手腕：「能打，但会疼。」',
                 note='两个选项都清 #手腕不适；改造＝同时置 #伤停，给收尾用',
                 opts=[]),
            dict(stage='收尾', eid='L37', status='新增', kind='life', phase='decline',
                 cond='#伤停 · 已签约',
                 text='医生说，要么手术，要么以后每逢阴天都疼。',
                 note='一次；把「疼」变成一次真选择',
                 opts=[
                     o('做手术，养半年', 'success', success={'injury': -2, 'coachTrust': -3},
                       st='手术很成功。等你回来，首发名单已经换了人。'),
                     o('保守治疗看看', 'roll', ['mentality'],
                       success={'stamina': 8, 'mentality': 1}, fail={'injury': 1, 'mentality': -1},
                       st='理疗师说，这手腕还能撑。', ft='第二天早上，你连拧毛巾都疼。'),
                     o('先打完这赛季', 'roll', ['operation'],
                       success={'coachTrust': 3}, fail={'injury': 2, 'coachTrust': -2},
                       st='你连着三场打满，没人看出异常。', ft='第五场，你连鼠标都握不稳。'),
                 ]),
        ]),
    dict(
        id='C2', name='金句', idea='一句采访的话，会自己长出后续（现有事件已经能连起来）',
        path='L12 → #金句 → L30 → #自嘲 → L31',
        edits='L30 加 requires #金句；L31 加 requires #自嘲（都在待审稿里，改条件即可）',
        nodes=[
            dict(stage='入口', eid='L12', status='现有', kind='life', phase='peak',
                 cond='（原条件）', text='客场夺冠，全场安静得像图书馆。',
                 note='「拿起话筒说话」成功置 #金句', opts=[]),
            dict(stage='中段', eid='L30', status='改造', kind='life', phase='peak',
                 cond='#金句', text='你那句采访被剪成短视频，播放量破了百万。',
                 note='「自己发一条」成功置 #自嘲；改造＝补 requires', opts=[]),
            dict(stage='收尾', eid='L31', status='改造', kind='life', phase='peak',
                 cond='#自嘲', text='粉丝把你的自嘲做成了表情包，传得到处都是。',
                 note='改造＝补 requires，不加新内容', opts=[]),
        ]),
    dict(
        id='C3', name='那条龙', idea='一次惩戒失误，会在训练室被反复提起',
        path='M11 → #丢龙 → L29 → #认过丢龙 → L40',
        edits='L29「认下来」成功加 flag: \'#认过丢龙\'',
        nodes=[
            dict(stage='入口', eid='M11', status='现有', kind='match', phase='peak',
                 cond='（原条件）', text='大龙还剩一格血，你的惩戒和对面打野同时按下。',
                 note='「拼这一手惩戒」失败置 #丢龙', opts=[]),
            dict(stage='中段', eid='L29', status='改造', kind='life', phase='peak',
                 cond='#丢龙', text='复盘会上，教练把丢龙那一帧暂停了。',
                 note='「认下来」成功加 #认过丢龙；改造＝补 requires + 标记', opts=[]),
            dict(stage='收尾', eid='L40', status='新增', kind='life', phase='peak',
                 cond='#认过丢龙',
                 text='训练赛大龙又被抢。打野把耳机摘了，看着你。',
                 note='一次；不重复「谁对谁错」，只给三种处理方式',
                 opts=[
                     o('先认下来再说', 'success', success={'attrs': {'mentality': 1}, 'coachTrust': 3},
                       st='你说这波我 call 的，下次我先到。'),
                     o('拉他一起复盘', 'roll', ['awareness'],
                       success={'attrs': {'awareness': 2}, 'coachTrust': 2}, fail={'attrs': {'mentality': -2}},
                       st='你们把那一帧看了二十遍，找到了问题。', ft='看到第三遍，他先走了。'),
                     o('下次我先到位', 'success', success={'attrs': {'awareness': 1}, 'stamina': -4},
                       st='你提前十秒站好位，惩戒没再丢过。'),
                 ]),
        ]),
    dict(
        id='C4', name='偷家', idea='成名的那一手，会被对手研究，然后逼你换活法',
        path='M16 → #偷家 → M22 → #被研究 → M26',
        edits='M22 任一成功分支加 flag: \'#被研究\'',
        nodes=[
            dict(stage='入口', eid='M16', status='现有', kind='match', phase='peak',
                 cond='（原条件）', text='对面五个人在打大龙，你带着兵线摸到了他们家高地。',
                 note='「一路偷到底」成功置 #偷家', opts=[]),
            dict(stage='中段', eid='M22', status='改造', kind='match', phase='peak',
                 cond='#偷家', text='对面赛前采访说，专门研究过你的偷家。',
                 note='改造＝补 requires + 成功置 #被研究', opts=[]),
            dict(stage='收尾', eid='M26', status='新增', kind='match', phase='peak',
                 cond='#被研究',
                 text='大龙刷新前，对面五个人从地图上消失了。边路兵线很好。',
                 note='一次；同一手，第二次做选择',
                 opts=[
                     o('还是照偷不误', 'roll', ['awareness'],
                       success={'attrs': {'popularity': 3}, 'coachTrust': 2},
                       fail={'attrs': {'popularity': -2}, 'coachTrust': -5},
                       st='你又一次站在他们家高地上，这次没人回防。',
                       ft='草丛里站着两个人。你连闪现都没按出来。'),
                     o('回头接这波团', 'roll', ['teamfight'],
                       success={'attrs': {'teamfight': 2}, 'coachTrust': 4},
                       fail={'attrs': {'mentality': -1}, 'coachTrust': -2},
                       st='你们五打四赢了团，大龙也顺手拿下。', ft='团开在龙坑口，你们被包了饺子。'),
                     o('让兵线自己走', 'success', success={'attrs': {'awareness': 1}, 'stamina': 4},
                       st='你没去。兵线自己拆了一座塔。'),
                 ]),
        ]),
    dict(
        id='C5', name='让二追三', idea='翻盘会变成标签，下一次决胜局它会先到场',
        path='M19 → #让二追三 → M23 → #被提起 → M27',
        edits='M23 任一成功分支加 flag: \'#被提起\'',
        nodes=[
            dict(stage='入口', eid='M19', status='现有', kind='match', phase='peak',
                 cond='（原条件）', text='0:2 落后，第三局 BP 前，休息室里没人说话。',
                 note='前两个选项成功置 #让二追三', opts=[]),
            dict(stage='中段', eid='M23', status='改造', kind='match', phase='peak',
                 cond='#让二追三', text='解说在赛前又提起了那场让二追三。',
                 note='改造＝补 requires + 成功置 #被提起', opts=[]),
            dict(stage='收尾', eid='M27', status='新增', kind='match', phase='peak',
                 cond='#被提起',
                 text='明天决胜局。走廊电视里，解说又提起那场让二追三。',
                 note='一次；这次是自己怎么过夜',
                 opts=[
                     o('早早上床睡觉', 'success', success={'stamina': 8, 'attrs': {'mentality': 1}},
                       st='你睡得很沉，梦里没有比分。'),
                     o('看录像到三点', 'roll', ['awareness'],
                       success={'attrs': {'awareness': 3}, 'stamina': -6},
                       fail={'stamina': -8, 'attrs': {'mentality': -2}},
                       st='你把对面的眼位记了满页，第二天真用上了。',
                       ft='天亮了，你只记住了输的那三局。'),
                     o('找教练聊两句', 'roll', ['mentality'], success={'coachTrust': 4},
                       fail={'coachTrust': -2},
                       st='教练说，明天你只管打，输了算我的。', ft='教练说，别想太多，然后先走了。'),
                 ]),
        ]),
]


def width(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
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


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = '链总览'
    ws.append(['链', '名字', '环数', '节点', '新写', '要改的旧事件', '标记路径', '为什么值得做'])
    for c in CHAINS:
        new = sum(1 for n in c['nodes'] if n['status'] == '新增')
        ws.append([c['id'], c['name'], len(c['nodes']),
                   ' → '.join(f"{n['eid']}({n['status']})" for n in c['nodes']),
                   f'{new} 条',
                   c['edits'], c['path'], c['idea']])
    width(ws, [6, 12, 6, 40, 8, 40, 44, 44])

    wd = wb.create_sheet('事件明细')
    wd.append(['链', '环', '事件ID', '状态', '类型', '阶段', '触发条件', '正文',
               '选项', '风险', '掷骰属性', '成功后果', '失败后果', '成功文案', '失败文案', '说明'])
    for c in CHAINS:
        for n in c['nodes']:
            if not n['opts']:
                wd.append([c['id'], n['stage'], n['eid'], n['status'], n['kind'], n['phase'],
                           n['cond'], n['text'], '（现有事件，选项见事件库）', '', '', '', '', '', '', n['note']])
                continue
            for op in n['opts']:
                wd.append([c['id'], n['stage'], n['eid'], n['status'], n['kind'], n['phase'],
                           n['cond'], n['text'], op['label'], op['risk'],
                           '/'.join(ATTR.get(a, a) for a in op['attrs']) or '—',
                           cons(op['success']), cons(op['fail']), op['st'] or '', op['ft'] or '', n['note']])
    width(wd, [6, 6, 8, 8, 8, 9, 18, 44, 16, 7, 10, 22, 22, 30, 30, 34])

    wn = wb.create_sheet('机制与待定')
    rows = [
        ['机制', '链只用「选项置 flag + 后续 requires」实现，不加新字段、不改类型。'],
        ['顺序', '同一标记的后续事件可能先于中段被抽到；所以中段成功分支再置一个标记'
                 '（#伤停 / #认过丢龙 / #被研究 / #被提起），收尾只认第二个标记。'],
        ['时序边界', '标记不会过期。现在只能靠 once + 阶段（成长/巅峰/衰退）把后一环限制在同一时期，'
                     '做不到「下一周」。要真正的紧邻，得给状态加「距上次事件第几周」——那是新字段。'],
        ['数量', '5 条链，新增 4 条事件（L37/L40/M26/M27），改 4 条旧事件的一行后果。'],
        ['工时', '4 条 × 20 分钟 ≈ 1.3 小时；加改 4 条旧事件、测试、审阅表重出，算半天。'],
        ['未进代码', '这份表只是建议；src 和草稿都没动。你圈「做 / 不做 / 改」之后我再落。'],
        ['待你定 1', '5 条里先做几条？还是全做？'],
        ['待你定 2', '伤病链收尾（L37）要不要能直接导向退役结局？现在只掉数值，不碰结局。'],
        ['待你定 3', '链的长度：现在最长 3 环（伤病/金句/大龙/偷家/让二追三都是 3 环）。要更长吗？'],
    ]
    wn.append(['项', '说明'])
    for r in rows:
        wn.append(r)
    width(wn, [12, 110])

    wb.save(OUT)

    bad = [(c['id'], n['eid'], len(n['text'])) for c in CHAINS for n in c['nodes']
           if n['status'] != '现有' and len(n['text']) > 50]
    long_labels = [(n['eid'], op['label']) for c in CHAINS for n in c['nodes'] for op in n['opts']
                   if not (4 <= len(op['label']) <= 8)]
    print('saved', OUT, 'chains', len(CHAINS), 'nodes', sum(len(c['nodes']) for c in CHAINS),
          'new', sum(1 for c in CHAINS for n in c['nodes'] if n['status'] == '新增'))
    print('正文超 50:', bad or '无')
    print('选项不在 4–8 字:', long_labels or '无')


if __name__ == '__main__':
    main()
