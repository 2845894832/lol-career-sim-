# -*- coding: utf-8 -*-
"""生成「人物梗 10 条试写」审阅表。只读梗表、只写 xlsx，不进 src。"""
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

OUT = 'P1-事件库-人物梗-10条-试写.xlsx'

# name, kind, phase, once, weight, requires, text, meme, origin, note, options
EV = [
    dict(
        id='N01', kind='match', phase='peak', once=False, weight=10,
        requires='signed && coachTrust >= 25',
        text='赛前采访你说，对面中单看到你的 ID 手会抖。开局三分钟，你在塔下被单杀。',
        meme='装杯', origin='文波装杯：戏称爱摆架子、爱秀操作。',
        note='把“赛前吹”改成“吹完被打脸”，给玩家三个台阶：打回去、发育、喊人。',
        opts=[
            ('亮回去', 'roll', '0.10', '{ attrs: { operation: 2, popularity: 2 }, coachTrust: 2 }', '{ attrs: { popularity: -3 }, coachTrust: -3 }',
             '你用同一个英雄在他塔下杀了回来。', '你越了两次塔，两次都死在里面。'),
            ('稳住补刀', 'roll', '0.05', '{ attrs: { laning: 2 } }', '{ attrs: { laning: -2, mentality: -2 } }',
             '你把线控在塔前，补刀一直压着他。', '刀没补到几个，镜头倒是一直给你。'),
            ('叫打野来', 'roll', '0.15', '{ attrs: { teamfight: 2 }, coachTrust: 2 }', '{ coachTrust: -2 }',
             '打野蹲了两分钟，他终于忍不住了。', '打野在上路露了头，对面中路直接推完了线。'),
        ],
    ),
    dict(
        id='N02', kind='match', phase='peak', once=False, weight=10,
        requires='signed && coachTrust >= 25',
        text='你拿到四杀。第五个人头，被辅助一记平 A 收走了。语音里安静了半秒。',
        meme='五杀', origin='五杀：职业生涯多次五杀，是常被提起的纪录。',
        note='不写“差一个五杀”，写“被队友抢走”，冲突落在队内关系上。',
        opts=[
            ('笑说没事', 'success', '—', '{ coachTrust: 3, attrs: { mentality: 1 } }', '—',
             '辅助连说了三个对不起，你笑得停不下来。', ''),
            ('当场质问', 'roll', '0.10', '{ attrs: { mentality: -1 }, coachTrust: 1 }', '{ coachTrust: -5, attrs: { mentality: -3 } }',
             '他解释了半天，队里有人笑出了声。', '话说重了，接下来十分钟没人报点。'),
            ('下波自己找回来', 'roll', '0.15', '{ attrs: { operation: 2, popularity: 2 }, flag: \'#五杀\' }', '{ attrs: { operation: -2 } }',
             '两分钟后，你在同一片野区拿了第五个人头。', '你追得太深，第五个人头变成了对面的。'),
        ],
    ),
    dict(
        id='N03', kind='match', phase='decline', once=False, weight=10,
        requires='signed && coachTrust >= 25',
        text='小龙团，你闪现过墙，撞在墙上。对面五个人隔着墙看了你一眼。',
        meme='闪现被塞恩撞死', origin='经典失误画面：闪现/走位失误被做成集锦。',
        note='把“被撞死”换成“自己撞墙”，失误归玩家，不归对手。',
        opts=[
            ('硬打', 'roll', '-0.10', '{ attrs: { teamfight: 2, popularity: 2 } }', '{ coachTrust: -4, attrs: { mentality: -3 } }',
             '墙那边的技能全空了，你反手开团。', '你倒在墙边，团战四打五。'),
            ('卖自己保队友', 'success', '—', '{ coachTrust: 2, attrs: { awareness: 1 } }', '—',
             '你往反方向跑，把三个人带进了野区。', ''),
            ('点信号撤', 'roll', '0.05', '{ attrs: { awareness: 2 } }', '{ attrs: { awareness: -2 } }',
             '队伍退到二塔，龙被对面拿走，但人都在。', '信号点晚了，撤退变成了逃跑。'),
        ],
    ),
    dict(
        id='N04', kind='match', phase='peak', once=False, weight=10,
        requires='signed && coachTrust >= 25',
        text='你假装回城，绕进龙坑，一个人打大龙。打到一半，对面辅助的路过眼亮了。',
        meme='灵性偷龙', origin='假装回城，趁对方松懈偷掉大龙完成翻盘。',
        note='和现有 M16 偷家、M11 抢龙区分：这条是“一个人偷”，赌的是对面没看见。',
        opts=[
            ('打完', 'roll', '-0.10', '{ attrs: { operation: 2, awareness: 2 }, coachTrust: 3 }', '{ coachTrust: -3, attrs: { mentality: -2 } }',
             '惩戒落下的时候，对面才刚走到河道。', '龙剩三百血，对面五个人到了。'),
            ('停手撤', 'success', '—', '{ attrs: { awareness: 1 } }', '—',
             '你从龙坑背面翻出去，一个人都没看见你。', ''),
            ('叫队友', 'roll', '0.10', '{ attrs: { teamfight: 2 }, coachTrust: 2 }', '{ coachTrust: -2 }',
             '四个人赶到，龙和团一起收了。', '队友到的时候，龙已经没了。'),
        ],
    ),
    dict(
        id='N05', kind='special', phase='peak', once=True, weight=2,
        requires='signed && honors 含 lpl-champion 或 worlds-champion',
        text='赛前直播你说，夺冠就穿女装。奖杯举起来那晚，弹幕翻出了录屏。',
        meme='袁儿无信', origin='赛前立 flag 夺冠就女装，夺冠后狡辩「没说拿什么冠军」。',
        note='保留“立 flag→翻旧账”的结构，不保留女装的具体人；兑现/狡辩/装失忆是三种人设。触发用 honors 里的冠军记录，不需要新字段。',
        opts=[
            ('兑现', 'success', '—', '{ attrs: { popularity: 4 }, flag: \'#女装\' }', '—',
             '你穿着裙子开了直播，热度冲到全站第一。', ''),
            ('狡辩没说哪个冠军', 'roll', '0.10', '{ attrs: { popularity: 2 } }', '{ attrs: { popularity: -4 } }',
             '弹幕骂了两天，然后把这句话做成了新的梗。', '录屏被翻出来，你越解释越像在赖账。'),
            ('装失忆', 'roll', '0.05', '{ attrs: { mentality: 1 } }', '{ coachTrust: -2, attrs: { popularity: -3 } }',
             '你坚称没说过，队友在评论区拆了台。', '粉丝把直播切片顶上了热搜。'),
        ],
    ),
    dict(
        id='N06', kind='life', phase='any', once=False, weight=10,
        requires='无',
        text='弹幕刷「妈妈爱你」，你顺口回了一句「谢谢妈」。直播间静了一秒。',
        meme='妈妈粉', origin='知道有妈妈粉，直播时干脆管粉丝叫「妈妈」。',
        note='不写“粉丝群体”，写“嘴比脑子快”的一秒；三个选项都是台阶，没有惩罚性选项。',
        opts=[
            ('顺着叫', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2 } }',
             '弹幕刷了一晚上「儿子」，你也没改口。', '有人截图发到论坛，标题写得很不好听。'),
            ('咳嗽转移', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '你咳了两声，弹幕自己把话题接走了。', ''),
            ('念 ID', 'roll', '0.05', '{ attrs: { popularity: 1, mentality: 1 } }', '{ attrs: { mentality: -1 } }',
             '你把那个 ID 念了三遍，他换了个更长的。', 'ID 里有脏字，直播间被警告了一次。'),
        ],
    ),
    dict(
        id='N07', kind='life', phase='growth', once=False, weight=10,
        requires='signed',
        text='你以为麦关了，说「这中单我带的动吗」。隔壁训练室的门开了。',
        meme='世界第一吹（忘关麦）', origin='与人聊天忘关直播，说了“队友是关键”一类的话。',
        note='把“忘关直播”改成“忘关麦”，战场从直播间挪进基地，冲突更近。',
        opts=[
            ('道歉', 'success', '—', '{ coachTrust: 3, attrs: { mentality: 1 } }', '—',
             '你当面把话收回，他拍了拍你的肩。', ''),
            ('硬撑', 'roll', '0.05', '{ attrs: { mentality: 1 }, coachTrust: -2 }', '{ coachTrust: -8, attrs: { mentality: -3 } }',
             '你说的是事实，他沉默了一会儿，没反驳。', '话传了一圈，训练赛没人给你让线。'),
            ('私下聊', 'roll', '0.10', '{ coachTrust: 2, attrs: { awareness: 1 } }', '{ attrs: { mentality: -2 } }',
             '你们在楼下便利店聊到凌晨，把话都说开了。', '他听完只说了一句「知道了」，之后再没提过。'),
        ],
    ),
    dict(
        id='N08', kind='life', phase='peak', once=False, weight=10,
        requires='signed && popularity >= 40',
        text='赛后采访你讲了五分钟赛区体系建设，弹幕开始刷「书记」。',
        meme='膏书记', origin='采访、发言一本正经像领导作报告。',
        note='把“外号”改成“弹幕现场反应”，玩家能看见自己把天聊死或接住。',
        opts=[
            ('继续讲', 'success', '—', '{ attrs: { popularity: 2, mentality: 1 } }', '—',
             '你把青训和赛训都讲了一遍，官媒转了这段。', ''),
            ('收住', 'success', '—', '{ attrs: { mentality: 1 }, coachTrust: 1 }', '—',
             '你笑了一下，把话头交给主持人。', ''),
            ('自嘲', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2 } }',
             '你说「那我以后少讲两句」，台下记者笑成一片。', '自嘲讲砸了，弹幕说你连玩笑都不会开。'),
        ],
    ),
    dict(
        id='N09', kind='life', phase='decline', once=False, weight=10,
        requires='signed',
        text='平台时长还差二十小时，你开着直播睡着了。醒来时在线人数是平时的三倍。',
        meme='大主播 + 卡比兽', origin='直播时间长、热度高；体型偏胖又爱吃爱睡。',
        note='两个梗拼一条：直播时长是压力，睡着是意外；不写“懒”，写“累到睡着”。',
        opts=[
            ('接着睡', 'roll', '0.10', '{ attrs: { popularity: 4 }, stamina: 8 }', '{ attrs: { popularity: -3 }, coachTrust: -2 }',
             '你翻了个身，弹幕开始给你盖被子。', '平台打来电话，说这算挂机。'),
            ('关掉', 'success', '—', '{ stamina: 8 }', '—',
             '你关了直播，睡了十二个小时。', ''),
            ('解释', 'roll', '0.05', '{ attrs: { popularity: 1 } }', '{ attrs: { popularity: -2 } }',
             '你说最近训练太满，弹幕反而心疼起来。', '你越解释越像在卖惨。'),
        ],
    ),
    dict(
        id='N10', kind='special', phase='peak', once=False, weight=2,
        requires='signed && popularity >= 50',
        text='群访你说了句口头禅。第二天，场馆里几千人跟着一起喊。',
        meme='芽儿呦 / 好吃好吃', origin='直播口头禅反复出现，成了个人标志。',
        note='不指定是哪句话（避免真人台词），只写“被全场接住”这件事。',
        opts=[
            ('挥手回应', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2 } }',
             '你把手举起来，声音又高了一层。', '你挥得太用力，被做成了鬼畜循环。'),
            ('装没听见', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '你低头走进通道，喊声跟了半条走廊。', ''),
            ('写进微博', 'roll', '0.10', '{ attrs: { popularity: 2 } }', '{ attrs: { popularity: -1 } }',
             '你发了四个字，点赞破了十万。', '文案打错了一个字，评论区全在纠错。'),
        ],
    ),
]

HDR = ['编号', '类型', '阶段', '一次', '权重', '触发条件', '正文', '字数', '来源梗', '梗的原文', '改编说明', '审查']
OPT_HDR = ['编号', '选项', '风险', '加成', '成功后果', '失败后果', '成功文案', '失败文案']

thin = Side(style='thin', color='CCCCCC')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
head_fill = PatternFill('solid', fgColor='1F3864')
head_font = Font(color='FFFFFF', bold=True, size=10)
wrap = Alignment(wrap_text=True, vertical='top')

wb = openpyxl.Workbook()
ws = wb.active
ws.title = '说明'

guide = [
    ('人物梗 10 条试写（未进代码）', 16, True),
    ('用途：让你判断“人物梗表怎么变成事件”的成分，通过后再决定要不要扩写、扩多少。', 10, False),
    ('', 10, False),
    ('来源：lol-memes/LOL人物梗表.xlsx（1000 行）。只取“行为/名场面”类梗，外号类不用；', 10, False),
    ('正文里 0 个真人名、0 个战队名、0 个选手外号；来源梗只留在表里，供你追溯。', 10, False),
    ('', 10, False),
    ('怎么读：先看“正文 + 三个选项”，再看“梗的原文”和“改编说明”，判断是不是你想要的味道。', 10, False),
    ('“审查”列留空，你可以填 通过 / 改 / 删；改的话把想改的那句写在旁边。', 10, False),
    ('', 10, False),
    ('成分（详见“成分”sheet）：比赛 4 / 生活 4 / 特殊 2；成长 1 / 巅峰 6 / 衰退 2 / 任意 1。', 10, False),
    ('与现有 84 条没有一对一重复；最近的邻居是 M16（偷家）、M11（抢龙）、L31（表情包），已在改编说明里区分。', 10, False),
    ('', 10, False),
    ('约束：正文 ≤50 字；选项 2–3 个；后果只用现有字段（attrs / stamina / money / coachTrust / flag 等）。', 10, False),
]
for i, (t, sz, bold) in enumerate(guide, start=1):
    c = ws.cell(row=i, column=1, value=t)
    c.font = Font(size=sz, bold=bold)
ws.column_dimensions['A'].width = 110

# 事件
we = wb.create_sheet('事件')
for j, h in enumerate(HDR, start=1):
    c = we.cell(row=1, column=j, value=h)
    c.fill, c.font, c.alignment, c.border = head_fill, head_font, Alignment(horizontal='center'), border
for i, e in enumerate(EV, start=2):
    row = [e['id'], e['kind'], e['phase'], '是' if e['once'] else '否', e['weight'],
           e['requires'], e['text'], len(e['text']), e['meme'], e['origin'], e['note'], '']
    for j, v in enumerate(row, start=1):
        c = we.cell(row=i, column=j, value=v)
        c.alignment, c.border = wrap, border
    if len(e['text']) > 50:
        raise SystemExit('%s 正文超 50 字：%d' % (e['id'], len(e['text'])))
for col, w in zip('ABCDEFGHIJKL', [7, 8, 7, 5, 5, 22, 46, 5, 14, 30, 38, 12]):
    we.column_dimensions[col].width = w
we.freeze_panes = 'A2'

# 选项
wo = wb.create_sheet('选项')
for j, h in enumerate(OPT_HDR, start=1):
    c = wo.cell(row=1, column=j, value=h)
    c.fill, c.font, c.alignment, c.border = head_fill, head_font, Alignment(horizontal='center'), border
r = 2
for e in EV:
    for (label, risk, bonus, succ, fail, st, ft) in e['opts']:
        vals = [e['id'], label, risk, bonus, succ, fail, st, ft]
        for j, v in enumerate(vals, start=1):
            c = wo.cell(row=r, column=j, value=v)
            c.alignment, c.border = wrap, border
        r += 1
for col, w in zip('ABCDEFGH', [7, 14, 7, 7, 40, 40, 34, 34]):
    wo.column_dimensions[col].width = w
wo.freeze_panes = 'A2'

# 成分
wf = wb.create_sheet('成分')
rows = [
    ('维度', '分布'),
    ('总数', '10 条 / 30 个选项'),
    ('类型', '比赛 4（N01–N04）· 生活 4（N06–N09）· 特殊 2（N05、N10）'),
    ('阶段', '成长 1（N07）· 巅峰 6（N01 N02 N04 N05 N08 N10）· 衰退 2（N03 N09）· 任意 1（N06）'),
    ('梗的来源类别', '赛场名场面 4（装杯、五杀、闪现撞墙、灵性偷龙）· 直播/粉丝 4（忘关麦、妈妈粉、大主播、口头禅）· 采访 1（膏书记）· 立 flag 1（女装）'),
    ('梗表用法', '只取“行为/名场面”，外号类（阿水、柴犬、大B老师等）一条没用；1000 行里可用的大约两成，其余是外号/谐音'),
    ('真人名/战队名', '0 / 0（正文与选项都不出现）'),
    ('与现有 84 条的关系', '无一对一重复；M16 偷家、M11 抢龙、L31 表情包、L21 直播合同最近，已在改编说明区分'),
    ('后果落点', 'attrs 与 coachTrust 为主，2 条各用一个 flag（#五杀 / #女装）；未用 honor / teamId / money'),
    ('待你判断', '这种“行为梗→两难选项”的比例够不够；要不要继续从这 20% 里再挑 20–40 条'),
]
for i, (a, b) in enumerate(rows, start=1):
    c1 = wf.cell(row=i, column=1, value=a)
    c2 = wf.cell(row=i, column=2, value=b)
    c1.font = Font(bold=True, size=10)
    c2.alignment = wrap
    c1.alignment = wrap
    if i == 1:
        c1.fill, c2.fill = head_fill, head_fill
        c1.font, c2.font = head_font, head_font
wf.column_dimensions['A'].width = 20
wf.column_dimensions['B'].width = 110

wb.save(OUT)
print('wrote', OUT, 'events', len(EV), 'options', sum(len(e['opts']) for e in EV))
