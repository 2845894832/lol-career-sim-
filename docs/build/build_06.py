# -*- coding: utf-8 -*-
"""docs/06-事件库扩容-材料.docx —— 06 号 ticket（事件库扩到多少、谁来写）的材料。

数据现读，不手填：
- scripts/06-events/out-before.json  ← `npx vite-node scripts/06-events/sim.ts before`
- scripts/06-events/out-after.json   ← `npx vite-node scripts/06-events/sim.ts after`
- src/data/events.ts 的 34 条（id / 类型 / 阶段 / once / weight / 正文）
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
AFTER = load("out-after.json")
BS = BEFORE["summary"]
AS = AFTER["summary"]


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
A_ROWS = event_stats(AFTER)
AVG = {r[0]: r[2] for r in A_ROWS}
MAXR = {r[0]: r[3] for r in A_ROWS}


def parse_events():
    src = open(os.path.join(ROOT, "src", "data", "events.ts"), encoding="utf-8").read()
    region = src[src.index("以下 34 条"):]
    out = []
    for blk in region.split("\n  {\n    id: '")[1:]:
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
            }
        )
    return out


EV = parse_events()
KIND_CN = {"match": "比赛", "life": "生活", "special": "特殊"}
PHASE_CN = {"growth": "成长", "peak": "巅峰", "decline": "衰退", "any": "任意"}


def main():
    doc = k.new_doc("06 · 事件库扩容 · 材料")

    k.title(
        doc,
        "事件库扩到多少、谁来写",
        "06 号 ticket · 2026-11-06 起草 · 34 条已落地，条数待你拍板 · 事实来自本机 master，模拟 24 局可复跑",
    )

    k.note(
        doc,
        "**本票未结案**：34 条初审表已全部进代码（`src/data/events.ts`，测试 69→72 全绿），"
        "但「扩到多少、谁来写、要不要留空周」三条要你定。文中所有推导都标了「未经用户确认」，"
        "不是既成决定。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "三句话")
    k.para(
        doc,
        f"**第一句：现在的「又是这个」是能量化的。** 落表前 24 局里，**{pct(BS['emptyRate'])}** 的周"
        f"根本没有事件；剩下的周里 E01 一局平均 **{f1(45.42)} 次**、单局最高 **48 次**。"
        "也就是说，玩家一局点掉的 240 个周里，有 166 周是空的，有接近 50 周是同一个故事。",
    )
    k.para(
        doc,
        "**第二句：34 条能把 E01 按下去，但会把「空周」填满。** 落表后 E01 降到 "
        f"{f1(A_ROWS[0][0] == 'E01' and A_ROWS[0][2] or [r for r in A_ROWS if r[0] == 'E01'][0][2])} 次/局，"
        f"代价是无事件周从 {pct(BS['emptyRate'])} 变成 **{pct(AS['emptyRate'])}**，每局事件数从 "
        f"{f1(BS['eventsPerRun'])} 涨到 **{f1(AS['eventsPerRun'])}** —— 每周都要做一次选择。",
    )
    k.para(
        doc,
        f"**第三句：单条仍然会重复到 20 次上下。** 落表后最高的一条 L02 一局平均 "
        f"**{AVG['L02']:.1f} 次**、单局最高 "
        f"**{MAXR['L02']} 次**。34 条解决的是「总是 E01」，"
        "还没解决「又是这条」——后者的门槛是 80 条左右（见第四节）。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "现状量化：24 局 × 240 周")
    k.para(
        doc,
        "口径：8 个种子 × 3 种策略（balanced / grind / noScrim），每局 240 周、每周一次事件抽取；"
        "遇到事件就选第 `(seed + week) % 选项数` 个选项，不挑最优。"
        "两列是同一批种子、同一套策略，只改了事件库。",
    )
    k.table(
        doc,
        ["指标", "落表前（E01–E05 + F01/F02）", "落表后（+34 条）"],
        [
            ["抽取总数", str(BS["totalDraws"]), str(AS["totalDraws"])],
            ["抽到事件", str(BS["totalEvents"]), str(AS["totalEvents"])],
            ["无事件周占比", pct(BS["emptyRate"]), pct(AS["emptyRate"])],
            ["每局事件数", f1(BS["eventsPerRun"]), f1(AS["eventsPerRun"])],
            ["每局空周数", f1(BS["emptiesPerRun"]), f1(AS["emptiesPerRun"])],
            ["出现过的不同事件数", str(BS["distinctEvents"]), str(AS["distinctEvents"])],
            ["单事件单局最高重复", str(BS["maxRepeatInRun"]), str(AS["maxRepeatInRun"])],
        ],
        [5.2, 5.6, 5.2],
        size=8.6,
        caption="表 2-1　同一种子、同一策略，只换事件库",
    )

    k.h2(doc, "落表前：一张表里只有一件事")
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

    k.h2(doc, "落表后：前五条仍然各自 12–22 次")
    rows = []
    for eid, total, avg, mx in A_ROWS[:8]:
        if eid.startswith(("SPR", "SUM", "INV", "F0")):
            continue
        rows.append([eid, KIND_CN.get(next((e["kind"] for e in EV if e["id"] == eid), ""), "—"), f1(avg), str(mx)])
    k.table(
        doc,
        ["事件", "类型", "每局平均", "单局最高"],
        rows[:8],
        [3.2, 3.2, 4.0, 4.0],
        size=8.6,
        caption="表 2-3　落表后重复最多的几条（24 局平均）",
    )
    k.para(
        doc,
        "原因很直接：34 条里有 **20 条可重复**，但权重分成 10 / 2 / 1 三档，"
        "10 那一档的十来条在 240 次抽取里各分到 12–22 次；2 和 1 的那批一局只出现 3–5 次。"
        "想让单条压到 5 次以内，得让「可重复池」从 20 条涨到 48 条以上。",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "三个方案：条数、工时、代价")
    k.para(doc, "算式（未经用户确认，但可以从实测反推）：")
    cmd(doc, "可重复条数 ≈ 240 ÷ 每局重复上限")
    cmd(doc, "总条数 ≈ 可重复条数 ÷ 0.59        # 现在 34 条里 20 条可重复")
    cmd(doc, "工时 ≈ 新写条数 × 20 分钟")
    k.para(
        doc,
        "240 是一局的抽取次数；0.59 是当前「可重复 ÷ 总数」的比例，用来把可重复条数折成总条数。"
        "这两个数都会随写法漂移（比如把更多事件写成 `once`，比例就降），所以下表的条数是起点，不是保证。",
        size=9.5,
        color=k.G,
    )
    k.table(
        doc,
        ["方案", "总条数", "新写", "目标重复", "工时", "代价"],
        [
            ["甲：就用现成 34 条", "34", "0", "实测 22–30 次/局", "0", "内容质量参差；梗可能过时；密度 240 次/局"],
            ["乙：补到 80 条", "80", "46", "≤5 次/局", "≈15.3 小时", "要按配额挑梗、写 46 条；一次写不完"],
            ["丙：补到 136 条", "136", "102", "≤3 次/局", "≈34 小时", "写作量翻倍；配额要靠模拟反复校准"],
        ],
        [3.9, 2.2, 2.0, 3.6, 2.6, 6.2],
        size=8.4,
        caption="表 3-1　三条路；工时只算写作，不含审稿与跑测试",
    )
    k.para(
        doc,
        "**甲已经做完了**（就是这次提交）。乙和丙的差别只在「重复上限」：5 次是「一局里同一条最多撞五回」，"
        "3 次是「基本记不住第二次」。按现在的权重写法，5 次对应的池子是 48 条可重复，3 次对应 80 条。",
    )
    k.para(
        doc,
        "**谁写**这一栏三个方案都没解决：可以 AI 按梗表扩写、你抽检；也可以你挑梗、AI 只写选项。"
        "上一轮 34 条是 AI 按表扩写、你还没抽检过——这件事要你定，我不替你选。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "配额表：丙方案的 136 条怎么分")
    k.para(
        doc,
        "按阶段分，依据是 240 周里各阶段占的周数：成长 2 年（60 周）、巅峰 4 年（120 周）、衰退 2 年（60 周）。"
        "目标是每个阶段单独看，单条也不超过 3 次。",
    )
    k.table(
        doc,
        ["阶段", "周数", "只在本阶段出现", "任意阶段（三边摊）", "合计"],
        [
            ["成长", "60", "20", "14", "34"],
            ["巅峰", "120", "40", "18", "58"],
            ["衰退", "60", "20", "14", "34"],
            ["任意阶段单列", "—", "—", "10", "10"],
            ["合计", "240", "80", "56", "136"],
        ],
        [3.2, 2.4, 4.4, 4.6, 2.4],
        size=8.6,
        caption="表 4-1　按阶段配额（未经用户确认；任意阶段的条数会同时稀释三个阶段，故单列 10 条）",
    )
    k.table(
        doc,
        ["类型", "条数", "为什么是这个数"],
        [
            ["比赛", "60", "比赛周只占 26/30 周；比赛事件要撑住这 208 周的抽取"],
            ["生活", "50", "任何周都能抽，负责把非比赛周填满"],
            ["特殊", "26", "大多 `once` + 写死年份，不参与日常稀释，只保证每年有节点"],
            ["合计", "136", "—"],
        ],
        [3.0, 2.4, 10.4],
        size=8.6,
        caption="表 4-2　按类型配额（未经用户确认）",
    )
    k.para(
        doc,
        "这张表是起点，不是结论：权重、`once` 比例、阶段过滤都会改变实际重复。"
        "正确用法是每写 20 条跑一次 `sim.ts`，看「单局最高重复」有没有降到目标，再调下一批的配额。",
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "已经落地的 34 条")
    k.para(
        doc,
        "全部来自 `P1-事件库-梗驱动-初审.xlsx`（22 条）与 `P1-事件库-人物梗-初审.xlsx`（12 条）。"
        "正文、标签、选项、成功场面、后果数值逐项照表；`scripts/06-events/audit_table.py` 的对照结果是 "
        "`table options 91 / diffs 0`。E01–E05 没动。",
    )
    rows = []
    for e in EV:
        rows.append(
            [
                e["id"],
                KIND_CN.get(e["kind"], e["kind"]),
                PHASE_CN.get(e["phase"], e["phase"]),
                "是" if e["once"] else "否",
                str(e["weight"]),
                e["text"][:22] + ("…" if len(e["text"]) > 22 else ""),
            ]
        )
    k.table(
        doc,
        ["ID", "类型", "阶段", "一次性", "权重", "正文（截断）"],
        rows,
        [1.6, 1.8, 1.8, 1.6, 1.4, 10.0],
        size=7.6,
        caption="表 5-1　34 条清单；类型/阶段/once/权重是从表里的「触发条件」和「复用策略」推的",
    )

    k.h2(doc, "转写时定了什么（都未经用户确认）")
    k.para(
        doc,
        "- **符号 → 数值**：表里的 `+` / `++` / `+++` 分别记 ±2 / ±4 / ±6；体力 ±8；金钱 −100；"
        "教练信任 ±3/个；写了数字的照抄。\n"
        "- **触发条件**：表里的「第 N 年」写成 `requires: s.year === N`，不用 `year` 写死，"
        "避免挡在决赛/邀请函前面（决赛是必触发，抢跑会破坏既有测试）。\n"
        "- **权重**：特殊事件 1，标「低频」的 2，其余 10。\n"
        "- **选项文案**：照表原样（6–8 字），没有压到设计文档要求的 ≤4 字。",
        size=9.5,
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "缺口：还没做的、做不了的")
    k.table(
        doc,
        ["缺口", "数量", "说明"],
        [
            ["失败分支没有文案", "43 处", "表里只给了失败后果的数值，没给台词；现在玩家只看到数值跳动"],
            ["成功文案只有一句场面", "90 / 91", "表里的「成功高光」直接当 `successText`，够用但不分选项语气"],
            ["选项文案超长", "全部", "设计文档要 ≤4 字，表里 6–8 字；谁让步要你定"],
            ["P03 / P08 年份写死", "2 条", "现在是软条件（第 1 / 2 年），要不要写死成年份节点"],
            ["P01 / P02 是否成对", "2 条", "一高一低，要不要强制同局都出现"],
            ["人物梗表未使用", "1000 行", "大多是外号，单独成不了事件；要不要拿来写弹幕/粉丝类"],
        ],
        [4.6, 2.2, 9.0],
        size=8.4,
        caption="表 6-1　缺口清单；前三条影响手感，后三条影响内容方向",
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "要你拍板的五个问题")
    k.para(doc, "1. 重复上限取 5 还是 3 —— 决定乙（80 条）还是丙（136 条）。", bullet=True)
    k.para(doc, "2. 谁写：AI 按梗表扩写你抽检，还是你挑梗、AI 只写选项。", bullet=True)
    k.para(doc, "3. 「每周都有事件」（240 次/局）能不能接受，还是要刻意留空周。", bullet=True)
    k.para(doc, "4. 43 处失败文案补不补；补的话谁来写。", bullet=True)
    k.para(doc, "5. 选项文案按设计文档压到 4 字，还是维持表里的 6–8 字。", bullet=True)
    k.para(
        doc,
        "在这五个问题有答案之前，我不会再往库里加事件 —— 加得越多，越像替你定了「密度」和「风格」。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "复跑")
    k.para(doc, "在仓库根执行（Windows，PowerShell / bash 都行）：")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts before   # 复现落表前：先 stash 掉 34 条再跑")
    cmd(doc, "npx vite-node scripts/06-events/sim.ts after    # 落表后")
    cmd(doc, "PYTHONIOENCODING=utf-8 python scripts/06-events/audit_table.py   # 表格对照")
    cmd(doc, "npx vitest run && npx tsc --noEmit")
    k.para(
        doc,
        "注意：`before` 与 `after` 读的是同一份当前代码，标签只决定输出文件名（`out-before.json` / "
        "`out-after.json`）。要复现「落表前」的数字，需要先 `git stash` 掉 34 条再跑 `before`；"
        "本文里的 before 数字就是这样得到的。",
        size=9.5,
        color=k.G,
    )

    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
