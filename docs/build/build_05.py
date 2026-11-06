# -*- coding: utf-8 -*-
"""docs/05-对手强度表-材料.docx —— 05 号 ticket（对手强度表）的材料。

数据全部现读，不手填：
- scripts/05-opponent/table.json  ← `npx vite-node scripts/05-opponent/table.ts`
  （每队强度 = 5 名选手 ovr 的算术平均，来源 src/data/rosters.ts）
- scripts/05-opponent/out.json    ← `npx vite-node scripts/05-opponent/sim.ts`
  （8 种子 × 3 策略 × 新旧两种强度 = 48 局）
顺带生成 docs/05-对手强度表-全量.md（131 队全表）。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(ROOT, "docs", "05-对手强度表-材料.docx")
OUT_MD = os.path.join(ROOT, "docs", "05-对手强度表-全量.md")


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
    with open(os.path.join(ROOT, "scripts", "05-opponent", name), encoding="utf-8") as fh:
        return json.load(fh)


TABLE = load("table.json")
SIM = load("out.json")
SEASONS = TABLE["seasons"]
S = SIM["summary"]
FIX = S["fixed"]
NEW = S["roster"]
DELTA = (NEW["winRate"] - FIX["winRate"]) * 100

ALL_TEAMS = [dict(t, season=s["season"]) for s in SEASONS for t in s["teams"]]
ALL_AVG = sum(t["strength"] for t in ALL_TEAMS) / len(ALL_TEAMS)
ALL_MIN = min(t["strength"] for t in ALL_TEAMS)
ALL_MAX = max(t["strength"] for t in ALL_TEAMS)


def pick(kind, n=5):
    rows = sorted(ALL_TEAMS, key=lambda x: -x["strength"])
    if kind == "top":
        out = rows[:n]
    elif kind == "mid":
        mid = len(rows) // 2
        out = rows[mid - n // 2: mid + n // 2 + 1]
    else:
        out = rows[-n:]
    return out, rows


def main():
    doc = k.new_doc("05 · 对手强度表 · 材料")

    k.title(
        doc,
        "对手强度：从占位常量换成名单真值",
        "05 号 ticket · 2026-11-05 起草，2026-11-06 拍板 · 事实来自本机 master；模拟 48 局可复跑",
    )

    k.note(
        doc,
        "**已拍板（2026-11-06）**：A 照用名单真值；决赛对手用当季第一；`winChance` 与 `matchRate` 统一；"
        "E01 的 60 也是占位，已接名单。三处代价都记在第 7 节，数字全部可复跑。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "三句话")
    k.para(
        doc,
        f"**第一句：旧的 60 不是「略低」，是整体低了 17 分。** 名单里 {len(ALL_TEAMS)} 支队的五人 ovr 均值是 "
        f"**{f1(ALL_AVG)}**（最低 {f1(ALL_MIN)}，最高 {f1(ALL_MAX)}）。按现在的公式分母 K=50，"
        f"差 17 分就是每场多 **34 个百分点** 的胜率。",
    )
    k.para(
        doc,
        "**第二句：真实强度其实早就算好了，只是没接到信任那条线上。** 积分榜和赛程表的胜率一直用名单真值"
        "（`league.ts` 的 `winChance` / `standings`）；真正决定教练信任、伤病、荣誉的那一场，"
        "用的是 `opponentDefault=60`。于是同一周里，赛程表显示五五开，实际结算却是八成赢。",
    )
    k.para(
        doc,
        f"**第三句：接上真值后，模拟胜率从 {pct(FIX['winRate'])} 掉到 {pct(NEW['winRate'])}"
        f"（**{DELTA:+.1f} 个百分点**）。** 分两步：只换掉常规赛/决赛的 60/78，是 {pct(FIX['winRate'])} → 57.4%（−25.6 pp）；"
        "再把 E01 的占位对手也换成真值，才到 46.0%（又 −11.4 pp）。同一套决策、同一批种子，只是对手换了算法。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "现在强度是怎么来的：两条并行的比赛线")
    k.table(
        doc,
        ["比赛线", "什么时候跑", "对手强度", "结果写到哪"],
        [
            [
                "信任主线（手感）",
                "每个比赛周（1–26）",
                "改之前：`isFinalWeek ? 78 : 60`（常量）",
                "`coachTrust` / 人气 / 伤病 / S 赛荣誉",
            ],
            [
                "赛程表（战绩）",
                "13 个常规赛周（2,4,…,26）",
                "`rivalStrength(year, rivalId)`，名单真值",
                "`seasonResults` → 积分榜、名次",
            ],
        ],
        [3.1, 3.4, 5.2, 4.3],
        size=8.2,
        caption="表 2-1　两条线各算各的；只有第一条影响信任",
    )
    k.para(
        doc,
        "**出处（改之前）**：`src/core/reduce.ts:169-179` 的 `settleMatch()` 里写死 "
        "`const opponent = isFinalWeek(state) ? CONFIG.match.opponentFinal : CONFIG.match.opponentDefault;`；"
        "`src/core/reduce.ts:230-248` 的赛程块用 `winChance(state, fixture.rivalId)`。"
        "两条线互不知道对方算了什么。",
    )
    k.para(
        doc,
        "**常量散在四个地方**，改之前谁也不知道该信哪个：`src/config.ts:158`（60）、"
        "`src/config.ts:160`（78）、`src/data/finals.ts:26`（春决 65）、`src/data/finals.ts:72`（夏决 70）；"
        "另外 `src/data/events.ts:112` 的 S 赛事件也直接读 78，`src/data/events.ts:13` 的 E01 写死 60。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "强度公式：两边其实是同一个式子")
    k.para(doc, "**我方强度**（`src/core/league.ts:164`）：签约后 = 场上五人 ovr 的算术平均（首发替下名单里最弱的那位，见 `mySquad`）；未签约 = 六维均值。")
    k.para(doc, "**胜负**（`src/core/match.ts:34-42`）：")
    cmd(doc, "p = 0.5 + (我方强度 − 对手强度) / 50 + 临场加成 + (信任 − 40) × 0.001")
    k.para(doc, "结果夹在 5%–95%。`winChance`（`src/core/league.ts:224`）是同一个式子的另一份拷贝，也夹 5–95%。")
    k.para(
        doc,
        "**这条式子说明「对手强度」和「我方强度」是同一把尺子**：换掉对手，等于给每场比赛平移一个固定差值。"
        "所以 60 → 77 不是「微调」，是 17 分的平移。",
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "从名单算出来的强度表")
    k.para(
        doc,
        "口径：每队强度 = 该队 5 名选手 `ovr` 的算术平均，**和代码里的 `teamStrength()` 完全一致**"
        "（`src/data/rosters.ts:165-167`）。没有手工调整、没有平滑、没有赛季权重。",
    )
    rows = []
    for s in SEASONS:
        top = s["teams"][0]
        bot = s["teams"][-1]
        rows.append([
            s["season"],
            str(s["count"]),
            f1(s["average"]),
            f1(s["median"]),
            f"{top['name']} {f1(top['strength'])}",
            f"{bot['name']} {f1(bot['strength'])}",
        ])
    k.table(
        doc,
        ["赛季", "队数", "均值", "中位", "最强", "最弱"],
        rows,
        [1.7, 1.4, 2.2, 2.2, 4.2, 4.2],
        size=8.2,
        caption=f"表 4-1　按赛季汇总；{len(ALL_TEAMS)} 队总均值 {f1(ALL_AVG)}，范围 {f1(ALL_MIN)}–{f1(ALL_MAX)}",
    )

    k.h2(doc, "冠军档 / 中位档 / 垫底档（各 5 队）")
    picks = pick("top")[0] + pick("mid")[0] + pick("bottom")[0]
    rows = []
    for i, t in enumerate(picks):
        tier = "冠军档" if i < 5 else ("中位档" if i < 10 else "垫底档")
        rows.append([tier, t.get("season", ""), t["name"], f1(t["strength"]), str(t["rank"])])
    k.table(
        doc,
        ["档位", "赛季", "队伍", "强度", "赛季内排名"],
        rows,
        [2.4, 2.0, 4.6, 2.4, 3.4],
        size=8.4,
        caption="表 4-2　完整 131 队见 docs/05-对手强度表-全量.md",
    )
    k.para(
        doc,
        f"**看这张表只要记一件事**：真实对手从 {f1(ALL_MIN)} 到 {f1(ALL_MAX)}，旧的 60 比最弱的队还低 9 分。"
        "也就是说旧代码里，玩家打谁都是「打一支不存在的鱼腩」。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "代码改了什么")
    k.table(
        doc,
        ["文件", "位置", "改动"],
        [
            ["`src/config.ts`", "156–160", "新增 `opponentSource`（默认 `'roster'`）；60/78 注释改成「兜底」，只在 `'fixed'` 时用"],
            ["`src/core/state.ts`", "40–43", "`isFinalWeek()` 从 reduce.ts 挪到这里，供 league/events 共用"],
            ["`src/core/league.ts`", "176–221", "新增 `seasonStrengths` / `seasonAverageStrength` / `seasonTopStrength` / `opponentStrength` / `finalOpponentStrength`"],
            ["`src/core/reduce.ts`", "172", "`settleMatch()` 的对手改调 `opponentStrength(state)`"],
            ["`src/core/events.ts`", "82–91", "`successRateOf()` 认 `opponentRole: 'final'`；没写死对手的比赛事件回落到当周对手"],
            ["`src/data/finals.ts`", "26–27、72–73", "春决 / 夏决加 `opponentRole: 'final'`，65/70 降为兜底"],
            ["`src/data/events.ts`", "112–113", "S 赛 E03 加 `opponentRole: 'final'`"],
            ["`src/types.ts`", "128", "`GameEvent.opponentRole?: 'final'`"],
            ["`src/core/odds.ts`", "1–24（新文件）", "唯一的胜率公式 `winProbability()`；`formulaK`、5%–95% 上下限、信任系数只在这里读"],
            ["`src/core/league.ts`", "174–180、235–237", "新增 `myMatchStrength()`（签约=五人均值 / 路人期=六维均值）；`winChance()` 改调同一个公式"],
            ["`src/core/match.ts`", "36–38", "`matchRate()` 瘦成一行：`winProbability(myMatchStrength(state), …)`"],
            ["`tests/core.test.ts`", "266–368", "新增 6 个测试：赛程周 / 非赛程周 / 决赛周 / 决赛事件 / fixed 兜底 / winChance≡matchRate"],
        ],
        [3.3, 2.5, 10.2],
        size=7.9,
        caption="表 5-1　改动的文件与行号（本机 master，改后会漂）",
    )
    k.para(
        doc,
        "**决赛规则**：春决文案写的是「对面是常规赛第一」，所以决赛取**当季最强队**，而不是「参赛两队里较强的一侧」——"
        "这一代没有给四强/半决赛建模，进决赛的两支队没有单独存。第 3 年 S 赛的对手因此是 S10 的 JDG，强度 83.0（旧的 78）。",
    )
    k.para(
        doc,
        "**保留 `fixed` 模式不是给玩家用的**：它只为把新旧两套数放在同一套种子下复跑。正式流程读 `'roster'`。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "新旧对比：48 局，同一套决策")
    k.para(
        doc,
        "8 个种子 × 3 种策略（balanced / grind / noScrim）× 2 种强度。每局跑到第 8 年结束。"
        "胜负按日志里的「赢了。」/「输了」，也就是**信任主线**那 26 场/年；名次取每年第 30 周的联赛排名。",
    )

    rows = [
        ["信任主线比赛场数", str(FIX["matches"]), str(NEW["matches"]), f"{NEW['matches'] - FIX['matches']:+d}"],
        ["胜率", pct(FIX["winRate"]), pct(NEW["winRate"]), f"{DELTA:+.1f} pp"],
        ["平均每局胜场（8 年）", f1(FIX["winsAvg"]), f1(NEW["winsAvg"]), f"{NEW['winsAvg'] - FIX['winsAvg']:+.1f}"],
        ["跑完 8 年的局数", f"{FIX['finished8']}/24", f"{NEW['finished8']}/24", "—"],
        ["进决赛（局数 / 平均次数）", f"{FIX['finalsRuns']}/24 · {f1(FIX['finalsAvg'])}", f"{NEW['finalsRuns']}/24 · {f1(NEW['finalsAvg'])}", "0"],
        ["全胜赛季", f"{FIX['allWin']}/{FIX['seasonCount']}", f"{NEW['allWin']}/{NEW['seasonCount']}", f"{NEW['allWin'] - FIX['allWin']:+d}"],
        ["全败赛季", f"{FIX['allLoss']}/{FIX['seasonCount']}", f"{NEW['allLoss']}/{NEW['seasonCount']}", "0"],
        ["最终段位", " / ".join(f"{a} {b}" for a, b in FIX["tiers"].items()), " / ".join(f"{a} {b}" for a, b in NEW["tiers"].items()), "同"],
        ["信任终值（均值）", f1(FIX["trustAvg"]), f1(NEW["trustAvg"]), f"{NEW['trustAvg'] - FIX['trustAvg']:+.1f}"],
        [
            "信任 <25 的局数",
            f"{FIX['trustLow']}/24",
            f"{NEW['trustLow']}/24",
            f"{NEW['trustLow'] - FIX['trustLow']:+d}",
        ],
    ]
    k.table(
        doc,
        ["指标", f"旧：60 / 78", f"新：名单真值", "差"],
        rows,
        [5.6, 4.0, 4.0, 2.6],
        size=8.4,
        caption="表 6-1　48 局汇总；胜率、胜场、全胜赛季是主要差异",
    )

    k.h2(doc, "每年胜场 / 每年名次")
    rows = []
    for i in range(8):
        rows.append([
            f"第 {i + 1} 年",
            f1(FIX["winsByYear"][i]),
            f1(NEW["winsByYear"][i]),
            f1(FIX["placeByYear"][i]),
            f1(NEW["placeByYear"][i]),
        ])
    k.table(
        doc,
        ["年份", "旧胜场", "新胜场", "旧名次", "新名次"],
        rows,
        [3.0, 3.2, 3.2, 3.2, 3.2],
        size=8.4,
        caption="表 6-2　名次 1 最好；名次几乎没动，因为积分榜那条线本来就用真值",
    )

    k.h2(doc, "按策略拆（确认不是某个策略带偏）")
    rows = []
    for a, b in zip(FIX["byStrategy"], NEW["byStrategy"]):
        rows.append([
            a["strategy"],
            pct(a["winRate"]),
            pct(b["winRate"]),
            f"{(b['winRate'] - a['winRate']) * 100:+.1f} pp",
            f1(a["winsAvg"]),
            f1(b["winsAvg"]),
        ])
    k.table(
        doc,
        ["策略", "旧胜率", "新胜率", "差", "旧胜场", "新胜场"],
        rows,
        [3.0, 2.8, 2.8, 2.8, 2.6, 2.6],
        size=8.4,
        caption="表 6-3　三种策略都掉 20 个百分点左右，方向一致",
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "拍板结果：A 照用真值（2026-11-06）")
    k.para(
        doc,
        "用户 2026-11-06 原话三句：「**A 照现在这样应用**」「**决赛对手用「当季第一」可接受**」「**统一 winChance 与 matchRate**」。"
        f"所以上面那个 {abs(DELTA):.1f} 个百分点的变化是**主动接受**的（A）；"
        "其中最后约 11.4 个点来自 E01，单独记在本节末尾。",
        size=10,
    )
    k.table(
        doc,
        ["问题", "结果", "落地"],
        [
            ["A / B / C 选哪条", "A：照现在这样应用", "`opponentSource='roster'` 保持默认；B（难度偏移）、C（改公式）不采用"],
            ["决赛对手", "当季第一，可接受", "决赛分支不变：`seasonTopStrength()`；这一代没有四强/半决赛建模"],
            ["两条线公式", "统一", "新增 `src/core/odds.ts`；`matchRate` 与 `winChance` 都调 `winProbability()`"],
        ],
        [3.6, 4.4, 7.8],
        size=8.4,
        caption="表 7-1　三条已定；出处：用户 2026-11-06 回复",
    )
    k.para(
        doc,
        "**统一公式带来的数值变化**：信任主线那 26 场的胜率一点没变（公式只是搬了个家）；变的是赛程表那 13 场——"
        "`winChance` 现在也带（信任 − 40）× 0.001 的微调，信任 64 时约 +2.4 个百分点。"
        f"统一公式本身不改信任主线的胜率（57.4% 那一段是纯公式搬家）；第 6 节现在显示 {pct(FIX['winRate'])} / {pct(NEW['winRate'])}，"
        "多出来的那段就是 E01。名次略动（例如第 1 年 7.2 → 7.0）。",
        size=9.5,
        color=k.G,
    )
    k.para(
        doc,
        f"**还剩一件没做：真机手感实测。** {pct(NEW['winRate'])} 是模拟出来的，玩家会不会觉得「练了也没用」，要真人打几局才知道；"
        "如果实测偏难，B / C 两条路仍然在桌上（见上一版材料记录，或直接调 `CONFIG.match.formulaK`）。",
        size=9.5,
        color=k.G,
    )

    k.h2(doc, "追加：E01 的 60 也是占位（2026-11-06 晚）")
    k.para(
        doc,
        "用户答复「**是占位**」，于是 E01 的 `opponent: 60` 已删，和别的比赛事件一样按当周对手算。"
        "代价比预想大：E01 是 growth 期的高频可重复事件，48 局里触发 1101 次（约 46 次/局），"
        "胜率从原来的八成五掉到五成出头，还会连带压信任。",
    )
    k.table(
        doc,
        ["指标", "E01 接名单前", "接上后", "差"],
        [
            ["信任主线胜率", "57.4%", f"{pct(NEW['winRate'])}", "−11.4 pp"],
            ["平均每局胜场（8 年）", "80.5", f"{f1(NEW['winsAvg'])}", f"−{80.5 - NEW['winsAvg']:.1f}"],
            ["全胜赛季", "5/184", f"{NEW['allWin']}/{NEW['seasonCount']}", f"{NEW['allWin'] - 5:+d}"],
            ["全败赛季", "0/184", f"{NEW['allLoss']}/{NEW['seasonCount']}", f"+{NEW['allLoss']}"],
            ["信任终值", "64.1", f"{f1(NEW['trustAvg'])}", f"{NEW['trustAvg'] - 64.1:+.1f}"],
        ],
        [5.4, 4.0, 4.0, 3.0],
        size=8.4,
        caption="表 7-2　两次连跑，代码只差 E01 那一行；E01 每局约 46 次",
    )
    k.para(
        doc,
        "**这一段要不要接受，得你定。** 它不在你 11-06 那三条里——那三条说的是 A、决赛、统一公式；"
        "E01 是你补充确认的占位，接上后的 −11.4pp 是新的信息。可选：接受；或把 E01 失败的 −5 信任调小 / 权重调低（我没有擅自改数值）。"
        "另外要注意「全败赛季」从 0 变成 2/184，这是接 E01 之后才出现的。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "风险 / 还没做的")
    k.para(
        doc,
        f"**1. 模拟不是玩家实测。** 48 局只能说明方向和量级；{pct(NEW['winRate'])} 这个数会随策略、种子、事件选择变化，不要当成承诺。",
        bullet=True,
    )
    k.para(
        doc,
        "**2. 两条线还是两条线。** 这次只把「信任主线」的对手换成了真值，赛程表的 13 场仍独立结算。"
        "同一周可能打两场不同的比赛（一场算信任、一场算战绩），这个结构本身没动。",
        bullet=True,
    )
    k.para(
        doc,
        "**3. 决赛取「当季第一」是权宜。** 真实赛制里决赛对手是另一半区杀出来的队，不一定是常规赛第一；"
        "这代没有四强建模，所以先用第一。以后加季后赛，这里要改。",
        bullet=True,
    )
    k.para(
        doc,
        "**4. E01 也接上名单了，代价单独记在第七节末尾。** 它原来写死 60，用户 2026-11-06 确认「是占位」，"
        "现已删掉该字段、按当周对手算；`event.opponent` 只剩「还没接名单的事件」和 fixed 模式的决赛兜底。",
        bullet=True,
    )
    k.para(
        doc,
        "**5. 公式已合并，赛程表会随信任浮动。** 两处都调 `src/core/odds.ts` 的 `winProbability()`；"
        "代价是赛程表显示的胜率带上了信任微调（信任 64 时约 +2.4 个百分点）。这是统一的必然结果，不是新 bug。",
        bullet=True,
    )

    # ---------------- 九 ----------------
    k.h1(doc, "九", "怎么复跑")
    k.para(doc, "在仓库根目录（`vibe-game-producer/`）执行：")
    cmd(doc, "npx vite-node scripts/05-opponent/table.ts   # 生成强度表 table.json")
    cmd(doc, "npx vite-node scripts/05-opponent/sim.ts     # 48 局新旧对比 out.json")
    cmd(doc, "python docs/build/build_05.py                # 重新生成本文档 + 全量表")
    cmd(doc, "npx tsc --noEmit && npx vitest run           # 类型 + 68 个测试")
    k.para(
        doc,
        "`table.ts` 只读 `src/data/rosters.ts`；`sim.ts` 只读 `src/`，新旧差别只在进程内改 "
        "`CONFIG.match.opponentSource`，不改文件。",
        size=9.5,
        color=k.G,
    )

    # ---------------- 十 ----------------
    k.h1(doc, "十", "接下来")
    k.para(doc, "05 本身已定稿。剩下三件事都不是这张票能自己结的：")
    k.para(doc, f"**① 真机手感实测。** {pct(NEW['winRate'])} 的胜率是否舒服，只能真人打几局；觉得难就回来选 B / C。", bullet=True)
    k.para(doc, "**② 季后赛建模。** 若你要「另一半区杀出来的决赛对手」，得先定四强/半决赛怎么算；现在的「当季第一」是权宜。", bullet=True)
    k.para(doc, "**③ E01 的对手 60 是否也是占位。** 现在的判断是「作者手写的剧情难度」，保留未动；若是占位，另开票。", bullet=True)

    doc.save(OUT)

    # ---------- 全量 md ----------
    lines = [
        "# 05 · 对手强度全量表（S8–S15，131 队）",
        "",
        "由 `npx vite-node scripts/05-opponent/table.ts` 生成，再经 `docs/build/build_05.py` 落盘。",
        "口径：队伍强度 = 该队 5 名选手 `ovr` 的算术平均，与 `src/data/rosters.ts` 的 `teamStrength()` 一致。",
        f"总均值 {ALL_AVG:.2f}，中位见各表，范围 {ALL_MIN:.2f}–{ALL_MAX:.2f}。",
        "",
    ]
    for s in SEASONS:
        lines.append(f"## {s['season']}（{s['count']} 队，均值 {s['average']:.2f}，中位 {s['median']:.2f}）")
        lines.append("")
        lines.append("| 排名 | 队伍 | 强度 |")
        lines.append("|---|---|---|")
        for t in s["teams"]:
            lines.append(f"| {t['rank']} | {t['name']} | {t['strength']:.2f} |")
        lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("已写出", OUT)
    print("已写出", OUT_MD)


if __name__ == "__main__":
    main()
