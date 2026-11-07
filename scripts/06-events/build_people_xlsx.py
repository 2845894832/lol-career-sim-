# -*- coding: utf-8 -*-
"""生成「人物梗 10 条试写」审阅表。只读梗表、只写 xlsx，不进 src。"""
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

OUT = 'P1-事件库-人物梗-20条-试写.xlsx'

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
    dict(
        id='N11', kind='life', phase='growth', once=False, weight=10,
        requires='无',
        text='基地宿舍五个人一间，你的床垫铺在地上。半夜，隔壁床开始打呼。',
        meme='打地铺', origin='穷队五人挤一间，个子高的只能睡地上。',
        note='不写“穷”，写“睡不好”；三个选项都是熬过这一夜的办法，没有对错。',
        opts=[
            ('戴耳机睡', 'roll', '0.05', '{ stamina: 8 }', '{ stamina: -4, attrs: { mentality: -2 } }',
             '你睡到中午，醒来发现耳机没电了。', '耳机里的歌循环到天亮，你一句没记住。'),
            ('去客厅睡', 'success', '—', '{ stamina: 4 }', '—',
             '沙发短了一截，但至少安静。', ''),
            ('叫醒他', 'roll', '0.10', '{ attrs: { mentality: 1 }, coachTrust: 1 }', '{ coachTrust: -2, attrs: { mentality: -2 } }',
             '他翻了个身，呼噜停了十分钟。', '他醒了，然后两个人一起失眠。'),
        ],
    ),
    dict(
        id='N12', kind='life', phase='decline', once=False, weight=10,
        requires='无',
        text='排位连败，你说「去洗澡了」。一个小时后，直播间里还有两万人在等。',
        meme='洗澡狗', origin='排位劣势时说“我要去洗澡了”，然后挂机。',
        note='把“挂机”改成“直播间还在等”，压力从队友转到观众；不惩罚玩家，只让他选怎么收场。',
        opts=[
            ('真去洗', 'success', '—', '{ stamina: 8, attrs: { popularity: -1 } }', '—',
             '你洗完回来，直播间只剩一半人。', ''),
            ('回来接着打', 'roll', '0.10', '{ attrs: { mentality: 2, popularity: 2 } }', '{ attrs: { mentality: -3 }, coachTrust: -2 }',
             '你连赢三把，弹幕说这澡洗得值。', '你越打越输，最后一把直接秒了。'),
            ('挂个自动回复', 'roll', '0.05', '{ attrs: { popularity: 1 } }', '{ attrs: { popularity: -2 } }',
             '你留了句「马上回来」，粉丝在评论区接龙。', '自动回复挂了三天，超话开始传你退役。'),
        ],
    ),
    dict(
        id='N13', kind='match', phase='peak', once=False, weight=10,
        requires='signed && coachTrust >= 25',
        text='BP 最后一手，你锁了刀妹。对面打野在公屏打字：「哥，能换一个吗。」',
        meme='lwx no daomei', origin='排位撞见对手玩刀妹，公屏求他别玩。',
        note='把“排位求饶”搬进比赛 BP：换不换是面子与胜负的交换，不是操作题。',
        opts=[
            ('不换', 'roll', '0.10', '{ attrs: { operation: 2, popularity: 2 }, coachTrust: 2 }', '{ coachTrust: -3, attrs: { mentality: -2 } }',
             '你把他野区反了个干净，公屏再没响过。', '你被抓了七次，公屏开始刷「谢谢哥」。'),
            ('换一个', 'success', '—', '{ coachTrust: 1, attrs: { teamfight: 1 } }', '—',
             '你锁了版本答案，对面打野发了句「好人」。', ''),
            ('回他一句', 'roll', '0.05', '{ attrs: { popularity: 3 } }', '{ attrs: { mentality: -1 }, coachTrust: -2 }',
             '你回了句「那你别来」，全场笑了。', '话被截进集锦，标题写「赛前挑衅」。'),
        ],
    ),
    dict(
        id='N14', kind='match', phase='decline', once=True, weight=2,
        requires='signed && coachTrust >= 25',
        text='决赛输了。你坐在椅子上没动，对面五个人已经走过来。',
        meme='赛后痛哭', origin='决赛被打崩后坐在椅子上痛哭的名场面。',
        note='不写哭，写“坐着没动”；握手是职业礼仪，但玩家可以选择先缓一会儿。',
        opts=[
            ('站起来握手', 'success', '—', '{ attrs: { mentality: 2 }, coachTrust: 2 }', '—',
             '你一个个握过去，手有点抖。', ''),
            ('坐着缓一会儿', 'roll', '0.05', '{ attrs: { mentality: 1 } }', '{ attrs: { popularity: -3 }, coachTrust: -2 }',
             '你缓了十秒，还是站起来走了过去。', '镜头拍了你半分钟，弹幕说你输不起。'),
            ('直接回休息室', 'fail', '—', '—', '{ attrs: { popularity: -4 }, coachTrust: -4 }',
             '', '官方罚了你一笔，公告写「未完成赛后礼仪」。'),
        ],
    ),
    dict(
        id='N15', kind='special', phase='peak', once=True, weight=2,
        requires='signed && honors 含 lpl-champion 或 worlds-champion',
        text='官方问你要哪个英雄的皮肤。你说了两个，两个英雄的粉丝在论坛吵翻了。',
        meme='杰斯吧爆吧', origin='选冠军皮肤时两个英雄之争，两个贴吧互爆。',
        note='不指定英雄名，只保留“二选一被粉丝放大”的结构；后果全落人气与心态。',
        opts=[
            ('选第一个', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2 } }',
             '皮肤原画出来那天，那个英雄的登场率涨了一倍。', '另一个英雄的玩家刷了三天差评。'),
            ('让粉丝投票', 'roll', '0.05', '{ attrs: { popularity: 2 } }', '{ attrs: { popularity: -3 } }',
             '投票持续了两周，你每天转发一次。', '两边都觉得你在敷衍，投票成了骂战。'),
            ('两个都想要', 'roll', '0.05', '{ attrs: { popularity: 4 } }', '{ attrs: { popularity: -2 } }',
             '官方破例做了两款，你成了第一个。', '官方回了句「不行」，截图被传得到处都是。'),
        ],
    ),
    dict(
        id='N16', kind='life', phase='any', once=False, weight=10,
        requires='无',
        text='你被单杀，镜头切过来。你对着摄像头说了一句「我没哭」。',
        meme='主播没有哭', origin='直播嘴硬名言，配句是“还在嘴硬”。',
        note='把“嘴硬”做成可选的台阶：继续硬、笑一下、不解释；没有人真的哭。',
        opts=[
            ('继续嘴硬', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2, mentality: -2 } }',
             '这句话上了热搜，配图是你红着的眼睛。', '弹幕把你三年前的哭脸翻了出来。'),
            ('笑一下', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '你笑出了声，弹幕也跟着笑。', ''),
            ('不解释', 'roll', '0.05', '{ attrs: { mentality: 1 } }', '{ attrs: { mentality: -1 } }',
             '你低头继续补刀，镜头自己切走了。', '沉默被解读成破防，超话吵了一晚上。'),
        ],
    ),
    dict(
        id='N17', kind='life', phase='any', once=False, weight=10,
        requires='无',
        text='排位排队的间隙，你用画图软件画了只猫。第二天，它成了粉丝群头像。',
        meme='被电竞耽误的画家', origin='排位间隙用系统画图软件鼠绘，画功不错。',
        note='轻事件，只影响人气和训练状态；“画队友”那条把风险落在队内关系上。',
        opts=[
            ('接着画', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ coachTrust: -2 }',
             '你画了一整套，战队官方拿去做了表情包。', '画到凌晨，第二天的训练赛你全程在打哈欠。'),
            ('删掉', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '你清空了画布，粉丝说可惜。', ''),
            ('画队友', 'roll', '0.05', '{ attrs: { popularity: 2, mentality: 1 } }', '{ coachTrust: -3 }',
             '你把队友画成一排土豆，他笑了一晚上。', '队友觉得你在嘲讽他，训练室冷了两天。'),
        ],
    ),
    dict(
        id='N18', kind='special', phase='peak', once=True, weight=2,
        requires='signed && honors 含 lpl-champion 或 worlds-champion',
        text='决赛台下，你被镜头拍到在吃热狗。三个月后，官方把它做成了守卫皮肤。',
        meme='冠军热狗', origin='拳头以他吃热狗的照片为原型做了冠军守卫皮肤。',
        note='把真人照片换成“镜头拍到”，官方做皮肤保留；钱只给 400，不破坏经济平衡。',
        opts=[
            ('转发认领', 'roll', '0.10', '{ attrs: { popularity: 4 } }', '{ attrs: { popularity: -1 } }',
             '你转发了皮肤预览，配文「版权费呢」。', '有人翻出你比赛前吃坏肚子的旧账。'),
            ('装作不知道', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '你在采访里被问到，只说「挺好吃的」。', ''),
            ('直播吃给粉丝看', 'roll', '0.10', '{ attrs: { popularity: 3 }, money: 400 }', '{ attrs: { popularity: -2 } }',
             '那晚直播间全在刷热狗，商家找上门来。', '你吃撑了，第二天训练赛状态全无。'),
        ],
    ),
    dict(
        id='N19', kind='life', phase='any', once=False, weight=10,
        requires='无',
        text='一晚上排到同一个 ID 三把。第三把，他在公屏打了一句「又是你」。',
        meme='峡谷鬼见愁 / 诺导', origin='排位存在感太强，撞上的队友对手都发愁。',
        note='“又是你”是中性开场，三个选项分别是交朋友、打服他、躲开，都不带惩罚。',
        opts=[
            ('加个好友', 'roll', '0.10', '{ attrs: { popularity: 2, mentality: 1 } }', '{ attrs: { mentality: -1 } }',
             '你们双排了一晚上，他把把给你让线。', '他反手把你举报了，理由写「演员」。'),
            ('认真打', 'roll', '0.10', '{ attrs: { operation: 2 } }', '{ attrs: { mentality: -2 } }',
             '第三把你把他打到 0/8，他再没说话。', '你越认真越急，第三把输得最难看。'),
            ('换个号', 'success', '—', '{ stamina: 4 }', '—',
             '你换了个小号，清净了一晚上。', ''),
        ],
    ),
    dict(
        id='N20', kind='life', phase='any', once=False, weight=10,
        requires='无',
        text='粉丝见面会，你从头到尾只摆了一个点赞手势。第二天，有人做了九宫格对比图。',
        meme='人型合影立牌', origin='与谁合影都摆标准点赞手势，像会自动换装的立牌。',
        note='不写“敷衍”，写“被做成九宫格”；三个选项都是公关处理，代价只在人气。',
        opts=[
            ('发微博自嘲', 'roll', '0.10', '{ attrs: { popularity: 3 } }', '{ attrs: { popularity: -2 } }',
             '你转了那张图，说「姿势是练过的」。', '评论区说你连营业都不用心。'),
            ('下次换个姿势', 'success', '—', '{ attrs: { popularity: 1, mentality: 1 } }', '—',
             '第二场你比了个心，粉丝尖叫。', ''),
            ('不回应', 'success', '—', '{ attrs: { mentality: 1 } }', '—',
             '图传了几天，自己沉下去了。', ''),
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
    ('人物梗 20 条试写（未进代码）', 16, True),
    ('用途：让你判断“人物梗表怎么变成事件”的成分，通过后再决定要不要扩写、扩多少。', 10, False),
    ('', 10, False),
    ('来源：lol-memes/LOL人物梗表.xlsx（1000 行）。只取“行为/名场面”类梗，外号类不用；', 10, False),
    ('正文里 0 个真人名、0 个战队名、0 个选手外号；来源梗只留在表里，供你追溯。', 10, False),
    ('', 10, False),
    ('怎么读：先看“正文 + 三个选项”，再看“梗的原文”和“改编说明”，判断是不是你想要的味道。', 10, False),
    ('“审查”列留空，你可以填 通过 / 改 / 删；改的话把想改的那句写在旁边。', 10, False),
    ('', 10, False),
    ('成分（详见“成分”sheet）：比赛 6 / 生活 10 / 特殊 4；成长 2 / 巅峰 9 / 衰退 4 / 任意 5。', 10, False),
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
    ('总数', '20 条 / 60 个选项'),
    ('类型', '比赛 6（N01–N04、N13、N14）· 生活 10（N06–N09、N11、N12、N16、N17、N19、N20）· 特殊 4（N05、N10、N15、N18）'),
    ('阶段', '成长 2（N07 N11）· 巅峰 9（N01 N02 N04 N05 N08 N10 N13 N15 N18）· 衰退 4（N03 N09 N12 N14）· 任意 5（N06 N16 N17 N19 N20）'),
    ('梗的来源类别', '赛场名场面 6（装杯、五杀、闪现撞墙、灵性偷龙、刀妹公屏、赛后痛哭）· 直播/粉丝 9（忘关麦、妈妈粉、大主播、口头禅、洗澡挂机、嘴硬、鼠绘、排位撞车、合影）· 采访 1（膏书记）· 立 flag 1（女装）· 生活/荣誉 3（打地铺、冠军皮肤、冠军热狗）'),
    ('梗表用法', '只取“行为/名场面”，外号类（阿水、柴犬、大B老师等）一条没用；1000 行里可用的大约两成，其余是外号/谐音'),
    ('真人名/战队名', '0 / 0（正文与选项都不出现）'),
    ('与现有 84 条的关系', '无一对一重复；M16 偷家、M11 抢龙、L31 表情包、L21 直播合同、L28 退役仪式最近，已在改编说明区分'),
    ('后果落点', 'attrs 与 coachTrust 为主，2 条各用一个 flag（#五杀 / #女装），1 条给 money 400；未用 honor / teamId'),
    ('待你判断', '这 20 条的比例与味道对不对；对的话再按同口径挑 20–40 条'),
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
