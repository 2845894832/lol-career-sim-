# 第五批：20 条「无条件 life/any」事件，专门往高频池里加分母；不写 src。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/build_expand5_life_xlsx.py
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from build_expand2_xlsx import ATTR, KIND, PHASE, RISK, cons, o

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'P1-事件库-扩写20条-第五批-待审.xlsx'

EV = [
    dict(id='L38', src='外卖备注（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='你备注了「少辣」，外卖打开是一片红。',
         opts=[o('将就吃掉', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -1}},
                 '你边喝水边吃完，下午训练一直跑厕所。',
                 '辣得你胃疼了一晚上，排位连跪三把。'),
               o('再点一份', 'success', [], {'money': -400},
                 s_text='你把这份推给队友，重新点了一份不辣的。')]),
    dict(id='L39', src='空调坏了（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='训练室空调坏了，屋里像蒸笼。',
         opts=[o('光膀子打', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}},
                 {'coachTrust': -1, 'attrs': {'mentality': -1}},
                 '你脱了外套继续打，直播间的弹幕笑疯了。',
                 '经理进来看了一眼，让你把衣服穿回去。'),
               o('搬去会议室', 'success', [], {'attrs': {'mentality': 1}, 'stamina': -8},
                 s_text='你们把电脑搬去会议室，挤了一下午。')]),
    dict(id='L40', src='凌晨四点排位（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='凌晨四点，你在排位里撞见了青训生。',
         opts=[o('认真打完', 'roll', ['operation'],
                 {'attrs': {'operation': 2}},
                 {'attrs': {'mentality': -2}, 'stamina': -8},
                 '你把他压了一整局，他加你好友说想学。',
                 '你困得手都在飘，被他单杀了两次。'),
               o('直接秒了', 'success', [], {'attrs': {'mentality': 1}, 'coachTrust': -1},
                 s_text='你退出游戏，第二天在基地见到他时有点心虚。')]),
    dict(id='L41', src='剪头发翻车（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='你去剪头发，理发师说「放心，我懂」。',
         opts=[o('戴帽子遮', 'success', [], {'attrs': {'popularity': -2, 'mentality': 1}},
                 s_text='你连戴了三天帽子，队友说像换了个人。'),
               o('剃成板寸', 'roll', ['popularity'],
                 {'attrs': {'popularity': 3}},
                 {'attrs': {'popularity': -2, 'mentality': -1}},
                 '你索性剃短，直播间说这发型挺精神。',
                 '你剃完照镜子，半天没说话。')]),
    dict(id='L42', src='直播标题（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='你开播前写标题：「今天绝对不鸽」。',
         opts=[o('播满四小时', 'roll', ['mentality'],
                 {'attrs': {'popularity': 2, 'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -1}},
                 '你播满四小时，下播时嗓子都哑了。',
                 '播到一半网断了，你在群里道了三次歉。'),
               o('改个标题', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把标题改成「随缘播」，心里一下轻松了。')]),
    dict(id='L43', src='粉丝送锦旗（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='粉丝把一面锦旗送到基地，写着「永远的神」。',
         opts=[o('挂训练室', 'roll', ['popularity'],
                 {'attrs': {'popularity': 2}, 'coachTrust': 1},
                 {'coachTrust': -1},
                 '锦旗挂上墙，教练路过看了一眼没说话。',
                 '经理说太招摇，让你先收起来。'),
               o('收进柜子', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你把锦旗叠好放进柜子，偶尔拿出来看一眼。')]),
    dict(id='L44', src='队服缩水（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='队服洗完缩了一码，袖口卡在手腕上。',
         opts=[o('硬穿一天', 'success', [], {'stamina': -8, 'attrs': {'mentality': -1}},
                 s_text='你穿了一整天，晚上肩膀勒出两道印。'),
               o('申请换新', 'roll', ['popularity'],
                 {'attrs': {'popularity': 1}},
                 {'coachTrust': -1, 'attrs': {'mentality': -1}},
                 '后勤很快给你换了件合身的。',
                 '申请表压了半个月，你只好继续穿。')]),
    dict(id='L45', src='眼药水过期（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='眼睛干得难受，你翻出一瓶眼药水，发现过期了。',
         opts=[o('照滴不误', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '滴完凉了一下，居然撑到了训练结束。',
                 '眼睛红了一晚上，队医把你骂了一顿。'),
               o('去药店买', 'success', [], {'money': -100, 'attrs': {'mentality': 1}},
                 s_text='你下楼买了瓶新的，顺便走了十分钟。')]),
    dict(id='L46', src='键盘进灰（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='键缝里全是灰，按下去有点粘。',
         opts=[o('拆开清理', 'roll', ['operation'],
                 {'attrs': {'operation': 1, 'mentality': 1}},
                 {'money': -800, 'attrs': {'mentality': -2}},
                 '你拆开擦干净，手感回来了。',
                 '你装回去多了两颗螺丝，只好换新键盘。'),
               o('凑合着用', 'success', [], {'attrs': {'operation': -1}},
                 s_text='你继续用，只是每次按键都得多用点力。')]),
    dict(id='L47', src='隔壁装修（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='隔壁开始装修，电钻声从早响到晚。',
         opts=[o('戴耳机硬练', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你把音量开到最大，居然练进去了。',
                 '你练了一下午，脑子里全是电钻声。'),
               o('去网吧躲', 'success', [], {'money': -200, 'attrs': {'mentality': 1}},
                 s_text='你抱着键盘去了楼下网吧，环境反而清净。')]),
    dict(id='L48', src='最后一串关东煮（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='便利店里只剩最后一串关东煮，你和队友同时伸手。',
         opts=[o('让给队友', 'success', [], {'coachTrust': 2, 'attrs': {'mentality': 1}},
                 s_text='队友愣了一下，第二天主动帮你带了早饭。'),
               o('先下手为强', 'roll', ['popularity'],
                 {'attrs': {'popularity': 1, 'mentality': 1}},
                 {'coachTrust': -1, 'attrs': {'mentality': -1}},
                 '你拿着串就跑，队友在后面笑骂。',
                 '你刚咬一口，发现是他先排的队。')]),
    dict(id='L49', src='小号被扒（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='你的小号被人扒出来了，里面全是吐槽队友的发言。',
         opts=[o('公开道歉', 'roll', ['popularity'],
                 {'attrs': {'popularity': 1, 'mentality': 1}},
                 {'attrs': {'popularity': -3}, 'coachTrust': -2},
                 '你发了条长文道歉，评论区慢慢缓和了。',
                 '道歉被截图做成表情包，传得到处都是。'),
               o('装死不回应', 'success', [], {'attrs': {'popularity': -1, 'mentality': -1}},
                 s_text='你三天没上微博，热度自己下去了。')]),
    dict(id='L50', src='牙套复诊（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='牙套该复诊了，医生说这次要加力。',
         opts=[o('按时复诊', 'success', [], {'money': -300, 'stamina': -8, 'attrs': {'mentality': -1}},
                 s_text='你复诊完疼了两天，只能吃流食。'),
               o('先往后拖', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'attrs': {'mentality': -1}, 'money': -300},
                 '你把复诊推到休赛期，暂时躲过一疼。',
                 '拖到牙套变形，医生说得多戴三个月。')]),
    dict(id='L51', src='快递柜超时（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='快递在柜子里放了三天，取件码过期了。',
         opts=[o('交超时费', 'success', [], {'money': -50},
                 s_text='你付了五块钱，取出一个不大的盒子。'),
               o('找客服理论', 'roll', ['mentality'],
                 {'money': 0, 'attrs': {'mentality': 1}},
                 {'attrs': {'mentality': -2}},
                 '客服帮你免了超时费，你心情不错。',
                 '你打了二十分钟电话，最后还是交了钱。')]),
    dict(id='L52', src='理发店办卡（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='理发师一边剪一边劝你办卡，说充两千送五百。',
         opts=[o('办一张卡', 'roll', ['popularity'],
                 {'money': -2000, 'attrs': {'popularity': 1}},
                 {'money': -2000, 'attrs': {'mentality': -2}},
                 '你办了卡，后来带队友一起来剪。',
                 '店两个月后关门了，卡里的钱没花完。'),
               o('婉言拒绝', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='你说下次再说，理发师的笑容淡了一点。')]),
    dict(id='L53', src='邻居的猫（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='邻居的猫蹲在基地门口，怎么赶都不走。',
         opts=[o('喂它一顿', 'roll', ['popularity'],
                 {'attrs': {'popularity': 1, 'mentality': 1}},
                 {'attrs': {'mentality': -1}, 'money': -50},
                 '猫赖着不走了，队员们轮流喂。',
                 '猫吃饱就跑，第二天还带了两个朋友来。'),
               o('打电话找主人', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='主人来接猫时连声道谢，还送了一袋水果。')]),
    dict(id='L54', src='体检验血（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='体检验血，护士说你的血管有点难找。',
         opts=[o('咬牙忍着', 'roll', ['mentality'],
                 {'attrs': {'mentality': 2}},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你一声没吭，护士说很少见。',
                 '扎了三针才抽出来，你手心全是汗。'),
               o('换一只手', 'success', [], {'attrs': {'mentality': 1}},
                 s_text='换左手一次就成了，你松了口气。')]),
    dict(id='L55', src='手机膜碎了（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='手机摔了一下，膜碎了，屏幕还能用。',
         opts=[o('凑合着用', 'success', [], {'attrs': {'mentality': -1}},
                 s_text='你用胶带粘了一下，裂纹越来越多。'),
               o('去贴新的', 'roll', ['mentality'],
                 {'attrs': {'mentality': 1}},
                 {'money': -100, 'attrs': {'mentality': -1}},
                 '你贴了张新的，顺便把手机壳也换了。',
                 '贴膜师傅手一抖，贴歪了两次。')]),
    dict(id='L56', src='深夜食堂（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='训练结束已过十二点，楼下只剩一家还开着。',
         opts=[o('吃碗热面', 'success', [], {'money': -30, 'stamina': 8, 'attrs': {'mentality': 1}},
                 s_text='你吃了碗热面，回去倒头就睡。'),
               o('直接回去睡', 'roll', ['mentality'],
                 {'stamina': 8},
                 {'stamina': -8, 'attrs': {'mentality': -2}},
                 '你饿着睡着，第二天居然精神不错。',
                 '你饿到凌晨三点，起来泡了碗面。')]),
    dict(id='L57', src='生日蛋糕（人物梗）', kind='life', phase='any', cond='无额外条件',
         text='队友偷偷订了个蛋糕，训练室灯突然灭了。',
         opts=[o('配合演戏', 'success', [], {'attrs': {'mentality': 2}, 'coachTrust': 1},
                 s_text='你假装被吓到，吹蜡烛时全队跟着起哄。'),
               o('先找开关', 'roll', ['awareness'],
                 {'attrs': {'awareness': 1, 'mentality': 1}},
                 {'attrs': {'mentality': -1}},
                 '你摸到开关，灯亮时蛋糕已经端出来了。',
                 '你把电闸拉了，整层楼黑了十分钟。')]),
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
    for col, w in zip('ABCDEFGHI', [7, 22, 7, 7, 16, 46, 7, 6, 10]):
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
        ['数量', f'{len(EV)} 条（全部 life / phase any / 无条件），{sum(len(e["opts"]) for e in EV)} 个选项'],
        ['目的', '往「每周都在池子里」的那 30–60 条里加分母，压掉 L38/N17 这类无条件生活事件的平均次数'],
        ['共同条件', 'kind=life、phase=any、requires 省略、once=false、weight 5'],
        ['审查列', '填「通过 / 改 / 删」'],
        ['状态', '只进这张表，没进 `src/data/events.ts`；代码现在是 204 条'],
    ]
    for r in notes:
        wn.append(r)
    for col, w in zip('AB', [12, 100]):
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
