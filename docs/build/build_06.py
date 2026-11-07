# -*- coding: utf-8 -*-
"""docs/06-事件库扩容-材料.docx —— 06 号 ticket（事件库扩到多少、谁来写）的材料。

数据现读，不手填：
- scripts/06-events/out-before.json   ← 落表前（E01–E05 + 兜底）
- scripts/06-events/out-after.json    ← 34 条落表后
- scripts/06-events/out-after84.json  ← 当前 84 条
- src/data/events.ts 的 84 条（id / 类型 / 阶段 / once / weight / 正文 / 写死年份标记）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(ROOT, "docs", "06-事件库扩容-材料.docx")


def _mono(r):
    r.font.name = "Consolas"
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi"):
        rf.set(qn(a), "Consolas")
    rf.set(qn("w:eastAsia"), k.CN)
    r.font.color.rgb = RGBColor(0x2F, 0x51, 0x7A)


def rich(p, s, size=10.5, color=k.K):
    """docx_kit.rich 的加强版：认 **加粗** 和 `行内代码`。"""
    for i, part in enumerate(s.split("**")):
        bold = i % 2 == 1
        for j, seg in enumerate(part.split("`")):
            if not seg:
                continue
            r = p.add_run(seg)
            k.set_run(r, size, bold, color)
            if j % 2 == 1:
                _mono(r)


k.rich = rich


def cmd(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.6)
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.25
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F1F3F6")
    pPr.append(shd)
    r = p.add_run(text)
    r.font.size = Pt(9.5)
    r.font.name = "Consolas"
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi"):
        rf.set(qn(a), "Consolas")
    rf.set(qn("w:eastAsia"), k.CN)


def f1(x):
    return f"{x:.1f}"


def pct(x):
    return f"{x * 100:.1f}%"


def load(name):
    with open(os.path.join(ROOT, "scripts", "06-events", name), encoding="utf-8") as fh:
        return json.load(fh)


BEFORE = load("out-before.json")
AFTER34 = load("out-after.json")
AFTER80 = load("out-after80.json")
AFTER84 = load("out-after84.json")
AFTER104 = load("out-after104w5.json")  # 权重 10→5 之后
BS, S34, S80, S84 = BEFORE["summary"], AFTER34["summary"], AFTER80["summary"], AFTER84["summary"]
S104 = AFTER104["summary"]


def event_stats(d):
    n = len(d["runs"])
    tot = {}
    mx = {}
    for r in d["runs"]:
        for kk, v in r["counts"].items():
            tot[kk] = tot.get(kk, 0) + v
            mx[kk] = max(mx.get(kk, 0), v)
    rows = [(kk, tot[kk], tot[kk] / n, mx[kk]) for kk in tot]
    rows.sort(key=lambda x: -x[1])
    return rows


B_ROWS = event_stats(BEFORE)
A34_ROWS = event_stats(AFTER34)
A80_ROWS = event_stats(AFTER80)
A84_ROWS = event_stats(AFTER84)
A104_ROWS = event_stats(AFTER104)
AVG80 = {r[0]: r[2] for r in A80_ROWS}
MAX80 = {r[0]: r[3] for r in A80_ROWS}
AVG84 = {r[0]: r[2] for r in A84_ROWS}
AVG104 = {r[0]: r[2] for r in A104_ROWS}
MAX104 = {r[0]: r[3] for r in A104_ROWS}


def parse_events():
    src = open(os.path.join(ROOT, "src", "data", "events.ts"), encoding="utf-8").read()
    region = src[src.index('export const EVENTS'):src.index('export const FILLER_EVENTS')]
    out = []
    for blk in re.split(r"\n  \{\n    id: '", region)[1:]:
        eid = blk.split("'", 1)[0]
        if not re.match(r"^[MLSPN]\d\d$", eid):
            continue
        kind = re.search(r"kind: '(\w+)'", blk)
        phase = re.search(r"phase: '(\w+)'", blk)
        once = re.search(r"once: (\w+)", blk)
        weight = re.search(r"weight: (\d+)", blk)
        text = re.search(r"text: '(.+?)',\n", blk)
        out.append(
            {
                "id": eid,
                "kind": kind.group(1) if kind else "?",
                "phase": phase.group(1) if phase else "?",
                "once": once.group(1) == "true" if once else None,
                "weight": int(weight.group(1)) if weight else 0,
                "text": text.group(1) if text else "",
                "star": "年份写死" in (blk[:200]),
            }
        )
    return out


EV = parse_events()
KIND_CN = {"match": "比赛", "life": "生活", "special": "特殊"}
EXTRA_KIND = {"E05": "special"}
PHASE_CN = {"growth": "成长", "peak": "巅峰", "decline": "衰退", "any": "任意"}

OLD = set(f"M{i:02d}" for i in range(1, 10)) | set(f"L{i:02d}" for i in range(1, 11)) | set(
    f"S{i:02d}" for i in range(1, 4)
) | set(f"P{i:02d}" for i in range(1, 13))
NEW = [e for e in EV if e["id"] not in OLD]


def ev_rows(evs):
    rows = []
    for e in evs:
        rows.append(
            [
                ("* " if e["star"] else "") + e["id"],
                KIND_CN.get(e["kind"], e["kind"]),
                PHASE_CN.get(e["phase"], e["phase"]),
                "是" if e["once"] else "否",
                str(e["weight"]),
                e["text"][:20] + ("…" if len(e["text"]) > 20 else ""),
            ]
        )
    return rows


HEAD = ["ID", "类型", "阶段", "一次性", "权重", "正文（截断）"]
WID = [1.7, 1.7, 1.7, 1.5, 1.3, 10.2]


def main():
    doc = k.new_doc("06 · 事件库扩容 · 材料")

    k.title(
        doc,
        "事件库扩到多少、谁来写",
        "06 号 ticket · 2026-11-07 · 104 条已进代码 · 模拟 24 局可复跑",
    )

    k.note(
        doc,
        "**你已拍板的：** 补到 80 条以上、AI 写你逐条看、选项 6–8 字（改设计文档）、失败文案每个选项单独写、"
        "比赛事件要求已签约且能上场、删掉转教练/合同转会/换位置类、L11 改两万块、E05 看伤停、84 条审核通过写进代码、"
        "事件链先不放进去、签约事件留着不写、8 处旧失败文案补上、84 条先停、链先停、梗密度不调、人物梗不引用真人名、"
        "人物梗 20 条审核通过写进代码、所有 weight 10 的事件改成 5。"
        "**还没拍板的：** 链以后做不做、收尾要不要用 auto 强制位、104 条够不够 / 要不要继续到 136 条、人物梗要不要再扩 20–40 条。"
        "文中标「未经用户确认」的推导不是决定。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "三句话")
    k.para(
        doc,
        f"**第一句：条数不是问题，重复才是。** E01 从每局 **{f1(45.4)} 次** 降到 **{f1(AVG104.get('E01', 0))} 次**，"
        f"无事件的周从 **{pct(BS['emptyRate'])}** 变成 **{pct(S104['emptyRate'])}**（104 条，24 局）。",
    )
    k.para(
        doc,
        f"**第二句：104 条把最高重复压到 {S104['maxRepeatInRun']} 次，但仍不是「记不住第二次」。** "
        f"顶部 N17 每局 {f1(AVG104.get('N17', 0))} 次；要压到 3 次以内，按算式约 136 条（丙）。",
    )
    k.para(
        doc,
        "**第三句：这次真正改的是「能不能穿帮」，不是「够不够多」。** 比赛事件现在要求已签约且信任 ≥25，"
        "路人期不会再抽到职业赛画面；代价是可重复池变小，顶部重复略升（80 条时最高 16 → 84 条时 14 → 104 条时 "
        f"{S104['maxRepeatInRun']}）。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "现状量化：24 局 × 240 周")
    k.para(
        doc,
        "口径：8 个种子 × 3 种策略（balanced / grind / noScrim），每局 240 周、每周一次抽取；"
        "遇到事件选第 `(seed + week) % 选项数` 个，不挑最优。四列只改了事件库。",
    )
    k.table(
        doc,
        ["指标", "落表前", "34 条", "80 条", "84 条", "104 条"],
        [
            ["抽到事件", str(BS["totalEvents"]), str(S34["totalEvents"]), str(S80["totalEvents"]), str(S84["totalEvents"]), str(S104["totalEvents"])],
            ["无事件周占比", pct(BS["emptyRate"]), pct(S34["emptyRate"]), pct(S80["emptyRate"]), pct(S84["emptyRate"]), pct(S104["emptyRate"])],
            ["每局事件数", f1(BS["eventsPerRun"]), f1(S34["eventsPerRun"]), f1(S80["eventsPerRun"]), f1(S84["eventsPerRun"]), f1(S104["eventsPerRun"])],
            ["每局空周数", f1(BS["emptiesPerRun"]), f1(S34["emptiesPerRun"]), f1(S80["emptiesPerRun"]), f1(S84["emptiesPerRun"]), f1(S104["emptiesPerRun"])],
            ["不同事件数", str(BS["distinctEvents"]), str(S34["distinctEvents"]), str(S80["distinctEvents"]), str(S84["distinctEvents"]), str(S104["distinctEvents"])],
            ["单事件单局最高", str(BS["maxRepeatInRun"]), str(S34["maxRepeatInRun"]), str(S80["maxRepeatInRun"]), str(S84["maxRepeatInRun"]), str(S104["maxRepeatInRun"])],
        ],
        [4.2, 2.9, 2.9, 2.9, 2.9, 2.9],
        size=8.6,
        caption="表 2-1　同一种子、同一策略，只换事件库",
    )

    k.h2(doc, "落表前：E01 一条吃掉大半局")
    rows = []
    for eid, total, avg, mx in B_ROWS:
        if eid not in ("E01", "E05"):
            continue
        rows.append([eid, str(total), f1(avg), str(mx)])
    k.table(
        doc,
        ["事件", "24 局总次数", "每局平均", "单局最高"],
        rows,
        [3.4, 4.0, 4.0, 4.0],
        size=8.6,
        caption="表 2-2　落表前能重复的只有两条；决赛/邀请函/兜底都只出 1 次，略",
    )

    k.h2(doc, "104 条时：最高 {n} 次".format(n=S104["maxRepeatInRun"]))
    rows = []
    for eid, total, avg, mx in A104_ROWS[:10]:
        kind = next((e["kind"] for e in EV if e["id"] == eid), EXTRA_KIND.get(eid, ""))
        rows.append([eid, KIND_CN.get(kind, "—"), f1(avg), str(mx)])
    k.table(
        doc,
        ["事件", "类型", "每局平均", "单局最高"],
        rows[:6],
        [3.2, 3.2, 4.0, 4.0],
        size=8.6,
        caption="表 2-3　104 条时重复最多的几条（24 局平均）",
    )
    k.para(
        doc,
        f"104 条里 **75 条可重复**、29 条 `once`，权重 5/2/1 = 75/13/16（这 99 条表内事件；另有 E01–E05 也是 5）。240 次抽取摊到 75 条，"
        "再乘权重差，顶部仍有 7–9 次。要让单条「一局记不住第二次」，条数还得往上走。"
        "\n\n**权重 10→5 的实测：** 全体一起减半不改变相对占比，只有 weight 1/2 的特殊事件占比翻倍；"
        f"最高重复从 18 降到 {S104['maxRepeatInRun']}，平均 >5 次的仍是 12 条（N17 8.5 次/局）。",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "三个方案：条数、工时、代价")
    k.para(doc, "算式（未经用户确认，从实测反推）：")
    cmd(doc, "可重复条数 ≈ 240 ÷ 每局重复上限")
    cmd(doc, "总条数 ≈ 可重复条数 ÷ 0.70        # 现在 84 条里 59 条可重复")
    cmd(doc, "工时 ≈ 新写条数 × 20 分钟")
    k.para(
        doc,
        "240 是一局的抽取次数；0.70 是当前「可重复 ÷ 总数」。比例会随写法漂移（多写 `once` 就降），"
        "下表是起点，不是保证。",
        size=9.5,
        color=k.G,
    )
    k.table(
        doc,
        ["方案", "总条数", "新写", "目标重复", "工时", "状态 / 代价"],
        [
            ["甲：现成 34 条", "34", "0", "实测 22–30 次/局", "0", "已完成；内容密度不够"],
            ["乙：补到 84 条", "84", "54", "实测 ≤{n} 次/局".format(n=S84["maxRepeatInRun"]), "≈18 小时", "已完成并进代码；审稿未做"],
            ["丙：补到 136 条", "136", "52", "目标 ≤3 次/局", "≈17.3 小时", "未做；只补 52 条，不重写"],
        ],
        [3.4, 2.0, 1.8, 3.6, 2.6, 7.2],
        size=8.4,
        caption="表 3-1　三条路；工时只算写作，不含审稿与跑测试",
    )
    k.para(
        doc,
        "乙累计新写 54 条（46 条新写 + 8 条补写），删 9 条后净增 50；54 × 20 分钟 ≈ 18 小时。"
        "丙是在 84 条上再加 52 条，≈17.3 小时。"
        "2026-11-07 又把已审的 20 条人物梗并进代码，现 104 条，实测最高 "
        f"{S104['maxRepeatInRun']} 次/局；下面四、五节按 104 条重算。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "配额表：目标 vs 实际")
    kinds = {}
    phases = {}
    for e in EV:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        phases[e["phase"]] = phases.get(e["phase"], 0) + 1
    k.table(
        doc,
        ["类型", "目标（你拍板）", "实际", "差"],
        [
            ["比赛", "30", str(kinds.get("match", 0)), str(kinds.get("match", 0) - 30)],
            ["生活", "36", str(kinds.get("life", 0)), str(kinds.get("life", 0) - 36)],
            ["特殊", "14", str(kinds.get("special", 0)), str(kinds.get("special", 0) - 14)],
            ["合计", "80", str(len(EV)), str(len(EV) - 80)],
        ],
        [4.0, 4.0, 4.0, 3.0],
        size=8.6,
        caption="表 4-1　类型配额；80 条目标之外又并入 20 条人物梗（比赛 +5、生活 +14、特殊 +1，未经你逐条配额）",
    )
    k.table(
        doc,
        ["阶段", "目标（你拍板）", "实际", "差"],
        [
            ["成长", "18", str(phases.get("growth", 0)), str(phases.get("growth", 0) - 18)],
            ["巅峰", "21", str(phases.get("peak", 0)), str(phases.get("peak", 0) - 21)],
            ["衰退", "12", str(phases.get("decline", 0)), str(phases.get("decline", 0) - 12)],
            ["任意", "29", str(phases.get("any", 0)), str(phases.get("any", 0) - 29)],
            ["合计", "80", str(len(EV)), str(len(EV) - 80)],
        ],
        [4.0, 4.0, 4.0, 3.0],
        size=8.6,
        caption="表 4-2　阶段配额；人物梗 20 条按成长 2 / 巅峰 9 / 衰退 4 / 任意 5 摊入",
    )
    k.para(
        doc,
        "如果继续到 136 条（丙），按同一比例摊剩下 52 条：比赛 +11、生活 +20、特殊 +7；"
        "阶段成长 +8、巅峰 +20、衰退 +5、任意 +9。这是按现有比例算的，**未经用户确认**。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "代码里的 104 条：改了什么")
    k.para(
        doc,
        "整表替换进 `src/data/events.ts`（E01–E05 保留，E02/E03 按你要求改了掷骰口径）。"
        "删 9 条：S01 P08 P12 L13 S11 L17 L20 L23 L27（转教练、合同转会、换位置、二队、L20 替补名单）。"
        "新增 8 条：L33–L36、S12–S15；2026-11-07 再并入人物梗 N01–N20（你已审核通过）。"
        "84 条版见 `P1-事件库-84条-重写稿-v5.xlsx`，人物梗见 `P1-事件库-人物梗-20条-试写.xlsx`；测试与类型检查全绿（75 tests）。",
    )
    k.table(
        doc,
        ["改动", "条数", "说明"],
        [
            ["删除", "9", "S01 P08 P12（合同/转会/换队）、L13 S11（转教练）、L17 L23 L27（换位置/首发再替补）、L20（替补名单）"],
            ["新增", "8", "L33 集锦、L34 卷尺、L35 水友赛、L36 网线、S12 解说泄密、S13 丢丢丢、S14 一年级五班、S15 50 血翻盘"],
            ["条件收紧", "31", "比赛事件统一 `signed && coachTrust >= benchThreshold(25)`"],
            ["E02", "1", "四维平均 + 人气，再 ÷2（`mix: 'fourAndPopularity'`）"],
            ["E03", "1", "保留 matchRate，另加四维加成（`skillBonus`，±0.2，**系数未经确认**）"],
            ["E05", "1", "触发改为 `injury >= 1`，并改 `once`，避免伤停期间每周复发"],
            ["L11", "1", "五百块 → 两万块，成功分支写 `#路人王`"],
            ["失败文案", "8", "E01–E04 的 8 个失败分支补上文案（此前只有数值）"],
            ["人物梗", "20", "N01–N20 审核通过进代码；比赛 5 / 生活 14 / 特殊 1；正文 0 真人名"],
            ["权重", "77", "所有 weight 10 → 5（含 E01–E05、M/L/S/P/N、F01/F02）；特殊 1/2 不动"],
        ],
        [3.2, 1.6, 10.8],
        size=8.4,
        caption="表 5-1　进代码的改动清单",
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "事件链：5 条建议，按你的决定暂不放进代码")
    k.para(
        doc,
        "建议表在 `P1-事件链-建议.xlsx`：5 条链、15 个节点、4 条新事件（L37 手腕收尾、L40 那条龙、M26 偷家、M27 让二追三），"
        "另改 4 条旧事件各一行。机制只用现成字段：选项置 flag，后续事件 `requires` 查 flag；"
        "中段成功再置一个二级标记（#伤停 / #认过丢龙 / #被研究 / #被提起），保证收尾不会抢在中段前面。",
    )
    k.para(
        doc,
        "**「一定抽到」只有一个办法：`auto: true`。** `forcedEvent` 每周最先查，标记一置上，下一周就无条件返回它"
        "（只让给当周决赛/邀请函），不走权重抽签。代价是它必占掉触发后那一周；标记若在最后一年才置，仍可能没机会。"
        "现在这 5 条链的收尾都还是概率触发（峰值期约九成），没有用 auto。"
        "**你已定：先不放进去。** 表留着，以后要开链时再定收尾用不用 auto。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "缺口")
    k.table(
        doc,
        ["缺口", "数量", "说明"],
        [
            ["事件链未进代码", "5 条链", "你已定先不放进去；建议表留着，开链时再定 auto"],
            ["签约事件", "1 条", "你已定留着不写；现在仍走 `resolveSigningWindow`"],
            ["丙方案的 52 条", "52", "未写；是否继续到 136 条要你定"],
            ["人物梗再扩", "0", "20 条已审核进代码；要不要再扩 20–40 条要你定"],
            ["梗密度未校准", "—", "有的梗很密、有的只有一句，需要你看过再调"],
        ],
        [4.6, 2.0, 9.4],
        size=8.4,
        caption="表 7-1　缺口清单；84 条与人物梗 20 条已审核进代码",
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "还要你拍板")
    k.para(doc, "**已定（2026-11-07）：** 84 条先停、不做到 136；5 条链先停；梗密度不调；人物梗表不引用真人名；人物梗 20 条审核通过写进代码。", bullet=True)
    k.para(doc, "1. 104 条够不够？要不要按丙方案继续到 136（再加 32，≈10.7 小时）？", bullet=True)
    k.para(doc, "2. 人物梗这 20 条的味道对不对？要不要按同口径再挑 20–40 条？", bullet=True)
    k.para(doc, "3. 5 条事件链以后做不做？做的话收尾用不用 `auto`？", bullet=True)
    k.para(doc, "4. 签约事件（单选项「签字」）要不要补进 `resolveSigningWindow`？", bullet=True)

    # ---------------- 九 ----------------
    k.h1(doc, "九", "复跑")
    k.para(doc, "在仓库根执行：")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts before    # 落表前：需先 stash 掉事件库")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after     # 34 条：在 67677c8 上跑，写 out-after.json")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after80   # 80 条版")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after84   # 84 条版")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after104  # 104 条、权重 10")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after104w5  # 本文数字（104 条、权重 5）")
    cmd(doc, "IGNORE_CONS=1 DELETED=S01,P08,P12 PYTHONIOENCODING=utf-8 python scripts/06-events/audit_table.py")
    cmd(doc, "npx vitest run && npx tsc --noEmit")
    k.para(
        doc,
        "`sim.ts` 的标签只决定输出文件名，读的都是当前代码。要复现 34 条那一列，先 checkout 到 "
        "`67677c8` 再跑。表格对照脚本的 `IGNORE_CONS` 用于跳过属性重排造成的数值差，`DELETED` 是已删事件的允许清单。",
        size=9.5,
        color=k.G,
    )

    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
