# 生成“继续扩写 20 条”的待审表；不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_expand_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-扩写20条-待审.xlsx'

ATTR = {'operation': '操作', 'laning': '对线', 'teamfight': '团战',
        'awareness': '意识', 'mentality': '心态', 'popularity': '人气'}
KIND = {'match': '比赛', 'life': '生活', 'special': '特殊'}
PHASE = {'growth': '成长', 'peak': '巅峰', 'decline': '衰退', 'any': '任何'}
RISK = {'roll': '掷骰', 'success': '必成', 'fail': '必败'}

MATCH_COND = '已签约且能上场（信任 ≥25）'


def o(label, risk, attrs=(), success=None, fail=None, s_text='', f_text='', bonus=None, match_result=None):
    return dict(label=label, risk=risk, attrs=list(attrs), success=success, fail=fail,
                s_text=s_text, f_text=f_text, bonus=bonus, match_result=match_result)


# 每条：id / 来源梗 / 类型 / 阶段 / 条件 / 正文 / 选项
EV = [
    dict(id='M28', src='反向Q（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='中路一波团，你的关键技能甩向了反方向。弹幕已经炸了。',
         opts=[o('公屏打字道歉', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2, 'mentality': -3}},
                 {'attrs': {'popularity': -3, 'mentality': -4}},
                 '队友回了句「没事，下波」，弹幕也慢慢过去了。',
                 '对面把这句话截图发上超话，你成了当晚的笑话。'),
               o('装没看见', 'success', [], {'attrs': {'popularity': -2, 'mentality': -2}},
                 s_text='你面无表情地继续补刀，像什么都没发生。')]),
    dict(id='M29', src='拔网线翻盘（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面中单掉线了。裁判在语音里问：重赛，还是继续打？',
         opts=[o('同意重赛', 'success', [], {'coachTrust': 3, 'attrs': {'mentality': 2}},
                 s_text='对面重连回来，你们还是赢了，赛后握手时谁都没提这事。'),
               o('继续比赛', 'roll', ['teamfight'],
                 {'attrs': {'popularity': 3}, 'coachTrust': -2},
                 {'attrs': {'popularity': -2}, 'coachTrust': -4},
                 '你们推掉基地，弹幕却为「该不该重赛」吵了一整晚。',
                 '重连的对手像换了个人，你们被翻盘，官博评论区沦陷。')]),
    dict(id='M30', src='虐泉/冲泉水（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面只剩辅助活着，队友在语音里喊：冲泉水！',
         opts=[o('跟着冲泉', 'roll', ['teamfight'],
                 {'attrs': {'popularity': 4}, 'coachTrust': -3},
                 {'attrs': {'popularity': -3}, 'coachTrust': -5},
                 '泉水里亮起五道击杀提示，这一幕上了当日集锦。',
                 '你们全死在泉水里，对面顺势拿下远古龙，比赛被拖进决胜局。'),
               o('劝住队友', 'success', [], {'coachTrust': 2, 'attrs': {'mentality': 1}},
                 s_text='你说了一句「推基地」，队友居然真的听了。')]),
    dict(id='M31', src='四保一（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='教练在 BP 时问：这把要不要四保一，所有资源都给你？',
         opts=[o('打四保一', 'roll', ['teamfight'],
                 {'attrs': {'popularity': 3}, 'coachTrust': 2},
                 {'attrs': {'popularity': -2}, 'coachTrust': -4},
                 '四个人围着你打，你也没辜负他们，输出面板拉满。',
                 '你被集火秒了，四个人跟着一起没，赛后复盘沉默了很久。'),
               o('按常规打', 'success', [], {'coachTrust': 1, 'attrs': {'mentality': 1}},
                 s_text='你说不用，正常打，最后赢得很平稳。')]),
    dict(id='M32', src='大头亮牌（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='推掉高地，队友怂恿你亮个队标。',
         opts=[o('亮个队标', 'roll', ['mentality'],
                 {'attrs': {'popularity': 4}, 'coachTrust': -2},
                 {'attrs': {'popularity': -4}, 'coachTrust': -4},
                 '对面心态崩了，下一波直接投降，亮标图成了名场面。',
                 '两分钟后你们被零换五，那张亮标图被嘲了一整年。'),
               o('不亮队标', 'success', [], {'attrs': {'mentality': 1}, 'coachTrust': 1},
                 s_text='你点掉水晶，什么都没做，队友说你没劲。')]),
    dict(id='M33', src='五杀剑姬（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='你四杀了。最后一个残血，队友先出了手。',
         opts=[o('公屏打问号', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2, 'mentality': -2}},
                 {'attrs': {'popularity': -3, 'mentality': -3}},
                 '队友在语音里笑成一团，说下次一定让你。',
                 '问号被截图，成了你「输不起」的证据。'),
               o('说声没事', 'success', [], {'attrs': {'mentality': 2}, 'coachTrust': 1},
                 s_text='你说五杀不重要，赢才重要，队友反而有点不好意思。')]),
    dict(id='M34', src='一级团（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='开局对面五个人蹲在河道草里，你们一级团接不接？',
         opts=[o('直接接团', 'roll', ['teamfight'],
                 {'coachTrust': 2, 'attrs': {'teamfight': 2}},
                 {'coachTrust': -2, 'attrs': {'teamfight': -2}},
                 '一级团打了个一换三，开局就顺。',
                 '你们交了三个闪现，还送了一血。'),
               o('放掉一级团', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你们绕开草丛，安稳开局，解说夸了句稳。')]),
    dict(id='M35', src='换线（赛场梗）', kind='match', phase='growth', cond=MATCH_COND,
         text='教练想让你和上单换线，避开对面的强势对位。',
         opts=[o('主动换线', 'roll', ['laning'],
                 {'attrs': {'laning': 2, 'awareness': 1}},
                 {'attrs': {'laning': -3}, 'coachTrust': -2},
                 '你在上路压了对面三十刀，换线赚了。',
                 '你连塔皮都没吃到，等级还落后两级。'),
               o('坚持不换', 'success', [], {'attrs': {'mentality': 1}, 'coachTrust': -1},
                 s_text='你说不用换，自己能打，结果五五开。')]),
    dict(id='M36', src='大龙毁一生（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='对面在打大龙，你们只剩一次抢龙的机会。',
         opts=[o('进龙坑抢', 'roll', ['awareness'],
                 {'attrs': {'awareness': 3}, 'coachTrust': 2},
                 {'attrs': {'awareness': -2}, 'coachTrust': -4},
                 '你惩戒落下，大龙是你的，全场欢呼。',
                 '龙没抢到，人也没回来，对面一波结束比赛。'),
               o('放龙推塔', 'success', [], {'attrs': {'awareness': 2}, 'coachTrust': 1},
                 s_text='你们换掉了两座高地塔，把损失压到最小。')]),
    dict(id='M37', src='塔下辣舞（赛场梗）', kind='match', phase='peak', cond=MATCH_COND,
         text='胜局已定，队友在对面塔下跳起了舞。',
         opts=[o('跟着跳两下', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}, 'coachTrust': -2},
                 {'attrs': {'popularity': -3}, 'coachTrust': -3},
                 '对面直接点了投降，这段舞成了赛后热搜。',
                 '对面拖到后期，真把你们翻了，跳舞截图被挂了一周。'),
               o('点掉基地', 'success', [], {'coachTrust': 1, 'attrs': {'mentality': 1}},
                 s_text='你一个人把基地点掉，队友的舞没跳完。')]),
    dict(id='N21', src='忘关麦（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='直播到一半，你去倒水，麦没关。',
         opts=[o('将错就错', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -3, 'mentality': -2}},
                 '你清唱了两句，切片第二天挂上了热门。',
                 '你吐槽队友的话，被队友本人听见了。'),
               o('赶紧关麦', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你冲回来关麦，弹幕已经刷满了问号。')]),
    dict(id='N22', src='女装flag（人物梗）', kind='life', phase='peak', cond='已签约',
         text='你曾在直播里立誓：夺冠就穿女装。现在真夺冠了。',
         opts=[o('兑现承诺', 'roll', ['mentality'],
                 {'attrs': {'popularity': 5}, 'coachTrust': -2},
                 {'attrs': {'popularity': -3, 'mentality': -2}},
                 '照片上了热搜，粉丝数涨了一截，官博也转了。',
                 '照片被做成表情包，队里笑了你一整年。'),
               o('装作失忆', 'success', [], {'attrs': {'popularity': -2}},
                 s_text='你说那是玩笑，弹幕不依不饶，刷了一晚上「言而无信」。')]),
    dict(id='N23', src='妈妈粉（人物梗）', kind='life', phase='peak', cond='已签约',
         text='机场出口，一群阿姨举着你的灯牌喊「儿子」。',
         opts=[o('挨个合影', 'success', [], {'attrs': {'popularity': 2, 'mentality': 1}},
                 s_text='你挨个合影，她们往你包里塞了水果。'),
               o('低头快走', 'success', [], {'attrs': {'popularity': -1, 'mentality': 1}},
                 s_text='你戴上帽子快步走过，身后有人喊「注意身体」。')]),
    dict(id='N24', src='外卖投毒（人物梗）', kind='life', phase='peak', cond='已签约',
         text='有人晒出订单，说要在你们基地的外卖里动手脚。',
         opts=[o('直接报警', 'success', [], {'coachTrust': 2, 'attrs': {'popularity': 1}},
                 s_text='警察来了，那人删号道歉，基地门口多了一道安检。'),
               o('当个玩笑', 'roll', ['mentality'],
                 {},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '什么都没发生，但你一周没敢点外卖。',
                 '外卖真出了问题，队里拉肚子拉了三天，训练赛全推了。')]),
    dict(id='N25', src='小号被认出（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='你在韩服开小号练英雄，对面公屏打：这操作像是你。',
         opts=[o('大方承认', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2}},
                 {'attrs': {'popularity': -2}},
                 '对面加你好友，说从小看你比赛。',
                 '你的小号战绩被扒出来，英雄池全暴露了。'),
               o('死不承认', 'success', [], {'attrs': {'awareness': 1}},
                 s_text='你打完这局就换了号，对面在公屏骂了句装。')]),
    dict(id='N26', src='直播唱歌（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='直播间有人刷礼物点歌，你会的那首已经唱了三遍。',
         opts=[o('接着唱完', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3, 'mentality': -1}},
                 {'attrs': {'popularity': -2, 'mentality': -1}},
                 '弹幕跟着合唱，气氛好得像演唱会。',
                 '你破了音，切片标题写着「电竞死歌」。'),
               o('放原唱吧', 'success', [], {'attrs': {'popularity': 1}},
                 s_text='你放了原唱，弹幕说你偷懒。')]),
    dict(id='N27', src='生日应援（人物梗）', kind='life', phase='peak', cond='已签约',
         text='粉丝包下了市中心的大屏，循环播你的生日应援。',
         opts=[o('去拍张照', 'success', [], {'attrs': {'popularity': 2, 'mentality': 2}},
                 s_text='你站在大屏下拍了张照，配文只有两个字：收到。'),
               o('不去现场', 'success', [], {'attrs': {'mentality': 1, 'popularity': -1}},
                 s_text='你在基地多打了两把排位，队友替你发了条感谢。')]),
    dict(id='N28', src='染发赌约（人物梗）', kind='life', phase='peak', cond='已签约',
         text='队里打赌，谁输了谁把头发染成粉色。',
         opts=[o('认赌服输', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}, 'coachTrust': -1},
                 {'attrs': {'popularity': -2}, 'coachTrust': -2},
                 '粉色头发上了官博，评论区吵成两派。',
                 '染完第二天要拍定妆照，造型师脸都绿了。'),
               o('赖掉赌约', 'success', [], {'attrs': {'popularity': -1, 'mentality': 1}},
                 s_text='你请全队吃了顿火锅，赌约作废。')]),
    dict(id='N29', src='解说圣经（人物梗）', kind='life', phase='peak', cond='已签约',
         text='赛后采访，记者问你最后一波在想什么。',
         opts=[o('说句真话', 'roll', ['mentality'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -3}, 'coachTrust': -1},
                 '你说「在想输了怎么跟队友交代」，这句话被剪进了圣经。',
                 '你说的话被断章取义，超话骂了你三天。'),
               o('背好稿子', 'success', [], {'coachTrust': 1, 'attrs': {'mentality': 1}},
                 s_text='你说了段滴水不漏的场面话，记者有点失望。')]),
    dict(id='N30', src='粉丝送外设（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='粉丝寄来一套键鼠，附纸条：用这个打上王者。',
         opts=[o('换上试试', 'roll', ['operation'],
                 {'attrs': {'popularity': 2, 'operation': 1}},
                 {'attrs': {'operation': -1, 'mentality': -1}},
                 '你用这套外设赢了一整晚，还在直播里谢了他。',
                 '键盘手感不对，你连跪四把，又默默换了回来。'),
               o('收进柜子', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把盒子收进柜子，没舍得用。')]),
]


def cons(c):
    if not c:
        return '—'
    bits = []
    for k, v in (c.get('attrs') or {}).items():
        bits.append(f'{ATTR.get(k, k)}{v:+d}')
    for k, name in (('coachTrust', '信任'), ('stamina', '体力'), ('money', '金钱')):
        if k in c and c[k]:
            bits.append(f'{name}{c[k]:+d}')
    return ' '.join(bits) or '—'


def main():
    # 自检
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
    for col, w in zip('ABCDEFGHI', [7, 22, 7, 7, 24, 46, 7, 6, 10]):
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
        ['来源', '比赛梗取 `lol-memes/LOL赛场梗表.xlsx` 的行为类梗（反向Q、拔网线、虐泉、四保一、亮标、五杀、一级团、换线、大龙、塔下舞）；人物梗取行为/场景类，不用外号与真人名'],
        ['权重', '新条一律 weight 5（2026-11-07 你要求把 10 改成 5；代码里 77 条已改）'],
        ['条件', '比赛 10 条统一「已签约且能上场（信任 ≥25）」；生活按是否在队内加 signed，个人生活不设'],
        ['审查列', '填「通过 / 改 / 删」；改就直接写怎么改'],
        ['状态', '只进这张表，没进 `src/data/events.ts`；你审完再合并'],
    ]
    for r in notes:
        wn.append(r)
    for col, w in zip('AB', [10, 100]):
        wn.column_dimensions[col].width = w

    for sh in wb.worksheets:
        for row in sh.iter_rows(min_row=1, max_row=sh.max_row):
            for c in row:
                c.border = Border(left=Side(style='thin', color='D6DCE5'), right=Side(style='thin', color='D6DCE5'),
                                  top=Side(style='thin', color='D6DCE5'), bottom=Side(style='thin', color='D6DCE5'))
                c.alignment = Alignment(wrap_text=True, vertical='top')
                c.font = Font(color='FFFFFF', bold=True, size=10) if c.row == 1 else Font(size=10)
                if c.row == 1:
                    c.fill = PatternFill('solid', fgColor='1F3B57')

    wb.save(OUT)
    print('saved', OUT, 'events', len(EV), 'options', sum(len(e['opts']) for e in EV))


if __name__ == '__main__':
    main()
