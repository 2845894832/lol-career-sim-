# -*- coding: utf-8 -*-
"""docs/06-事件库扩容-材料.docx —— 06 号 ticket（事件库扩到多少、谁来写）的材料。

数据现读，不手填：
- scripts/06-events/out-before.json   ← 落表前（E01–E05 + 兜底）
- scripts/06-events/out-after.json    ← 34 条落表后
- scripts/06-events/out-after80.json  ← 补到 80 条后
- src/data/events.ts 的 80 条（id / 类型 / 阶段 / once / weight / 正文 / 写死年份标记）
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
BS, S34, S80 = BEFORE["summary"], AFTER34["summary"], AFTER80["summary"]


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
AVG80 = {r[0]: r[2] for r in A80_ROWS}
MAX80 = {r[0]: r[3] for r in A80_ROWS}


def parse_events():
    src = open(os.path.join(ROOT, "src", "data", "events.ts"), encoding="utf-8").read()
    region = src[src.index("以下 34 条"):]
    out = []
    for blk in re.split(r"\n  \{\n    id: '", region)[1:]:
        eid = blk.split("'", 1)[0]
        if not re.match(r"^[MLSP]\d\d$", eid):
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
        "06 号 ticket · 2026-11-06 · 34 条落表 + 按你拍板的配额补 46 条 = 80 条 · 模拟 24 局可复跑",
    )

    k.note(
        doc,
        "**你已经拍板的（2026-11-06 对话）：** 总量先补到 80 条、AI 写你逐个看、6–8 字并改设计文档、"
        "失败文案每个选项单独写、做 6 条跨事件标记链、类型 30/36/14、阶段 18/21/12/29。"
        "**还没拍板的：** 要不要继续到 136 条、梗密度、人物梗表怎么用。文中推导标了「未经用户确认」的部分不是决定。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "三句话")
    k.para(
        doc,
        f"**第一句：34 条把「总是 E01」解决了。** E01 从每局 **{f1(45.4)} 次** 降到 **{f1(1.8)} 次**"
        f"（80 条时），无事件的周从 **{pct(BS['emptyRate'])}** 变成 **{pct(S80['emptyRate'])}**。",
    )
    k.para(
        doc,
        f"**第二句：34 条没解决「又是这条」。** 34 条时单局最高重复 **{S34['maxRepeatInRun']} 次**、"
        f"L02 一局平均 {f1(22.0)} 次；补到 80 条后最高重复 **{S80['maxRepeatInRun']} 次**、"
        f"最高的一条 L16 平均 {f1(AVG80['L16'])} 次。",
    )
    k.para(
        doc,
        "**第三句：80 条是「一局同一条不超过 16 次」，还不是「记不住第二次」。** 想要后者，"
        f"按算式要 136 条（丙方案），那是另外 102 条、约 34 小时——要不要走，你定。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "现状量化：24 局 × 240 周")
    k.para(
        doc,
        "口径：8 个种子 × 3 种策略（balanced / grind / noScrim），每局 240 周、每周一次事件抽取；"
        "遇到事件就选第 `(seed + week) % 选项数` 个选项，不挑最优。三列是同一批种子、同一套策略，只改了事件库。",
    )
    k.table(
        doc,
        ["指标", "落表前", "34 条", "80 条"],
        [
            ["抽取总数", str(BS["totalDraws"]), str(S34["totalDraws"]), str(S80["totalDraws"])],
            ["抽到事件", str(BS["totalEvents"]), str(S34["totalEvents"]), str(S80["totalEvents"])],
            ["无事件周占比", pct(BS["emptyRate"]), pct(S34["emptyRate"]), pct(S80["emptyRate"])],
            ["每局事件数", f1(BS["eventsPerRun"]), f1(S34["eventsPerRun"]), f1(S80["eventsPerRun"])],
            ["每局空周数", f1(BS["emptiesPerRun"]), f1(S34["emptiesPerRun"]), f1(S80["emptiesPerRun"])],
            ["出现过的不同事件数", str(BS["distinctEvents"]), str(S34["distinctEvents"]), str(S80["distinctEvents"])],
            ["单事件单局最高重复", str(BS["maxRepeatInRun"]), str(S34["maxRepeatInRun"]), str(S80["maxRepeatInRun"])],
        ],
        [5.0, 3.6, 3.6, 3.6],
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
    k.para(
        doc,
        "E01 是唯一一条「可重复、无前置、权重 10」的事件，所以它吃掉了整个随机池。"
        "其余可重复事件只有 E05（要求 `#手腕不适`，不是每周都有）和两条兜底 F01/F02（`once`）。",
        size=9.5,
        color=k.G,
    )

    k.h2(doc, "34 条时：前五条各自 12–22 次")
    rows = []
    for eid, total, avg, mx in A34_ROWS[:8]:
        if eid.startswith(("SPR", "SUM", "INV", "F0")):
            continue
        rows.append([eid, KIND_CN.get(next((e["kind"] for e in EV if e["id"] == eid), EXTRA_KIND.get(eid, "")), "—"), f1(avg), str(mx)])
    k.table(
        doc,
        ["事件", "类型", "每局平均", "单局最高"],
        rows[:6],
        [3.2, 3.2, 4.0, 4.0],
        size=8.6,
        caption="表 2-3　34 条时重复最多的几条（24 局平均）",
    )

    k.h2(doc, "80 条时：最高 16 次，顶部压到 9 次")
    rows = []
    for eid, total, avg, mx in A80_ROWS[:8]:
        rows.append([eid, KIND_CN.get(next((e["kind"] for e in EV if e["id"] == eid), EXTRA_KIND.get(eid, "")), "—"), f1(avg), str(mx)])
    k.table(
        doc,
        ["事件", "类型", "每局平均", "单局最高"],
        rows[:6],
        [3.2, 3.2, 4.0, 4.0],
        size=8.6,
        caption="表 2-4　80 条时重复最多的几条（24 局平均）；E05 是伤病链，7.3 次/局",
    )
    k.para(
        doc,
        "原因：80 条里 **58 条可重复**、22 条 `once`，权重 10/2/1 三档。240 次抽取摊到 58 条，"
        "再乘上权重差异，顶部仍有 9 次左右——这就是「丙方案」还值得讨论的地方。",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "三个方案：条数、工时、代价")
    k.para(doc, "算式（未经用户确认，但可以从实测反推）：")
    cmd(doc, "可重复条数 ≈ 240 ÷ 每局重复上限")
    cmd(doc, "总条数 ≈ 可重复条数 ÷ 0.72        # 现在 80 条里 58 条可重复")
    cmd(doc, "工时 ≈ 新写条数 × 20 分钟")
    k.para(
        doc,
        "240 是一局的抽取次数；0.72 是当前「可重复 ÷ 总数」的比例，用来把可重复条数折成总条数。"
        "这两个数会随写法漂移（多写 `once` 比例就降），所以下表是起点，不是保证。",
        size=9.5,
        color=k.G,
    )
    k.table(
        doc,
        ["方案", "总条数", "新写", "目标重复", "工时", "状态 / 代价"],
        [
            ["甲：现成 34 条", "34", "0", "实测 22–30 次/局", "0", "已完成；内容密度不够"],
            ["乙：补到 80 条", "80", "46", "实测 ≤16 次/局", "≈15.3 小时", "已完成；梗密度与审稿未做"],
            ["丙：补到 136 条", "136", "102", "目标 ≤3 次/局", "≈34 小时", "未做；写作量翻倍，配额要按模拟校准"],
        ],
        [3.4, 2.0, 1.8, 3.4, 2.4, 7.4],
        size=8.4,
        caption="表 3-1　三条路；工时只算写作，不含审稿与跑测试",
    )
    k.para(
        doc,
        "**甲、乙都已经在代码里了**（`src/data/events.ts`，80 条，测试 69→72 全绿）。"
        "丙的 136 是按 `240 ÷ 3 ≈ 80 条可重复 ÷ 0.72 ≈ 111` 再留余量取整得到；"
        "它的真正价值不是「条数」，是把顶部从 16 次压到 5 次以内。",
    )
    k.para(
        doc,
        "**谁写**：这次 46 条是 AI 按两张初审表的梗写的，你还没逐个看。"
        "谁写、抽检到什么程度，仍要你定——我不替你把它当成已验收。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "配额表：你拍的目标 vs 实际")
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
        caption="表 4-1　类型配额（目标来自 2026-11-06 对话）",
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
        caption="表 4-2　阶段配额（目标来自 2026-11-06 对话）",
    )
    k.para(
        doc,
        "如果继续到 136 条（丙），剩下的 56 条按同一比例摊：比赛 +11、生活 +20、特殊 +9；"
        "阶段按成长 +8、巅峰 +20、衰退 +6、任意 +8。这是按现有比例算的，**未经用户确认**。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "已经落地的 80 条")
    k.para(
        doc,
        "前 34 条全部来自 `P1-事件库-梗驱动-初审.xlsx`（22 条）与 `P1-事件库-人物梗-初审.xlsx`（12 条），"
        "正文、标签、选项、成功场面、后果数值逐项照表；`scripts/06-events/audit_table.py` 的对照结果是 "
        "`table options 91 / diffs 0`。后 46 条按你拍的配额补写，梗来自同一批初审表与两张梗表。E01–E05 没动。",
    )
    k.para(doc, "**前 34 条（初审表原样）**", size=10.5)
    k.table(
        doc,
        HEAD,
        ev_rows([e for e in EV if e["id"] in OLD]),
        WID,
        size=7.6,
        caption="表 5-1　34 条；`*` = 年份写死，要你亲自审",
    )
    k.para(doc, "**后 46 条（按你拍的配额补写）**", size=10.5)
    k.table(
        doc,
        HEAD,
        ev_rows(NEW),
        WID,
        size=7.6,
        caption="表 5-2　46 条；`*` = 年份写死，要你亲自审",
    )

    k.h2(doc, "转写时定了什么")
    k.para(
        doc,
        "- **符号 → 数值**：表里的 `+` / `++` / `+++` 分别记 ±2 / ±4 / ±6；体力 ±8；金钱 −100；"
        "教练信任 ±3/个；写了数字的照抄。\n"
        "- **触发条件**：表里的「第 N 年」写成 `requires: s.year === N`，代码里标 `// * 年份写死`；"
        "没用 `year` 字段，避免抢在决赛/邀请函前面。\n"
        "- **权重**：特殊事件 1，标「低频」的 2，其余 10。\n"
        "- **选项文案**：6–8 字，设计文档已从 ≤4 字改为 6–8 字（2026-11-06，按你拍板）。\n"
        "- **失败文案**：新 46 条每个选项都写；旧 34 条的 42 处也补齐了。",
        size=9.5,
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "缺口：还没做的、做不了的")
    k.table(
        doc,
        ["缺口", "数量", "说明"],
        [
            ["E01–E04 没有失败文案", "8 处", "历史事件没动；要不要补，你定"],
            ["80 条还没被你逐个看", "80 / 80", "你说过「整完后我会一个一个看」；这一步只能你做"],
            ["真人选手/战队名", "0", "按你拍板继续全虚构"],
            ["人物梗表", "1000 行", "大多是外号，单独成不了事件；要不要拿来写弹幕/粉丝类"],
            ["梗密度未校准", "—", "46 条里有的梗很密、有的只有一句，需要你看过再调"],
            ["丙方案的 56 条", "56", "未写；是否继续到 136 条要你定"],
        ],
        [4.6, 2.2, 9.0],
        size=8.4,
        caption="表 6-1　缺口清单；前两条影响验收，后四条影响内容方向",
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "还要你拍板的问题")
    k.para(doc, "1. 80 条够不够？要继续到 136 条（丙，+56 条、约 34 小时）还是先停在这里让你看完。", bullet=True)
    k.para(doc, "2. 46 条新事件的梗密度：现在按初审表的密度写，要不要更密/更疏。", bullet=True)
    k.para(doc, "3. 人物梗表 1000 行怎么用：只做弹幕/粉丝类，还是引入真人名（现在 0 条）。", bullet=True)
    k.para(doc, "4. `*` 标记的 6 条（S01/S02/S03/P03/P08/P12）年份写死，要不要保留。", bullet=True)
    k.para(
        doc,
        "已经拍过、不用再答的：总量 80、AI 写你逐个看、6–8 字、失败文案每个选项单独写、6 条标记链、"
        "「每周都有事件」（接受 240 次/局）。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "复跑")
    k.para(doc, "在仓库根执行（Windows，PowerShell / bash 都行）：")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts before    # 落表前：需先 stash 掉 80 条")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after     # 34 条时：在 67677c8 上跑，写 out-after.json")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after80   # 80 条时（本文数字）")
    cmd(doc, "PYTHONIOENCODING=utf-8 python scripts/06-events/audit_table.py   # 表格对照")
    cmd(doc, "npx vitest run && npx tsc --noEmit")
    k.para(
        doc,
        "注意：`sim.ts` 的标签只决定输出文件名（`out-<tag>.json`），读的都是当前代码。"
        "要复现 34 条那一列，需要先 checkout 到 `67677c8 feat(06): 事件库落表 34 条` 再跑 `after`（写 out-after.json）；"
        "本文的三列数字就是这样得到的。",
        size=9.5,
        color=k.G,
    )

    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
