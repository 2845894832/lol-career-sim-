"""把 src/data/events.ts 里的 34 条与初审表逐项对照，只打印差异。

用法（仓库根，需 openpyxl）：
  PYTHONIOENCODING=utf-8 <python> scripts/06-events/audit_table.py
"""
import io
import re
import sys
from openpyxl import load_workbook

TS = 'src/data/events.ts'
SHEETS = ['P1-事件库-梗驱动-初审.xlsx', 'P1-事件库-人物梗-初审.xlsx']

ATTR = {
    '操作': 'operation', '对线': 'laning', '团战': 'teamfight',
    '意识': 'awareness', '心态': 'mentality', '人气': 'popularity',
}
OTHER = {'教练信任': 'coachTrust', '体力': 'stamina', '伤病': 'injury', '金钱': 'money'}
ALL_NAMES = list(ATTR.items()) + list(OTHER.items())


def load_table():
    rows = []
    for path in SHEETS:
        wb = load_workbook(path, data_only=True)
        ws = wb['选项']
        header = [c.value for c in ws[1]]
        for r in ws.iter_rows(min_row=2, values_only=True):
            d = dict(zip(header, r))
            if d.get('事件ID'):
                rows.append(d)
    return rows


def brace_obj(text, start):
    """text[start] == '{'，返回 (内部文本, 结尾下标)。"""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i
    raise ValueError('unbalanced')


def parse_cons(body):
    d = {}
    m = re.search(r'attrs:\s*\{([^}]*)\}', body)
    if m:
        for k, v in re.findall(r"(\w+): (-?\d+)", m.group(1)):
            d[k] = int(v)
    for k in ('coachTrust', 'stamina', 'injury', 'money', 'temp', 'maxStamina', 'honor'):
        m = re.search(k + r':\s*(-?\d+)', body)
        if m:
            d[k] = int(m.group(1))
    m = re.search(r"flag: '(#.+?)'", body)
    if m:
        d['flag'] = m.group(1)
    return d


def parse_ts():
    src = io.open(TS, encoding='utf-8').read()
    region = src[src.index('以下 34 条'):]
    events = []
    for blk in region.split("\n  {\n    id: '")[1:]:
        ev_id = blk.split("'", 1)[0]
        opts = []
        for chunk in blk.split("\n      {\n        label: '")[1:]:
            label = chunk.split("',", 1)[0]
            o = {'label': label, 'successText': None, 'failText': None,
                 'risk': None, 'bonus': 0.0, 'success': {}, 'fail': {}}
            m = re.search(r"risk: '(\w+)'", chunk)
            o['risk'] = m.group(1) if m else None
            m = re.search(r"bonus: ([0-9.]+)", chunk)
            o['bonus'] = float(m.group(1)) if m else 0.0
            m = re.search(r"successText: '(.+?)',\n", chunk)
            o['successText'] = m.group(1) if m else None
            m = re.search(r"failText: '(.+?)',\n", chunk)
            o['failText'] = m.group(1) if m else None
            for key in ('success', 'fail'):
                m = re.search(key + r': \{', chunk)
                if m:
                    body, _ = brace_obj(chunk, m.end() - 1)
                    o[key] = parse_cons(body)
            opts.append(o)
        events.append((ev_id, opts))
    return events


def expected_consequence(text):
    out = {}
    if not text or str(text).strip() in ('—', ''):
        return out
    for tok in str(text).split('；'):
        tok = tok.strip().split('，')[0]
        if not tok:
            continue
        for name, key in ALL_NAMES:
            m = re.match(name + r'\s*([+−-]\s*\d+|[+−-]+|\d+)?$', tok)
            if not m:
                continue
            raw = m.group(1)
            if raw is None:
                v = 0
            elif raw.replace(' ', '').lstrip('+−-').isdigit():
                v = int(raw.replace(' ', '').lstrip('+−-'))
                if raw.strip().startswith(('−', '-')):
                    v = -v
            else:
                n = raw.count('+') + raw.count('−') + raw.count('-')
                sign = -1 if ('−' in raw or '-' in raw) else 1
                unit = 8 if key == 'stamina' else 100 if key == 'money' else 2 if key in ATTR.values() else 3
                v = sign * n * unit
            if v:
                out[key] = v
    return out


def main():
    table = load_table()
    ts = {ev: opts for ev, opts in parse_ts()}
    diffs = 0
    for row in table:
        ev_id = str(row['事件ID']).strip()
        label = str(row['选项']).strip()
        opts = ts.get(ev_id, [])
        o = next((x for x in opts if x['label'] == label), None)
        if not o:
            print('MISSING', ev_id, label)
            diffs += 1
            continue
        tag = '%s %s' % (ev_id, label)
        want_risk = {'掷骰': 'roll', '必成': 'success', '必败': 'fail'}[str(row['风险类型']).strip()]
        if o['risk'] != want_risk:
            print('RISK', tag, o['risk'], '!=', want_risk)
            diffs += 1
        bonus = str(row.get('比赛加成') or '—').strip()
        want_bonus = 0.0 if bonus in ('—', '') else int(bonus.replace('%', '')) / 100
        if abs(o['bonus'] - want_bonus) > 1e-9:
            print('BONUS', tag, o['bonus'], '!=', want_bonus)
            diffs += 1
        scene = str(row.get('成功高光（场面）') or '').strip()
        scene = None if scene in ('—', '') else scene
        got_scene = o['failText'] if want_risk == 'fail' else o['successText']
        if got_scene != scene:
            print('SCENE', tag, '\n  ts:', o['successText'], '\n  tb:', scene)
            diffs += 1
        flag = str(row.get('写标记') or '—').strip()
        want_flag = None if flag in ('—', '') else flag
        for key, col in (('success', '成功后果'), ('fail', '失败后果')):
            want = expected_consequence(row.get(col))
            got = dict(o[key])
            got.pop('flag', None)
            if got != want:
                print('CONS', key, tag, '\n  ts:', got, '\n  tb:', want)
                diffs += 1
        flags = [o['success'].get('flag'), o['fail'].get('flag')]
        for f in flags:
            if f and f != want_flag:
                print('FLAG', tag, f, '!=', want_flag)
                diffs += 1
        if want_flag and want_flag not in flags:
            print('FLAG-MISSING', tag, want_flag)
            diffs += 1
    print('---')
    print('table options', len(table), 'ts events', len(ts), 'diffs', diffs)
    return 1 if diffs else 0


if __name__ == '__main__':
    sys.exit(main())
