# 第三批扩写 20 条（比赛梗 10 + 人物梗 10）的待审表；不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_expand3_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from build_expand2_xlsx import ATTR, KIND, PHASE, RISK, MATCH_COND, cons, o

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-扩写20条-第三批-待审.xlsx'

EV = [
    dict(id='M48', src='反向闪现（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='被追到河道，你按下闪现，人却朝反方向飞了出去。',
         opts=[o('回身反打', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 1},
                 {'coachTrust': -3, 'attrs': {'teamfight': -2}},
                 '你回头一套，把追你的人按在墙上。',
                 '你交完闪现还是死了，镜头在你脸上停了很久。'),
               o('交闪跑路', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你绕进野区，捡回一条命。')]),
    dict(id='M49', src='丝血逃生（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='团战打完，你只剩 12 点血站在龙坑边。',
         opts=[o('原地回城', 'roll', ['awareness'],
                 {'attrs': {'laning': 2}},
                 {'coachTrust': -2, 'attrs': {'awareness': -1}},
                 '你贴着墙读回城，没人来找你。',
                 '一发远距离技能飞过来，屏幕黑了。'),
               o('继续补线', 'success', [], {'attrs': {'mentality': 1, 'laning': 1}},
                 s_text='你贴着墙补完这波线，才慢慢走回去。')]),
    dict(id='M50', src='大龙团灭（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='你们开大龙，对面从三个方向围了过来。',
         opts=[o('停手先打', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'teamfight': -1}},
                 '你们转身接团，把对面堵在河道。',
                 '龙没拿到，人也没了，语音里一片安静。'),
               o('硬打完这波', 'roll', ['mentality'],
                 {'coachTrust': 3},
                 {'coachTrust': -3, 'attrs': {'teamfight': -2}},
                 '惩戒落下，你们带着龙 buff 冲了出去。',
                 '龙剩一丝血，你们先团灭了。')]),
    dict(id='M51', src='越塔被反杀（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='你越塔追残血，防御塔的伤害先把你打死了。',
         opts=[o('认下这波', 'roll', ['mentality'],
                 {'coachTrust': 1},
                 {'attrs': {'popularity': -2}},
                 '你说这波急了，队友说下波稳点。',
                 '弹幕开始刷「越塔送」，你盯着屏幕没说话。'),
               o('怪队友没跟', 'success', [], {'attrs': {'popularity': -2, 'mentality': -2}},
                 s_text='语音里没人接话，之后也没人来帮你越塔。')]),
    dict(id='M52', src='偷塔差一刀（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='你摸到对面高地，水晶只剩一丝血。',
         opts=[o('再 A 一下', 'roll', ['operation'],
                 {'attrs': {'popularity': 3}, 'coachTrust': 2},
                 {'coachTrust': -3, 'attrs': {'popularity': -3}},
                 '水晶炸开的前一秒，对面的回防才刚到家。',
                 '你被回防的人按死，基地还剩 20 血。'),
               o('先撤再说', 'success', [], {'attrs': {'awareness': 2}},
                 s_text='你撤进野区，把对面的回防全引了出来。')]),
    dict(id='M53', src='双传送（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='队友喊双传送包下，你的传送还在冷却。',
         opts=[o('走路支援', 'roll', ['laning'],
                 {'attrs': {'laning': 2}, 'coachTrust': 1},
                 {'coachTrust': -2, 'attrs': {'laning': -1}},
                 '你绕后赶到，正好接上队友的控制。',
                 '你走到一半，下路已经打完了。'),
               o('不过去了', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你继续推线，把对面的塔磨掉了一半。')]),
    dict(id='M54', src='二级抓下（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='二级抓下，你蹲在草里等对面压线。',
         opts=[o('现在就上', 'roll', ['teamfight'],
                 {'attrs': {'teamfight': 2}, 'coachTrust': 2},
                 {'coachTrust': -2, 'attrs': {'teamfight': -2}},
                 '你闪顶接控，下路双杀。',
                 '对面打野也在，你们二打三。'),
               o('再等一等', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你多蹲了十秒，等到了对面交完技能。')]),
    dict(id='M55', src='视野全黑（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='地图全黑，队友还在往龙坑走。',
         opts=[o('去做视野', 'roll', ['awareness'],
                 {'attrs': {'awareness': 2}, 'coachTrust': 1},
                 {'coachTrust': -2, 'attrs': {'mentality': -2}},
                 '你插下的眼照出了对面的三个人。',
                 '你死在插眼的路上，龙也丢了。'),
               o('打信号撤', 'success', [], {'coachTrust': 1, 'attrs': {'awareness': 1}},
                 s_text='你连打三个撤退信号，队友停在了河道。')]),
    dict(id='M56', src='被让二追三（赛场梗）', kind='match', phase='decline', cond=MATCH_COND,
         text='你们 2:0 领先，对面连追两局，决胜局要开了。',
         opts=[o('稳住心态', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}, 'coachTrust': 2},
                 {'attrs': {'mentality': -3}, 'coachTrust': -2},
                 '你戴上耳机，说按前两局那么打。',
                 '你的手又开始抖，第一波团就空了技能。'),
               o('换套打法', 'success', [], {'attrs': {'awareness': 2}, 'coachTrust': -1},
                 s_text='你们换了一套阵容，对面明显没准备。')]),
    dict(id='M57', src='现场喊 ID（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='现场有人喊你的 ID，声音穿过了解说。',
         opts=[o('抬手回应', 'success', [], {'attrs': {'popularity': 2}},
                 s_text='你朝看台抬了下手，那片声音更大了。'),
               o('装没听见', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你盯着屏幕，把耳机又按紧了一点。')]),
    dict(id='N41', src='粉丝接机（人物梗）', kind='life', phase='peak', cond='已签约',
         text='凌晨的机场，十几个人举着你的灯牌。',
         opts=[o('停下来合影', 'success', [], {'attrs': {'popularity': 2}, 'stamina': -8},
                 s_text='你签完最后一个名字，天已经快亮了。'),
               o('走 VIP 通道', 'success', [], {'attrs': {'mentality': 1, 'popularity': -1}},
                 s_text='你从侧门出去，回头看了一眼那群人。')]),
    dict(id='N42', src='队友生日（人物梗）', kind='life', phase='any', cond='已签约',
         text='队友生日，群里在凑钱买礼物。',
         opts=[o('多出一点', 'success', [], {'money': -500, 'coachTrust': 3},
                 s_text='你把钱转过去，队友在群里发了一排问号。'),
               o('装没看见', 'success', [], {'coachTrust': -1},
                 s_text='你划走了消息，晚上吃饭时才想起来。')]),
    dict(id='N43', src='直播首秀（人物梗）', kind='life', phase='growth', cond='无额外条件',
         text='第一次开播，在线人数卡在 3 个人。',
         opts=[o('坚持播完', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你自说自话讲了两个小时，第二天多了几十个关注。',
                 '你对着三个人讲了两个小时，下播时嗓子哑了。'),
               o('直接关播', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你关了直播，把那三个观众忘在了脑后。')]),
    dict(id='N44', src='被举报挂机（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='队友在游戏里举报你挂机，系统发来警告。',
         opts=[o('提交申诉', 'roll', ['awareness'],
                 {'attrs': {'mentality': 1}},
                 {'attrs': {'mentality': -2}},
                 '客服看了录像，把警告撤了。',
                 '申诉被驳回，警告挂在了你的账号上。'),
               o('认下处罚', 'success', [], {'attrs': {'mentality': 1}, 'coachTrust': -1},
                 s_text='你点了确认，把游戏关了。')]),
    dict(id='N45', src='火锅被认出（人物梗）', kind='life', phase='peak', cond='已签约',
         text='教练请吃火锅，锅底刚上就被隔壁桌认出来了。',
         opts=[o('过去合个影', 'success', [], {'attrs': {'popularity': 2}, 'coachTrust': 1},
                 s_text='你擦了擦嘴过去合影，回来时肉已经老了。'),
               o('换去包间', 'success', [], {'money': -300, 'coachTrust': 1},
                 s_text='你们端着锅换进包间，教练说这顿他请。')]),
    dict(id='N46', src='租房漏水（人物梗）', kind='life', phase='decline', cond='无额外条件',
         text='你租的房子漏水，楼下邻居找上门。',
         opts=[o('赔钱了事', 'success', [], {'money': -600, 'attrs': {'mentality': -1}},
                 s_text='你转了钱，邻居走的时候还在念叨。'),
               o('去找房东', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'attrs': {'mentality': -2}, 'money': -300},
                 '房东第二天就带人来修了。',
                 '房东拖了半个月，你只好自己掏钱。')]),
    dict(id='N47', src='牙套（人物梗）', kind='life', phase='growth', cond='无额外条件',
         text='医生说得戴牙套，至少一年。',
         opts=[o('戴上牙套', 'success', [], {'attrs': {'popularity': -2, 'mentality': 1}},
                 s_text='你戴着牙套开了直播，弹幕说认不出来了。'),
               o('不戴牙套', 'success', [], {'stamina': -8, 'attrs': {'mentality': -1}},
                 s_text='你把诊断单折起来，塞进了包里。')]),
    dict(id='N48', src='老队友来电（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='以前的队友打来电话，问你最近怎么样。',
         opts=[o('聊了很久', 'success', [], {'attrs': {'mentality': 2}},
                 s_text='你们聊到手机发烫，才发现已经过去两个小时。'),
               o('说自己在忙', 'success', [], {'attrs': {'mentality': -1}},
                 s_text='你挂了电话，盯着训练室的白板发了会儿呆。')]),
    dict(id='N49', src='猫踩键盘（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='猫踩上键盘，把你的排位送进了游戏。',
         opts=[o('打完这局', 'roll', ['mentality'],
                 {'attrs': {'popularity': 1}},
                 {'attrs': {'mentality': -2}, 'coachTrust': -1},
                 '你一手抱猫一手操作，居然赢了。',
                 '队友骂了你一整局，猫在键盘上睡着了。'),
               o('拔掉电源', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把猫抱下来，顺手拔了电源。')]),
    dict(id='N50', src='微博热搜（人物梗）', kind='life', phase='peak', cond='已签约',
         text='你上了热搜，词条是「某选手 迟到」。',
         opts=[o('发微博解释', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -3}},
                 '你说路上堵车，评论区有人帮你作证。',
                 '解释被截成表情包，又挂了一天。'),
               o('不做回应', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你关了微博，第二天热搜自己掉了。')]),
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
        ['来源', '比赛梗：反向闪现、丝血、大龙团、越塔被反杀、偷塔差一刀、双传送、二级抓下、视野全黑、被让二追三、现场喊 ID；人物梗只用行为/场景，不用外号与真人名'],
        ['权重', '新条一律 weight 5'],
        ['条件', '比赛 10 条统一「已签约且能上场（信任 ≥25）」；生活按队内/个人加 signed'],
        ['审查列', '填「通过 / 改 / 删」'],
        ['状态', '只进这张表，没进 `src/data/events.ts`；代码现在是 124 条'],
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
