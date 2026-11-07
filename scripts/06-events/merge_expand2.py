# 将第二批 20 条并入 src/data/events.ts；一次性脚本。
# 用法：PYTHONIOENCODING=utf-8 <python> scripts/06-events/merge_expand2.py
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import build_expand2_xlsx as M  # noqa: E402

SRC = ROOT / 'src' / 'data' / 'events.ts'

COND = {
    M.MATCH_COND: 's.signed && s.coachTrust >= CONFIG.match.benchThreshold',
    '已签约': 's.signed',
    '无额外条件': None,
}


def cons(d):
    if not d:
        return '{}'
    parts = []
    if 'attrs' in d:
        inner = ', '.join(f'{k}: {v}' for k, v in d['attrs'].items())
        parts.append(f'attrs: {{ {inner} }}')
    for k, v in d.items():
        if k == 'attrs':
            continue
        if isinstance(v, str):
            parts.append(f"{k}: '{v}'")
        else:
            parts.append(f'{k}: {v}')
    return '{ ' + ', '.join(parts) + ' }'


def opt(o):
    lines = [f"        label: '{o['label']}',", f"        risk: '{o['risk']}',"]
    if o['attrs']:
        lines.append('        attrs: [' + ', '.join(f"'{a}'" for a in o['attrs']) + '],')
    if o['bonus'] is not None:
        lines.append(f"        bonus: {o['bonus']},")
    if o['success'] is not None:
        lines.append(f"        success: {cons(o['success'])},")
    if o['fail'] is not None:
        lines.append(f"        fail: {cons(o['fail'])},")
    if o['s_text']:
        lines.append(f"        successText: '{o['s_text']}',")
    if o['f_text']:
        lines.append(f"        failText: '{o['f_text']}',")
    return '      {\n' + '\n'.join(lines) + '\n      },'


def ev(e):
    tag = '#比赛' if e['kind'] == 'match' else '#人物梗'
    lines = [f"  {{",
             f"    id: '{e['id']}',",
             f"    kind: '{e['kind']}',",
             f"    phase: '{e['phase']}',",
             f"    tags: ['{tag}'],",
             f"    text: '{e['text']}',",
             "    once: false,",
             "    weight: 5,"]
    c = COND[e['cond']]
    if c:
        lines.append(f"    requires: (s) => {c},")
    lines.append('    options: [')
    body = '\n'.join(opt(o) for o in e['opts'])
    lines.append(body)
    lines.append('    ],')
    lines.append('  },')
    return '\n'.join(lines)


def main():
    src = SRC.read_text(encoding='utf-8')
    marker = '\n];\n\n/** 无条件填充池'
    at = src.index(marker)
    block = '\n' + '\n'.join(ev(e) for e in M.EV) + '\n'
    src = src[:at] + block + src[at:]
    SRC.write_text(src, encoding='utf-8')
    print('merged', len(M.EV), 'events')


if __name__ == '__main__':
    main()
