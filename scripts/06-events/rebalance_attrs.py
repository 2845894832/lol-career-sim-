# 按 2026-11-06 用户反馈「属性加成太多人气/心态，应多一些操作/对线/团战/意识」重排草稿。
# 只改草稿 _draft80.ts，不改 src；用法（仓库根）：
#   PYTHONIOENCODING=utf-8 <python> scripts/06-events/rebalance_attrs.py
import re
from pathlib import Path

DRAFT = Path(__file__).with_name('_draft80.ts')

SKILL = ('operation', 'laning', 'teamfight', 'awareness')

# 先匹配到的优先；只看选项文案（label）
HINTS = [
    (('团', '开团', '正面', '越塔', '对拼', '换血', '拼一波', '接团', '反打', '守家', '集火', '打团'), 'teamfight'),
    (('线', '补刀', '压线', '对线', '发育', '控线', '塔皮', '兵线', '推塔', '清线'), 'laning'),
    (('视野', '节奏', '绕', '偷家', '传送', '惩戒', '龙', '野', '蹲', '换线', '决策', '指挥',
      '研究', '复盘', '录像', 'BP', '分析', '看', '运营', '抓'), 'awareness'),
    (('操作', '技能', '手速', '绝活', '连招', '点人', '按下', '排位', '单杀', '对枪'), 'operation'),
]

# 明显属于舆论/粉丝/心理的选项，保持原样（不转技巧）
KEEP_POP = ('人气', '粉丝', '直播', '采访', '微博', '超话', '热搜', '代言', '广告', '镜头',
            '集锦', '自嘲', '公屏', '舆论', '运营', '评论', '弹幕', '通告', '商务')
KEEP_MEN = ('心态', '紧张', '失眠', '压力', '冷静', '沟通', '鼓励', '吵', '道歉', '认了')

# 个别选项手工指定（label 全局唯一时可直接用）
MANUAL = {
    '去，通宵打': 'operation',
    '不去，留下训练': 'operation',
    '拉上二队一起': 'teamfight',
    '加练到凌晨': 'operation',
    '找教练问差距': 'awareness',
    '拉着队友加练': 'teamfight',
    '认真回他': None,
    '发个模板': None,
    '不回': None,
    '起来看录像': 'awareness',
    '下楼走走': None,
    '找教练聊': None,
    '认真备课': 'awareness',
    '随便讲讲': 'awareness',
    '推掉': None,
    '硬拼到底': 'teamfight',
    '让队友拖住': 'teamfight',
    '回来接着压': 'laning',
    '回城整补': 'awareness',
    '换一套打法': 'awareness',
    '学他的打法': 'awareness',
    '先适应场地': 'awareness',
}


def classify(eid, label):
    if label in MANUAL:
        return MANUAL[label]
    for words, attr in HINTS:
        if any(w in label for w in words):
            return attr
    return None


def parse_cons(s):
    """'{ attrs: { popularity: 2 }, coachTrust: -1, flag: \\'#X\\' }' -> (attrs, nums, strings)

    字符串字段（flag / clearFlag / teamId）必须原样留着，否则重排一次标记就全丢了。
    """
    attrs = {}
    strings = re.findall(r"(flag|clearFlag|teamId): '([^']*)'", s)
    if strings:
        s = re.sub(r"(flag|clearFlag|teamId): '[^']*',?\s*", '', s)
    m = re.search(r'attrs: \{([^}]*)\}', s)
    if m:
        for k, v in re.findall(r'(\w+): (-?\d+)', m.group(1)):
            attrs[k] = int(v)
        s = s[:m.start()] + s[m.end():]
    rest = [(k, int(v)) for k, v in re.findall(r'(\w+): (-?\d+)', s)]
    return attrs, rest, strings


def emit_cons(attrs, rest, strings=()):
    parts = []
    if attrs:
        parts.append('attrs: { ' + ', '.join(f'{k}: {v}' for k, v in attrs.items()) + ' }')
    parts += [f'{k}: {v}' for k, v in rest]
    parts += [f"{k}: '{v}'" for k, v in strings]
    return '{ ' + ', '.join(parts) + ' }'


def rebalance(attrs, skill, branch, kind):
    """技巧类选项：人气/心态正向点折半换成技巧点；
    其余选项：人气/心态加成一律减半（不新增技巧）。
    比赛事件没有技巧点就补 2 点，避免整条只涨人气。"""
    if not attrs:
        return attrs
    out = dict(attrs)
    if branch == 'success':
        if skill:
            pool = 0
            for k in ('popularity', 'mentality'):
                v = out.get(k, 0)
                if v > 0:
                    pool += v
                    out.pop(k, None)
            if pool:
                out[skill] = out.get(skill, 0) + max(1, round(pool * 0.5))
            if skill not in out:
                out[skill] = 2
        else:
            for k in ('popularity', 'mentality'):
                v = out.get(k, 0)
                if v > 0:
                    out[k] = max(1, round(v / 2))
        if kind == 'match' and not any(k in out for k in SKILL):
            out['operation'] = out.get('operation', 0) + 2
    else:
        for k in ('popularity', 'mentality'):
            v = out.get(k, 0)
            if v < 0:
                out[k] = -max(1, round(abs(v) / 2))
    return out


def main():
    src = DRAFT.read_text(encoding='utf-8')
    head, rest = src.split("export const EVENTS: GameEvent[] = [\n", 1)
    body, tail = rest.split('\n];\n', 1)

    chunks = ("\n" + body).split("\n  {\n    id: '")
    out = [chunks[0]]
    changed = 0

    for ch in chunks[1:]:
        eid = ch.split("'", 1)[0]
        text = "  {\n    id: '" + ch
        kind = re.search(r"kind: '(\w+)'", text).group(1)
        opts = text.split("\n      {\n        label: '")
        new_opts = [opts[0]]
        for opt in opts[1:]:
            label = opt.split("'", 1)[0]
            skill = classify(eid, label)
            if skill:
                # roll 用的属性列也一起换
                opt = re.sub(r"attrs: \[[^\]]*\],", f"attrs: ['{skill}'],", opt, count=1)
            lines = opt.split('\n')
            for i, ln in enumerate(lines):
                m = re.match(r"^        (success|fail): \{(.*)\},$", ln)
                if not m:
                    continue
                attrs, rest, strings = parse_cons(m.group(2))
                new = rebalance(attrs, skill, m.group(1), kind)
                if new != attrs:
                    changed += 1
                lines[i] = f"        {m.group(1)}: {emit_cons(new, rest, strings)},"
            new_opts.append('\n'.join(lines))
        text = "\n      {\n        label: '".join(new_opts)
        out.append(text)

    DRAFT.write_text(head + "export const EVENTS: GameEvent[] = [\n" + ''.join(out) + '\n];\n' + tail,
                     encoding='utf-8')
    print('changed consequence lines:', changed)


if __name__ == '__main__':
    main()
