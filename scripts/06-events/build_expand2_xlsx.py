# 第二批扩写 20 条（比赛梗 10 + 人物梗 10）的待审表；不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_expand2_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from build_expand_xlsx import ATTR, KIND, PHASE, RISK, MATCH_COND, cons, o

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-扩写20条-第二批-待审.xlsx'

EV = [
    dict(id='M38', src='空大（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='团战开打，你捏了半天的大招，放出去只打到空气。',
         opts=[o('立刻解释', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2, 'mentality': -1}},
                 {'attrs': {'popularity': -3, 'mentality': -2}},
                 '你在语音里说「手滑」，队友笑了一声。',
                 '没人接话，那波团你们输了。'),
               o('闭嘴打钱', 'success', [], {'attrs': {'awareness': 1, 'mentality': 1}},
                 s_text='你闷头补了十分钟刀，再没开过大。')]),
    dict(id='M39', src='闪现撞墙（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='越塔时你闪现撞上了墙，对面的控制正好接上。',
         opts=[o('认下这波', 'roll', ['mentality'],
                 {'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'popularity': -2}},
                 '你说这波我的，下一波打回来了。',
                 '队友没说话，那局你一直低着头。'),
               o('甩锅打野', 'roll', ['mentality'],
                 {'attrs': {'popularity': -1}},
                 {'attrs': {'popularity': -3, 'mentality': -2}},
                 '打野没接话，但之后没再来帮过你。',
                 '语音里吵起来，训练赛气氛僵了一晚。')]),
    dict(id='M40', src='伤害面板（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='赛后数据面板出来，你的伤害数字被截了图。',
         opts=[o('发微博自嘲', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -2, 'mentality': -2}},
                 '你转发说「数字挺吉利」，评论区笑成一片。',
                 '转发被解读成阴阳怪气，又吵了一轮。'),
               o('关掉评论', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把评论区关了，下一把打得格外凶。')]),
    dict(id='M41', src='泉水钩（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面辅助的钩子穿过兵线，把你们的 C 位拖进了泉水。',
         opts=[o('追进泉水', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 1},
                 {'attrs': {'teamfight': -2}, 'coachTrust': -3},
                 '你们反打，把对面堵在泉水里。',
                 '追进去的人一个没出来。'),
               o('放掉这波', 'success', [], {'attrs': {'awareness': 1}, 'coachTrust': 1},
                 s_text='你标记撤退，把损失停在一个人头。')]),
    dict(id='M42', src='四一分推（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='教练让你去带线，四个人在中路拖着。',
         opts=[o('一条线带到底', 'roll', ['laning'],
                 {'attrs': {'laning': 2}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'laning': -1}},
                 '你拆到高地，对面回防已经来不及。',
                 '你被抓，正面四个人也被开。'),
               o('带两波就回', 'success', [], {'attrs': {'awareness': 2}},
                 s_text='你带了两波线就回城，正面没崩。')]),
    dict(id='M43', src='一级学错（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='一级团开打，你才发现自己学错了技能。',
         opts=[o('硬着头皮打', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}},
                 {'coachTrust': -2, 'attrs': {'teamfight': -2}},
                 '少一个技能也打赢了，队友没发现。',
                 '你交了闪现还是死了，语音里沉默。'),
               o('先撤再说', 'success', [], {'attrs': {'awareness': 1, 'mentality': 1}},
                 s_text='你撤出草丛，回城换了技能。')]),
    dict(id='M44', src='决胜局手抖（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='决胜局，你的手开始抖，鼠标垫上全是汗。',
         opts=[o('深呼吸调整', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}},
                 {'attrs': {'mentality': -3}, 'coachTrust': -2},
                 '你盯着屏幕，把第一个技能稳稳放了出去。',
                 '第一波团你技能全空，队伍被打散。'),
               o('请求暂停', 'success', [], {'coachTrust': 1, 'stamina': -8},
                 s_text='裁判给了两分钟，你洗了把脸。')]),
    dict(id='M45', src='时空回溯（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='比赛打到一半，服务器崩了。裁判说可能要重开。',
         opts=[o('接受重开', 'success', [], {'attrs': {'mentality': 2}},
                 s_text='重开后你们照着刚才的节奏又打了一遍。'),
               o('反对重开', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2}, 'coachTrust': -2},
                 {'coachTrust': -3, 'attrs': {'popularity': -2}},
                 '你据理力争，裁判改判继续。',
                 '判罚没变，你还吃了个警告。')]),
    dict(id='M46', src='公屏打字（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面在公屏打字指挥，队友问你要不要回。',
         opts=[o('回他一句', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -2}, 'coachTrust': -1},
                 '你回了句「打你的」，对面真急了。',
                 '对面抓着这句话举报，裁判给了警告。'),
               o('屏蔽所有人', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你把公屏关了，专心打自己的。')]),
    dict(id='M47', src='泉水指挥（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='你第一个阵亡，只能在泉水里看队友打。',
         opts=[o('泉水指挥', 'roll', ['awareness'],
                 {'attrs': {'awareness': 2}, 'coachTrust': 1},
                 {'coachTrust': -2, 'attrs': {'awareness': -1}},
                 '你报了点，队友四打五打赢了。',
                 '你喊错了方向，队友全冲进人堆。'),
               o('闭嘴看戏', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你什么都没说，队友自己打赢了。')]),
    dict(id='N31', src='训练赛睡过头（人物梗）', kind='life', phase='growth', cond='已签约',
         text='训练赛定在下午两点，你醒来已经两点半。',
         opts=[o('冲去基地', 'roll', ['mentality'],
                 {'coachTrust': 1},
                 {'coachTrust': -3},
                 '你脸都没洗就上线，队友没说什么。',
                 '教练把这事记在了本子上。'),
               o('装病请假', 'success', [], {'coachTrust': -2, 'attrs': {'popularity': -1}},
                 s_text='你说发烧，队医来量了体温。')]),
    dict(id='N32', src='基地阿姨（人物梗）', kind='life', phase='any', cond='已签约',
         text='基地阿姨每天多做一份饭，说给你留着。',
         opts=[o('全部吃完', 'success', [], {'stamina': 8, 'attrs': {'mentality': 2}},
                 s_text='你连吃了两碗，阿姨笑得合不拢嘴。'),
               o('分给队友', 'success', [], {'coachTrust': 2, 'attrs': {'mentality': 1}},
                 s_text='你把那份饭推给晚归的队友。')]),
    dict(id='N33', src='亲戚借钱（人物梗）', kind='life', phase='peak', cond='已签约',
         text='一个多年没联系的亲戚发来消息：借点钱周转。',
         opts=[o('把钱借给他', 'roll', ['mentality'],
                 {'money': -800, 'attrs': {'mentality': 1}},
                 {'money': -800, 'attrs': {'mentality': -3}},
                 '钱转过去，对方说了声谢谢。',
                 '钱没了，人也没影了。'),
               o('说手头紧', 'success', [], {'attrs': {'mentality': -1}},
                 s_text='你回了句最近手头紧，对方没再说话。')]),
    dict(id='N34', src='同学群（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='高中同学群里有人发：这是我们班那个打职业的吗？',
         opts=[o('群里冒泡', 'success', [], {'attrs': {'popularity': 2, 'mentality': 1}},
                 s_text='你发了个表情，群里炸了。'),
               o('装死不说话', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你退了群，第二天又被拉回去。')]),
    dict(id='N35', src='小号点赞（人物梗）', kind='life', phase='peak', cond='已签约',
         text='你的小号点赞了一条骂教练的微博。',
         opts=[o('取消点赞', 'roll', ['awareness'],
                 {'attrs': {'awareness': 1}},
                 {'coachTrust': -2, 'attrs': {'mentality': -2}},
                 '你手快取消了，没人发现。',
                 '截图已经传开，教练问你是不是手滑。'),
               o('登门道歉', 'success', [], {'coachTrust': -1, 'attrs': {'mentality': 2}},
                 s_text='你去道歉，教练说下次别用小号。')]),
    dict(id='N36', src='被认错（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='商场里有人拍你肩膀：你是那个打野吧？',
         opts=[o('当场纠正', 'success', [], {'attrs': {'popularity': 1}},
                 s_text='你说我是中单，对方尴尬地笑了笑。'),
               o('顺着演下去', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -3}},
                 '你签了那个打野的名字，对方高兴坏了。',
                 '真打野本人转发了这条微博。')]),
    dict(id='N37', src='解说念错 ID（人物梗）', kind='life', phase='peak', cond='已签约',
         text='解说把你的 ID 念错了三次，弹幕在刷屏纠正。',
         opts=[o('发微博调侃', 'success', [], {'attrs': {'popularity': 3}},
                 s_text='你发了条「我叫这个」，解说转发了。'),
               o('装作没看见', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你当没看见，下一场解说又念错了。')]),
    dict(id='N38', src='广告 NG（人物梗）', kind='life', phase='peak', cond='已签约',
         text='广告拍摄，你对着镜头说了十遍同一句台词。',
         opts=[o('再来一遍', 'roll', ['mentality'],
                 {'attrs': {'popularity': 1, 'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '第十九遍过了，导演说你适合演戏。',
                 '你越说越僵，最后用了第一遍。'),
               o('要求改词', 'success', [], {'attrs': {'popularity': 1}, 'coachTrust': -1},
                 s_text='你把台词改成了自己的口头禅。')]),
    dict(id='N39', src='粉丝群吵架（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='粉丝群里两拨人吵起来了，@你去评理。',
         opts=[o('群里劝架', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -3}},
                 '你说了句都别吵，群里安静了。',
                 '你一开口，两拨人一起吵你。'),
               o('直接退群', 'success', [], {'attrs': {'mentality': 1, 'popularity': -1}},
                 s_text='你退了群，超话说你飘了。')]),
    dict(id='N40', src='体检报告（人物梗）', kind='life', phase='decline', cond='已签约',
         text='体检报告出来，医生的建议栏写了三行字。',
         opts=[o('认真看完', 'roll', ['mentality'],
                 {'stamina': 8, 'attrs': {'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你开始早睡，训练状态反而好了。',
                 '你看了两页就关掉，继续熬夜。'),
               o('收进抽屉', 'success', [], {'stamina': -8},
                 s_text='你把报告塞进抽屉，没告诉任何人。')]),
]


def main():
    for e in EV:
        assert len(e['text']) <= 50, (e['id'], len(e['text']))
        assert 2 <= len(e['opts']) <= 3, e['id']
        for op in e['opts']:
            assert 4 <= len(op['label']) <= 8, (e['id'], op['label'])
            if op['risk'] == 'roll':
                assert op['attrs'], (e['id'], op['label'])

    wb = Workbook()
    ws = wb.active
    ws.title = '事件'
    ws.append(['ID', '来源梗', '类型', '阶段', '触发条件', '正文', '选项数', '权重', '审查'])
    for e in EV:
        ws.append([e['id'], e['src'], KIND[e['kind']], PHASE[e['phase']], e['cond'],
                   e['text'], len(e['opts']), 5, ''])
    for col, w in zip('ABCDEFGHI', [7, 24, 7, 7, 24, 46, 7, 6, 10]):
        ws.column_dimensions[col].width = w

    wo = wb.create_sheet('选项')
    wo.append(['事件ID', '#', '选项', '风险', '加成', '成功后果', '失败后果', '成功文案', '失败文案', '审查'])
    for e in EV:
        for i, op in enumerate(e['opts'], 1):
            extra = '/'.join(ATTR.get(a, a) for a in op['attrs'])
            wo.append([e['id'], i, op['label'], RISK[op['risk']], extra or '—',
                       cons(op['success']), cons(op['fail']), op['s_text'], op['f_text'], ''])
    for col, w in zip('ABCDEFGHIJ', [7, 4, 16, 6, 14, 24, 24, 44, 44, 10]):
        wo.column_dimensions[col].width = w

    wn = wb.create_sheet('说明')
    notes = [
        ['项目', '内容'],
        ['数量', f'{len(EV)} 条（比赛 10 + 生活 10），{sum(len(e["opts"]) for e in EV)} 个选项'],
        ['来源', '比赛梗：空大、闪现撞墙、伤害面板、泉水钩、四一分推、一级学错、决胜局手抖、时空回溯、公屏打字、泉水指挥；人物梗只用行为/场景，不用外号与真人名'],
        ['权重', '新条一律 weight 5'],
        ['条件', '比赛 10 条统一「已签约且能上场（信任 ≥25）」；生活按队内/个人加 signed'],
        ['审查列', '填「通过 / 改 / 删」'],
        ['状态', '只进这张表，没进 `src/data/events.ts`；与第一批 20 条分开审'],
    ]
    for r in notes:
        wn.append(r)
    for col, w in zip('AB', [10, 100]):
        wn.column_dimensions[col].width = w

    for sh in wb.worksheets:
        for row in sh.iter_rows(min_row=1, max_row=sh.max_row):
            for c in row:
                c.border = Border(*[Side(style='thin', color='D6DCE5')] * 4)
                c.alignment = Alignment(wrap_text=True, vertical='top')
                c.font = Font(color='FFFFFF', bold=True, size=10) if c.row == 1 else Font(size=10)
                if c.row == 1:
                    c.fill = PatternFill('solid', fgColor='1F3B57')

    wb.save(OUT)
    print('saved', OUT, 'events', len(EV), 'options', sum(len(e['opts']) for e in EV))


if __name__ == '__main__':
    main()
