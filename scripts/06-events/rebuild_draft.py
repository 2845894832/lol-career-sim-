# 依据 2026-11-06 的拍板重写事件库草稿（不进 src，只产出可审查的草稿）。
# 用法（仓库根）：PYTHONIOENCODING=utf-8 <python> scripts/06-events/rebuild_draft.py
import io
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC80 = Path(__file__).with_name('_ev80.ts')
DRAFT = Path(__file__).with_name('_draft80.ts')
JSON_OUT = Path(__file__).with_name('draft80.json')

MATCH = "(s) => s.signed && s.coachTrust >= CONFIG.match.benchThreshold"

# id -> (TS 条件, 审查表里的中文说明)
COND = {
    'E01': (MATCH, '已签约 · 能上场（信任 ≥25）'),
    'E04': ("(s) => s.signed", '已签约'),
    'E05': ("(s) => s.signed && s.injury >= 1", '已签约 · 伤停 ≥1'),
    'L02': ("(s) => s.signed", '已签约'),
    'L03': ("(s) => s.signed", '已签约'),
    'L04': ("(s) => s.attrs.popularity >= 50", '人气 ≥50 · 一次'),
    'L05': ("(s) => s.signed", '已签约'),
    'L06': ("(s) => s.attrs.popularity >= 50", '人气 ≥50'),
    'L07': ("(s) => s.signed && s.coachTrust <= 30", '已签约 · 信任 ≤30'),
    'L08': ("(s) => s.signed && s.week <= CONFIG.career.matchWeeksPerYear", '已签约 · 比赛周'),
    'L09': ("(s) => s.signed", '已签约'),
    'L10': ("(s) => s.signed && s.coachTrust <= 50", '已签约 · 信任 ≤50'),
    'L11': (None, '无门槛（路人期）'),
    'L12': ("(s) => s.signed", '已签约'),
    'L14': (None, '无门槛（路人期）'),
    'L15': ("(s) => s.signed", '已签约'),
    'L16': (None, '无门槛（路人期）'),
    'L18': ("(s) => s.signed && s.attrs.popularity >= 60", '已签约 · 人气 ≥60'),
    'L19': ("(s) => s.signed", '已签约'),
    'L21': ("(s) => s.signed", '已签约'),
    'L22': ("(s) => s.signed", '已签约'),
    'L24': ("(s) => s.signed", '已签约'),
    'L25': ("(s) => s.signed", '已签约'),
    'L26': ("(s) => s.signed", '已签约'),
    'L28': ("(s) => s.signed", '已签约'),
    'L29': ("(s) => s.signed", '已签约'),
    'L30': ("(s) => s.signed && s.attrs.popularity >= 60", '已签约 · 人气 ≥60'),
    'L31': ("(s) => s.signed && s.attrs.popularity >= 50", '已签约 · 人气 ≥50'),
    'L32': ("(s) => s.signed", '已签约'),
    'P03': ("(s) => s.signed", '已签约'),
    'P04': ("(s) => s.signed && s.attrs.popularity >= 60", '已签约 · 人气 ≥60'),
    'P05': ("(s) => s.attrs.popularity >= 40", '人气 ≥40'),
    'P06': (None, '无门槛（路人期）'),
    'P09': ("(s) => s.signed", '已签约'),
    'S02': ("(s) => s.signed && s.year === 3 && s.week <= CONFIG.career.matchWeeksPerYear", '第 3 年 · 已签约 · 比赛周'),
    'S03': ("(s) => s.signed && s.year === 1 && s.week <= CONFIG.career.matchWeeksPerYear", '第 1 年 · 已签约 · 比赛周'),
    'S04': (None, '无门槛（青训期）'),
    'S05': ("(s) => s.signed", '已签约'),
    'S06': (None, '无门槛（路人期）'),
    'S07': ("(s) => s.signed", '已签约'),
    'S08': (None, '无门槛（路人期）'),
    'S09': ("(s) => s.signed", '已签约'),
    'S10': ("(s) => s.signed", '已签约'),
    'M04': (MATCH, '已签约 · 能上场（信任 ≥25）'),
    'M05': ("(s) => s.signed && s.actionGrid.includes('stream')", '已签约 · 本周直播'),
}

DELETE = {'S01', 'P08', 'P12', 'L13', 'S11', 'L17', 'L20', 'L23', 'L27'}

NEW_EVENTS = {
    'L33': dict(kind='life', phase='peak', tags=['#生活', '#舆论', '#集锦'], once=False, weight=10,
                requires="(s) => s.signed && s.attrs.popularity >= 40",
                cond='已签约 · 人气 ≥40',
                text='这场比赛被剪成「总嚼赛」集锦，弹幕说两边都在下饭。',
                options=[
                    dict(label='跟着自嘲', risk='success', success={'attrs': {'popularity': 2, 'mentality': 1}},
                         successText='你在评论区回了一句：确实，饭管够。'),
                    dict(label='让运营删', risk='roll', attrs=['popularity'],
                         success={'attrs': {'popularity': 2}},
                         fail={'attrs': {'popularity': -2, 'mentality': -2}},
                         successText='运营删得很快，截图传得更快。',
                         failText='运营回了你一个问号，然后没再理你。'),
                ]),
    'L34': dict(kind='life', phase='peak', tags=['#生活', '#对手', '#习惯'], once=False, weight=10,
                requires="(s) => s.signed", cond='已签约',
                text='对面中单掏出卷尺，量了量键盘和显示器的距离。',
                options=[
                    dict(label='借他尺子', risk='success', success={'attrs': {'popularity': 2, 'awareness': 1}},
                         successText='你把尺子递过去，全场笑出了声。'),
                    dict(label='不理会', risk='success', success={'attrs': {'mentality': 2}},
                         successText='你戴上耳机，把注意力放回补刀。'),
                ]),
    'L35': dict(kind='life', phase='any', tags=['#直播', '#水友赛', '#翻车'], once=False, weight=10,
                requires="(s) => s.attrs.popularity >= 40", cond='人气 ≥40',
                text='直播水友赛，你被一个钻石水友单杀了。弹幕全是问号。',
                options=[
                    dict(label='认了', risk='success', success={'attrs': {'popularity': 2, 'mentality': 1}},
                         successText='你说：这水友有点东西。弹幕笑成一片。'),
                    dict(label='说设备卡', risk='roll', attrs=['popularity'],
                         success={'attrs': {'popularity': 2}},
                         fail={'attrs': {'popularity': -3, 'mentality': -2}},
                         successText='你换了台电脑重开，又赢回来了。',
                         failText='弹幕开始刷：设备也救不了你。'),
                ]),
    'L36': dict(kind='life', phase='growth', tags=['#生活', '#基地', '#乌龙'], once=False, weight=10,
                requires="(s) => s.signed", cond='已签约',
                text='保洁阿姨拔了基地网线，训练赛掉线，对面以为你们跑了。',
                options=[
                    dict(label='重连道歉', risk='roll', attrs=['awareness'],
                         success={'attrs': {'awareness': 2}, 'coachTrust': 2},
                         fail={'coachTrust': -3},
                         successText='你第一个连回去，对面接受了道歉。',
                         failText='重连回来，对面已经开了下一把。'),
                    dict(label='怪保洁', risk='fail', fail={'attrs': {'mentality': -2}},
                         failText='话说出口，训练室里没人接。'),
                ]),
    'S12': dict(kind='special', phase='peak', tags=['#特殊', '#解说', '#泄密'], once=True, weight=1,
                requires="(s) => s.signed", cond='已签约 · 一次',
                text='解说在台上念出了你们的秘密选人，对面教练笑了。',
                options=[
                    dict(label='临时换阵', risk='roll', attrs=['awareness'],
                         success={'attrs': {'awareness': 3}},
                         fail={'coachTrust': -2},
                         successText='你们换了套阵容，对面愣了一整局。',
                         failText='换阵没练过，十五分钟就崩了。'),
                    dict(label='照原计划打', risk='success', success={'attrs': {'teamfight': 2}},
                         successText='你把那套阵容打成了教学局。'),
                ]),
    'S13': dict(kind='special', phase='any', tags=['#特殊', '#现场', '#音乐'], once=True, weight=2,
                requires="(s) => s.signed", cond='已签约 · 一次',
                text='场间响起「丢丢丢」，全场跟着拍手，你的紧张散了一半。',
                options=[
                    dict(label='跟着哼', risk='success', success={'attrs': {'mentality': 3}},
                         successText='你跟着哼完，走进选手通道时脚步轻了。'),
                    dict(label='戴上耳机', risk='success', success={'attrs': {'awareness': 2}},
                         successText='你把噪音隔在外面，把注意力收回屏幕上。'),
                ]),
    'S14': dict(kind='special', phase='decline', tags=['#特殊', '#舆论', '#垫底'], once=True, weight=1,
                requires="(s) => s.signed", cond='已签约 · 一次',
                text='卫冕冠军这赛季垫底，网友把你们叫「一年级五班」。',
                options=[
                    dict(label='认了这个称呼', risk='success', success={'attrs': {'mentality': 2, 'popularity': 1}},
                         successText='你在采访里说：对，我们留级了。'),
                    dict(label='关掉评论', risk='success', success={'attrs': {'mentality': 2, 'popularity': -1}},
                         successText='你把评论关了，训练室安静了不少。'),
                ]),
    'S15': dict(kind='special', phase='peak', tags=['#特殊', '#翻盘', '#偷家'], once=True, weight=1,
                requires="(s) => s.signed && s.week <= CONFIG.career.matchWeeksPerYear",
                cond='已签约 · 比赛周 · 一次',
                text='基地只剩 50 血，兵线进了门牙。你还有一次传送。',
                options=[
                    dict(label='传送偷家', risk='roll', attrs=['awareness'],
                         success={'attrs': {'awareness': 3, 'popularity': 3}},
                         fail={'coachTrust': -2},
                         successText='你传到对面基地，一下一下点掉了水晶。',
                         failText='你传到一半，屏幕先黑了。'),
                    dict(label='回防守家', risk='roll', attrs=['teamfight'],
                         success={'attrs': {'teamfight': 3}},
                         fail={'attrs': {'mentality': -2}},
                         successText='你守住这波，反手一波推平。',
                         failText='你守到最后一个兵，还是没守住。'),
                ]),
}


def ts_opt(o):
    parts = [f"label: '{o['label']}'", f"risk: '{o['risk']}'"]
    if o.get('attrs'):
        parts.append('attrs: [' + ', '.join(f"'{a}'" for a in o['attrs']) + ']')
    for k in ('success', 'fail'):
        if k in o:
            parts.append(f"{k}: {ts_cons(o[k])}")
    for k in ('successText', 'failText'):
        if o.get(k):
            parts.append(f"{k}: '{o[k]}'")
    return '      {\n        ' + ',\n        '.join(parts) + ',\n      },'


def ts_cons(c):
    inner = []
    if c.get('attrs'):
        inner.append('attrs: { ' + ', '.join(f"{k}: {v}" for k, v in c['attrs'].items()) + ' }')
    for k in ('coachTrust', 'stamina', 'money', 'injury', 'popularity'):
        if k in c:
            inner.append(f'{k}: {c[k]}')
    if c.get('flag'):
        inner.append(f"flag: '{c['flag']}'")
    return '{ ' + ', '.join(inner) + ' }'


def ts_event(eid, e):
    lines = [f"    id: '{eid}'", f"    kind: '{e['kind']}'", f"    phase: '{e['phase']}'",
             '    tags: [' + ', '.join(f"'{t}'" for t in e['tags']) + ']',
             f"    text: '{e['text']}'",
             f"    once: {'true' if e['once'] else 'false'}",
             f"    weight: {e['weight']}"]
    if e.get('requires'):
        lines.append(f"    requires: {e['requires']}")
    opt = ''.join(ts_opt(o) + '\n' for o in e['options'])
    return '  {\n' + ',\n'.join(lines) + ',\n    options: [\n' + opt + '    ]\n  },'


def main():
    src = SRC80.read_text(encoding='utf-8')
    src = re.sub(r"\n  //[^\n]*", "", src)
    head, rest = src.split('export const EVENTS: readonly GameEvent[] = [\n', 1)
    body, tail = rest.split('\n];\n', 1)

    chunks = ("\n" + body).split("\n  {\n    id: '")
    prefix = chunks[0]
    events = []
    for ch in chunks[1:]:
        eid = ch.split("'", 1)[0]
        text = "  {\n    id: '" + ch
        events.append([eid, text])

    out = []
    cond_report = []
    for eid, text in events:
        if eid in DELETE:
            continue
        if eid == 'E02':
            # 2026-11-06：试训成功率改成（四维平均 + 人气）÷ 2。
            text = text.replace(
                "        attrs: ['laning', 'popularity'],",
                "        attrs: ['operation', 'laning', 'teamfight', 'awareness'],\n"
                "        mix: 'fourAndPopularity',")
        if eid == 'E03':
            # 2026-11-06：三个选项在 matchRate 之上加四维加成。
            for b in ('0.25', '0.0', '0.05'):
                text = text.replace(f"        bonus: {b},",
                                    f"        bonus: {b},\n        skillBonus: true,")
        if eid in COND:
            expr, human = COND[eid]
            if eid == 'L11':
                text = text.replace('五百块', '两万块')
                text = text.replace("success: { money: 400, attrs: { popularity: 2 } }",
                                    "success: { money: 400, attrs: { popularity: 2 }, flag: '#路人王' }")
            # 去掉原有 requires
            text = re.sub(r"\n    requires: [^\n]*,", "", text, count=1)
            if expr:
                text = text.replace('\n    options: [', f"\n    requires: {expr},\n    options: [", 1)
            cond_report.append((eid, human, expr or '无'))
        else:
            # 比赛事件（M/P/E01）统一门槛；其余保持原条件
            if eid == 'E01' or eid.startswith('M') or eid in ('P01', 'P02', 'P07', 'P10', 'P11'):
                text = re.sub(r"\n    requires: [^\n]*,", "", text, count=1)
                text = text.replace('\n    options: [', f"\n    requires: {MATCH},\n    options: [", 1)
                cond_report.append((eid, '已签约 · 能上场（信任 ≥25）', MATCH))
            else:
                cond_report.append((eid, '（未改）', '—'))
        out.append(text)

    for eid, e in NEW_EVENTS.items():
        out.append(ts_event(eid, e))
        cond_report.append((eid, e['cond'], e['requires']))

    draft = head + 'export const EVENTS: GameEvent[] = [\n' + '\n'.join(out) + '\n];\n' + tail
    draft = draft.replace("from '../config'", "from '../../src/config'")
    draft = draft.replace("from '../types'", "from '../../src/types'")
    DRAFT.write_text(draft, encoding='utf-8')

    from collections import Counter
    kinds, phases = Counter(), Counter()
    for m in re.finditer(r"id: '([A-Z]\d\d)',\n    kind: '(\w+)',\n    phase: '(\w+)'", draft):
        kinds[m.group(2)] += 1
        phases[m.group(3)] += 1
    print(f"draft events: {len(out)}  kinds={dict(kinds)} phases={dict(phases)}  ->  {DRAFT}")


if __name__ == '__main__':
    main()
