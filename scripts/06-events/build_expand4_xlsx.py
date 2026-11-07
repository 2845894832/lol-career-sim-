# 第四批扩写 20 条（比赛梗 10 + 人物梗 10）的待审表；不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_expand4_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from build_expand2_xlsx import ATTR, KIND, PHASE, RISK, MATCH_COND, cons, o

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-扩写20条-第四批-待审.xlsx'

EV = [
    dict(id='M58', src='解说毒奶（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='解说刚说你这局一次没死，你就在下一波团里倒了。',
         opts=[o('顺着解说笑', 'success', [], {'attrs': {'popularity': 1, 'mentality': 1}},
                 s_text='你复活后亮了个表情，弹幕说这波是玄学。'),
               o('不接这个梗', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'coachTrust': -2, 'attrs': {'mentality': -2}},
                 '你把耳机按紧，下一波团打了个一换三。',
                 '你越想越别扭，连着两波都没开到人。')]),
    dict(id='M59', src='场间香蕉（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='场间休息，你剥了根香蕉，导播把镜头切给了你。',
         opts=[o('对着镜头吃', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -2}, 'coachTrust': -1},
                 '你咬了一大口，现场笑成一片。',
                 '你吃得太急噎住了，镜头拍了整整五秒。'),
               o('放下香蕉', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把香蕉放回桌上，重新戴上耳机。')]),
    dict(id='M60', src='BP 最后一手（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='BP 最后一手留给你，教练问你想打谁。',
         opts=[o('点自己的绝活', 'roll', ['operation'],
                 {'attrs': {'operation': 2}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'operation': -2}},
                 '你锁下绝活，对面中单的表情变了。',
                 '绝活被对面三手针对，你整局没出过塔。'),
               o('听教练的', 'success', [], {'coachTrust': 2, 'attrs': {'awareness': 1}},
                 s_text='你锁了教练要的阵容，对线期稳得像训练赛。')]),
    dict(id='M61', src='满血回城（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='你满血按了回城，对面打野从草里走了出来。',
         opts=[o('取消回城', 'roll', ['operation'],
                 {'attrs': {'operation': 2}},
                 {'coachTrust': -2, 'attrs': {'operation': -2}},
                 '你在最后一秒取消，反手把对面打野秀了。',
                 '你按了取消，人还是被控在原地。'),
               o('硬着头皮回', 'success', [], {'attrs': {'mentality': -1}, 'coachTrust': -1},
                 s_text='你读完了回城，屏幕亮起来时只剩半血。')]),
    dict(id='M62', src='五人追辅助（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面五个人追着你们的辅助跑进了野区。',
         opts=[o('回头接应', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'teamfight': -2}},
                 '你们反包过去，把追人的五个全留在了野区。',
                 '你们冲进去救人，一起死在了三角草。'),
               o('卖了辅助', 'success', [], {'attrs': {'awareness': 1}, 'coachTrust': -1},
                 s_text='你转头把中塔推了，辅助在语音里叹了口气。')]),
    dict(id='M63', src='残血诱敌（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='你残血站在塔前，对面明显上头了。',
         opts=[o('继续勾引', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2, 'teamfight': 2}},
                 {'coachTrust': -3, 'attrs': {'mentality': -2}},
                 '对面越塔的一瞬间，你们的支援从后面到了。',
                 '你算错了一步，被对面先手秒在塔下。'),
               o('先撤回来', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你退回二塔，对面追进来被塔打了两下。')]),
    dict(id='M64', src='逆风守家（赛场梗）', kind='match', phase='decline', cond=MATCH_COND,
         text='三路兵线压进高地，你们只剩一座门牙。',
         opts=[o('守到最后一波', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'mentality': -2}},
                 '你们清了三波线，终于等到对面一波失误。',
                 '门牙倒了，你看着水晶的血条一点点见底。'),
               o('找机会开团', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 1},
                 {'coachTrust': -3, 'attrs': {'teamfight': -2}},
                 '你绕后开到对面的 C 位，一波翻了。',
                 '你开团的位置太深，队友没跟上。')]),
    dict(id='M65', src='游走支援（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='中路推完线，你有 20 秒可以游走。',
         opts=[o('往下路走', 'roll', ['laning'],
                 {'attrs': {'laning': 2}, 'coachTrust': 1},
                 {'coachTrust': -1, 'attrs': {'laning': -1}},
                 '你绕后包下，对面双人组一个没跑掉。',
                 '你走到河道，下路已经打完了。'),
               o('回中路推', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你回中路又推了一波，把对面的中塔磨掉一半。')]),
    dict(id='M66', src='决胜局选边（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='决胜局选边，裁判把硬币抛了起来。',
         opts=[o('选蓝色方', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你选了蓝方，先手抢下了对面最难受的那个英雄。'),
               o('让对面选', 'roll', ['mentality'],
                 {'coachTrust': 1},
                 {'coachTrust': -2, 'attrs': {'mentality': -1}},
                 '对面犹豫了半天，选了个自己不舒服的阵容。',
                 '对面选了最熟悉的阵容，你们从 BP 就开始难受。')]),
    dict(id='M67', src='红开还是蓝开（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='开局前，打野问你：红开还是蓝开？',
         opts=[o('先去打红', 'roll', ['awareness'],
                 {'attrs': {'awareness': 2}},
                 {'attrs': {'awareness': -2}},
                 '你们红开抓到了对面的换线。',
                 '你们红开扑了个空，对面已经三包一了。'),
               o('先去打蓝', 'success', [], {'coachTrust': 1, 'attrs': {'awareness': 1}},
                 s_text='你们蓝开稳住节奏，第一条小龙没让。')]),
    dict(id='N51', src='外卖被偷（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='外卖放在门口，你出去拿的时候只剩一个空袋子。',
         opts=[o('找前台理论', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'attrs': {'mentality': -2}, 'money': -400},
                 '前台调了监控，偷外卖的人把钱赔了。',
                 '监控是坏的，你又点了一份。'),
               o('自认倒霉', 'success', [], {'money': -400, 'attrs': {'mentality': -1}},
                 s_text='你重新点了份饭，等的时候把排位打完了。')]),
    dict(id='N52', src='队服尺码（人物梗）', kind='life', phase='growth', cond='已签约',
         text='新队服发下来，你的那件小了一码。',
         opts=[o('换大一码', 'success', [], {'attrs': {'popularity': 1}},
                 s_text='你换了大一码，拍照时终于不用吸肚子了。'),
               o('凑合着穿', 'success', [], {'stamina': -8, 'attrs': {'mentality': -1}},
                 s_text='你穿着紧身队服打完一整天，肩膀勒出了印子。')]),
    dict(id='N53', src='粉丝来信（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='粉丝寄来一封信，手写的，写了三页。',
         opts=[o('认真回信', 'success', [], {'attrs': {'popularity': 2, 'mentality': 1}},
                 s_text='你回了一张明信片，一个月后收到了第二封。'),
               o('收进盒子', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把信折好放进盒子，盒子已经快满了。')]),
    dict(id='N54', src='直播设备炸了（人物梗）', kind='life', phase='peak', cond='已签约',
         text='直播到一半，麦克风炸了，弹幕开始刷问号。',
         opts=[o('用手机播', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -2}, 'money': -600},
                 '你举着手机播完了剩下的两个小时。',
                 '手机也烫关机了，你只好提前下播。'),
               o('今天鸽了', 'success', [], {'attrs': {'mentality': 1}, 'money': -200},
                 s_text='你在动态里道了歉，说明天补上。')]),
    dict(id='N55', src='队友借钱（人物梗）', kind='life', phase='any', cond='已签约',
         text='队友私聊你：最近手头紧，能借点吗？',
         opts=[o('借他一点', 'roll', ['mentality'],
                 {'money': -500, 'coachTrust': 2},
                 {'money': -500, 'attrs': {'mentality': -2}},
                 '他下个月就还了，还请了你一顿夜宵。',
                 '钱借出去半年，他再没提过。'),
               o('说手头紧', 'success', [], {'coachTrust': -1, 'attrs': {'mentality': -1}},
                 s_text='你回了个表情，他没再问。')]),
    dict(id='N56', src='家里催相亲（人物梗）', kind='life', phase='peak', cond='无额外条件',
         text='家里打来电话，说给你安排了个相亲。',
         opts=[o('回去相亲', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}},
                 {'attrs': {'mentality': -2}, 'coachTrust': -1},
                 '你跟对方聊了半小时游戏，居然聊得不错。',
                 '你坐了二十分钟，全程不知道说什么。'),
               o('说在打比赛', 'success', [], {'attrs': {'mentality': -1}},
                 s_text='你说最近走不开，电话那头沉默了一会儿。')]),
    dict(id='N57', src='网吧被认出（人物梗）', kind='life', phase='growth', cond='无额外条件',
         text='你去网吧开黑，隔壁机位的人一直看你。',
         opts=[o('承认身份', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -1}, 'mentality': -1},
                 '你给他签了个名，他请你喝了瓶水。',
                 '他掏出手机拍你，你整局都没打好。'),
               o('说认错了', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你说自己只是长得像，他半信半疑地转回去了。')]),
    dict(id='N58', src='青训生来基地（人物梗）', kind='life', phase='peak', cond='已签约',
         text='青训生来基地参观，站在你身后看你打了一下午。',
         opts=[o('带他打一把', 'success', [], {'attrs': {'popularity': 2}, 'coachTrust': 1},
                 s_text='你带他打了一把自定义，他走的时候眼睛是亮的。'),
               o('让他先看', 'success', [], {'coachTrust': 1, 'attrs': {'mentality': 1}},
                 s_text='你继续打自己的，他安安静静看到天黑。')]),
    dict(id='N59', src='健身卡（人物梗）', kind='life', phase='decline', cond='无额外条件',
         text='基地楼下新开了家健身房，年卡打折。',
         opts=[o('去练两次', 'roll', ['mentality'],
                 {'stamina': 8, 'attrs': {'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你练了两次，脖子不酸了，觉也睡得沉了。',
                 '你第一次就练猛了，第二天抬不起胳膊。'),
               o('转手卖掉', 'success', [], {'money': 200},
                 s_text='你把卡挂上二手平台，第二天就有人接了。')]),
    dict(id='N60', src='机场误机（人物梗）', kind='life', phase='peak', cond='已签约',
         text='机场广播念到你的航班时，你还在安检排队。',
         opts=[o('改签下一班', 'success', [], {'money': -600, 'attrs': {'mentality': -1}},
                 s_text='你改签了下一班，到基地时训练赛已经开始了。'),
               o('求人插队', 'roll', ['popularity'],
                 {'attrs': {'popularity': -1}},
                 {'attrs': {'popularity': -3}, 'money': -600},
                 '前面的人认出了你，让你先过。',
                 '没人理你，你看着登机口关了。')]),
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
        ['来源', '比赛梗：解说毒奶、场间香蕉、BP 最后一手、满血回城被蹲、五人追辅助、残血诱敌、逆风守家、游走、选边、红蓝开；人物梗只用行为/场景，不用外号与真人名'],
        ['权重', '新条一律 weight 5'],
        ['条件', '比赛 10 条统一「已签约且能上场（信任 ≥25）」；生活按队内/个人加 signed'],
        ['审查列', '填「通过 / 改 / 删」'],
        ['状态', '只进这张表，没进 `src/data/events.ts`；代码现在是 164 条'],
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
