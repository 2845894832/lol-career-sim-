# -*- coding: utf-8 -*-
"""生成 ticket 07 的「新赛程下四种荣誉评定规则」待审表。

只写 Excel，不改代码。输出到仓库根 P1-荣誉-待审.xlsx。
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "P1-荣誉-待审.xlsx"

NAVY = "1F3B57"
WHITE = "FFFFFF"
LIGHT = "EEF3F8"
YELLOW = "FFF2CC"
GREY = "F2F2F2"
BORDER_CLR = "D6DCE5"

TITLE_FONT = Font(name="Microsoft YaHei", size=16, bold=True, color=NAVY)
SUB_FONT = Font(name="Microsoft YaHei", size=9, color="5B6770")
HEAD_FONT = Font(name="Microsoft YaHei", size=10, bold=True, color=WHITE)
BODY_FONT = Font(name="Microsoft YaHei", size=9, color="1F2933")
HONOR_FONT = Font(name="Microsoft YaHei", size=10, bold=True, color=NAVY)
NOTE_FONT = Font(name="Microsoft YaHei", size=9, color="7A5A00")

HEAD_FILL = PatternFill("solid", fgColor=NAVY)
YELLOW_FILL = PatternFill("solid", fgColor=YELLOW)
GREY_FILL = PatternFill("solid", fgColor=GREY)

THIN = Side(style="thin", color=BORDER_CLR)
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top", horizontal="left")
CENTER = Alignment(wrap_text=True, vertical="center", horizontal="center")

ROWS = [
    {
        "honor": "赛程 · 联赛决赛",
        "trigger": (
            "已定：第 25 周联赛决赛，常规赛前 2 名直接打一场；你不在前 2 就没有决赛事件。\n"
            "获胜 → lpl-champion；一年 1 次；不扩季后赛。\n"
            "（你被替补时，队伍夺冠也不写个人荣誉。）"
        ),
        "basis": (
            "新赛程取消春/夏双决，lpl-champion 从一年最多 2 次降为 1 次。\n"
            "当前 finalFor() 只认春决第 15 周 / 夏决第 30 周，没有名次门槛"
            "（src/data/finals.ts:16-29,65-75）。"
        ),
        "question": (
            "Q1 已定：前 2 直接打一场，不扩季后赛。\n"
            "➡️ 记录，无需再答。"
        ),
    },
    {
        "honor": "赛程 · S 赛",
        "trigger": (
            "第 26 周无比赛；第 27 周小组赛；第 28 周八强；第 29 周四强；第 30 周决赛。\n"
            "S 赛固定 16 队；LPL 前 4 参加；小组赛自动模拟，出线后八强/四强/决赛各打一场；"
            "你首发并赢下决赛 → worlds-champion。"
        ),
        "basis": (
            "你 m00606 定：每年 S 赛 16 队、LPL 前 4、小组赛自动模拟。"
            "当前代码只有第 3 年第 26 周一场决赛"
            "（src/data/events.ts:108-116 E03），没有小组赛/八强/四强；"
            "需要新增 27–30 的赛程与自动模拟。\n"
            "第 26 周明确无比赛，但现有 isMatchWeek 是 week <= 26"
            "（src/core/state.ts:36-37）；新赛程要改成「26 不打、27–30 打」，"
            "不能再用单一边界。"
        ),
        "question": (
            "Q3 已定：16 队 / LPL 前 4 / 小组赛自动模拟 / 八强、四强、决赛可打。\n"
            "➡️ 记录，无需再答。"
        ),
    },
    {
        "honor": "荣誉 · MSI 冠军（已删除）",
        "trigger": (
            "已定：不办 MSI；从 HonorId / HONOR_LABEL 删除 msi-champion；"
            "代码中不再存在这个荣誉。\n"
            "名人堂的国际冠军门槛只看 S 冠军。"
        ),
        "basis": (
            "你 m00606 定 A：删除。msi-champion 从未被写入；"
            "删除后图鉴、结局、UI 都不再出现。"
        ),
        "question": (
            "Q2 已定：A 删除，无需再答。\n"
            "➡️ 记录。"
        ),
    },
    {
        "honor": "荣誉 · 常规赛 MVP",
        "trigger": (
            "第 25 周决赛前结算：已签约 + 当前首发 + 常规赛名次前 4 + "
            "五维均值 ≥85 → season-mvp。\n"
            "人气不计入。"
        ),
        "basis": (
            "常规赛第 24 周结束，第 25 周决赛前是自然结算点。\n"
            "myPlace() 用 16–17 队积分榜（src/core/league.ts:265）；"
            "myOvr() 是五项均值（:110）；85 = 名单 p90。\n"
            "其他选手没有赛季数据，只能用「名次 + 门槛」代理。"
        ),
        "question": (
            "Q4 已定：前 4 + ≥85 + 首发；人气不参与。\\n"
            "➡️ 记录，无需再答。\n"
            ""
        ),
    },
    {
        "honor": "荣誉 · 最佳阵容",
        "trigger": (
            "同第 25 周决赛前：已签约 + 首发 + 名次前 4 + 五维 ≥82 → all-pro。\n"
            "可与 MVP 同年同时拿。"
        ),
        "basis": (
            "前 4 = 16–17 队的前 23.5–25%；"
            "82 高于 p75=81、低于 p90=85。\n"
            "最佳阵容与 MVP 同为前 4，靠 82 / 85 两级门槛拉开。"
        ),
        "question": (
            "Q5 已定：前 4 + ≥82。\n"
            "➡️ 记录，无需再答。"
        ),
    },
    {
        "honor": "荣誉 · 名人堂",
        "trigger": (
            "退役或第 8 年到期时结算一次：荣誉总数 ≥8，且至少 1 个 S 冠军"
            "（MSI 已取消）→ hall-of-fame（年份=退役年）。"
        ),
        "basis": (
            "新赛程下 lpl-champion 一年 1 个（原 2 个），S 每年 1 个（若夺冠）；"
            "8 个荣誉比旧赛程更难。\n"
            "state.honors 只记 {id, year}，addHonor 只 push（src/core/state.ts:145）；"
            "hasHonor 不区分次数（:150）。\n"
            "纯数数会把「联赛冠军多」等同于「伟大」，保留 S 冠军门槛。"
        ),
        "question": (
            "Q6 已定：≥8 + 至少 1 个 S 冠军；MSI 不办，国际冠军只看 S。\\n"
            "➡️ 记录，无需再答。\n"
            ""
        ),
    },
    {
        "honor": "通用 · 频次",
        "trigger": (
            "MVP / 最佳阵容：每年最多 1 次，可跨年重复。\n"
            "名人堂：整局只 1 次。"
        ),
        "basis": (
            "hasHonor() 只判「有没有」不判次数；重复获得靠 honors 数组多条同 id 记录。\n"
            "UI 已按年分组并显示 ×N（src/ui/main.ts:352-372），不用改 UI。"
        ),
        "question": (
            "Q7 已定：年年可评、可重复；名人堂只一次。\n"
            "➡️ 记录，无需再答。"
        ),
    },
    {
        "honor": "通用 · 时点",
        "trigger": (
            "第 25 周先评 MVP/最佳阵容，再打联赛决赛；"
            "第 30 周 S 决赛后进年终结算；第 8 年也先评再出结局。\n"
            "退役时先评名人堂，再出结局。"
        ),
        "basis": (
            "advanceToNextYear() 现在先 year += 1，再判 >8 直接出结局"
            "（src/core/reduce.ts:285-293）；照原样加结算，第 8 年荣誉会丢。\n"
            "retire() 设 retired = true 后立刻 normalEnding('retired')"
            "（:310），名人堂要在算结局前写。"
        ),
        "question": (
            "Q8 已定：第 8 年也先评再出结局。\n"
            "➡️ 记录，无需再答。"
        ),
    },
]

SCHEDULE = [
    (
        "14",
        "13",
        "2、4、6、8、9、11、13、15、17、19、20、22、24",
        "不办 MSI；用原排法",
        "原第 13 周 MSI 方案作废",
    ),
    (
        "16",
        "15",
        "2、4、5、7、8、10、11、13、15、16、18、19、21、22、24",
        "不办 MSI；用原排法",
        "原第 13 周 MSI 方案作废",
    ),
    (
        "17",
        "16",
        "2、3、5、6、8、9、11、12、14、15、17、18、20、21、23、24",
        "不办 MSI；用原排法",
        "第 13 周仍空着",
    ),
]

FACTS = [
    ("赛程（已确认）", "30 周/年；第 2–24 周单循环联赛；第 25 周联赛决赛；第 26 周无比赛；第 27 周小组赛 / 28 八强 / 29 四强 / 30 决赛。", "你 m00298 / m00349 确认的排法"),
    ("单循环场次", "场次 N = 当年队数 − 1；14/16/17 队分别 13/15/16 场。", "14/16/17 队单循环"),
    ("联赛周次", "第 i 场放在 2 + round(i × 22 ÷ (N−1)) 周；首场第 2 周，末场第 24 周。", "本表方案"),
    ("MSI", "已定不办；msi-champion 已删除；HOF 只看 S 冠军。", "你 m00606"),
    ("S 赛现状", "只有第 3 年第 26 周一场决赛；没有小组赛/八强/四强；新赛程要 27–30 四段。", "src/data/events.ts:108-116"),
    ("比赛周判定", "现在 isMatchWeek 是 week <= 26；新赛程 26 不打、27–30 打，需要改判定。", "src/core/state.ts:36-37"),
    ("S 赛资格", "16 队；LPL 前 4；小组赛自动模拟；出线后八强/四强/决赛各打一场。", "你 m00606"),
    ("联赛决赛现状", "已定：第 25 周单决赛，常规赛前 2 直接打一场，不扩季后赛。", "你 m00395；src/data/finals.ts:16-29,65-75"),
    ("荣誉结构", "{ id: HonorId; year: number }，数组 honors: HonorEntry[]。", "src/types.ts:63-66, :206"),
    ("写入 / 查重", "addHonor push { id, year }；hasHonor 只判有没有，不区分次数。", "src/core/state.ts:145-152"),
    ("联赛名次", "standings 生成 16–17 队积分榜；myPlace 返回我的名次。", "src/core/league.ts:243, :265"),
    ("五维均值", "myOvr = 操作/对线/团战/意识/心态 五项均值，不含人气。", "src/core/league.ts:110"),
    ("人气口径", "人气只在场外生效，不参与比赛判定。", "src/types.ts:8"),
    ("名单 ovr 分位", "655 人：p10=71 / p25=73 / p50=77 / p75=81 / p90=85 / p95=87 / p99=89 / max=91。", "src/data/rosters.ts（统计）"),
    ("当季最强队", "S8–S15 的 LPL 最强队强度 83.0–87.4。", "src/core/league.ts:187 + 名单"),
    ("联赛前 4 / 属性 82", "16–17 队里前 4 = 23.5–25%；82 高于 p75=81、低于 p90=85。", "按 standings 队数 + 名单分位"),
    ("现有荣誉写入", "lpl-champion 旧赛程一年最多 2，新赛程 1；worlds-champion 旧仅第 3 年 1，新赛程每年 1（若夺冠）；rookie-of-year 第 2 年 1。", "src/data/finals.ts；src/core/match.ts；src/core/reduce.ts:305"),
    ("MSI 冠军", "已定从 HonorId / HONOR_LABEL 删除；不再有该荣誉。", "你 m00606"),
    ("存档", "CONFIG.version = 3，版本不符旧档直接作废；本方案不新增字段。", "src/config.ts:7；src/core/save.ts:19"),
    ("UI 显示", "荣誉按年分组，同 id 同年显示 ×N。", "src/ui/main.ts:352-372"),
]


def style_cell(cell, font=BODY_FONT, fill=None, align=WRAP):
    cell.font = font
    cell.border = BORDER
    cell.alignment = align
    if fill:
        cell.fill = fill


def build_review_sheet(ws):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = NAVY

    widths = {"A": 18, "B": 52, "C": 58, "D": 46, "E": 16}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    ws.merge_cells("A1:E1")
    ws["A1"] = "07 号 · 新赛程下的荣誉规则待审表"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 34

    ws.merge_cells("A2:E2")
    ws["A2"] = (
        "赛程前提（你已确认）：30 周/年；第 2–24 周单循环联赛；"
        "第 25 周联赛决赛；第 26 周无比赛；"
        "第 27 周小组赛 / 28 八强 / 29 四强 / 30 决赛。"
    )
    ws["A2"].font = SUB_FONT
    ws["A2"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[2].height = 28

    ws.merge_cells("A3:E3")
    ws["A3"] = (
        "「审查」列留空。填「同意」/「改：___」/「否」即可；"
        "要改只改「触发条件」那一格。黄色是这次新赛程带出来的岔路，先拍板。"
    )
    ws["A3"].font = NOTE_FONT
    ws["A3"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[3].height = 20

    headers = ["项", "触发条件（我的推荐）", "依据（代码事实 / 数值）", "我的问题", "审查"]
    for idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=idx, value=header)
        style_cell(cell, font=HEAD_FONT, fill=HEAD_FILL, align=CENTER)
    ws.row_dimensions[4].height = 28

    heights = [96, 124, 112, 104, 88, 112, 76, 92]
    for i, row in enumerate(ROWS):
        r = 5 + i
        question = row["question"].replace(chr(92) + "n", chr(10))
        values = [row["honor"], row["trigger"], row["basis"], question, ""]
        for idx, value in enumerate(values, start=1):
            cell = ws.cell(row=r, column=idx, value=value)
            if idx == 1:
                style_cell(cell, font=HONOR_FONT, fill=GREY_FILL if i % 2 else None, align=CENTER)
            elif idx == 5:
                style_cell(cell, fill=YELLOW_FILL, align=CENTER)
            else:
                style_cell(cell, fill=GREY_FILL if i % 2 else None)
        ws.row_dimensions[r].height = heights[i]

    ws.merge_cells("A14:E14")
    ws["A14"] = (
        "填法示例：同意　|　改：MSI 取消，只留 S 赛　|　否。"
        "Q1–Q8 在聊天里也会问一遍，表格和聊天选一个答就行。"
    )
    ws["A14"].font = NOTE_FONT
    ws["A14"].fill = YELLOW_FILL
    ws["A14"].alignment = Alignment(wrap_text=True, vertical="center", horizontal="left")
    ws["A14"].border = BORDER
    ws.row_dimensions[14].height = 32

    ws.freeze_panes = "A5"
    ws.print_area = "A1:E14"
    ws.print_title_rows = "1:4"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def build_schedule_sheet(ws):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "8EA9C1"

    widths = {"A": 10, "B": 10, "C": 56, "D": 56, "E": 38}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    ws.merge_cells("A1:E1")
    ws["A1"] = "赛程 · 你已确认的 24 周排法"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 34

    ws.merge_cells("A2:E2")
    ws["A2"] = (
        "第 2–24 周单循环，场次 = 队数−1；第 25 周联赛决赛；"
        "第 26 周无比赛；第 27 周小组赛 / 28 八强 / 29 四强 / 30 决赛；第 1 周空着。"
        "「MSI」列已定不办，联赛周次直接用「原排法」。"
    )
    ws["A2"].font = SUB_FONT
    ws["A2"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[2].height = 28

    headers = ["队数", "场次", "原排法（你已确认）", "MSI（已定不办）", "说明"]
    for idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=idx, value=header)
        style_cell(cell, font=HEAD_FONT, fill=HEAD_FILL, align=CENTER)
    ws.row_dimensions[4].height = 28

    for i, (teams, matches, original, with_msi, note) in enumerate(SCHEDULE):
        r = 5 + i
        for idx, value in enumerate([teams, matches, original, with_msi, note], start=1):
            cell = ws.cell(row=r, column=idx, value=value)
            if idx in (1, 2):
                style_cell(cell, fill=GREY_FILL if i % 2 else None, align=CENTER)
            else:
                style_cell(cell, fill=GREY_FILL if i % 2 else None)
        ws.row_dimensions[r].height = 58

    ws.merge_cells("A9:E9")
    ws["A9"] = (
        "你已定不办 MSI：联赛周次直接用「原排法」；"
        "原「第 13 周 MSI / 挪到第 12 周」方案作废。"
    )
    ws["A9"].font = NOTE_FONT
    ws["A9"].fill = YELLOW_FILL
    ws["A9"].alignment = Alignment(wrap_text=True, vertical="center", horizontal="left")
    ws["A9"].border = BORDER
    ws.row_dimensions[9].height = 34

    ws.merge_cells("A10:E10")
    ws["A10"] = (
        "S 赛：第 26 周无比赛 · 第 27 周小组赛 · 第 28 周八强 · "
        "第 29 周四强 · 第 30 周决赛。资格拟 LPL 前 4；"
        "小组赛自动模拟，八强/四强/决赛可打（待 Q3）。"
    )
    ws["A10"].font = NOTE_FONT
    ws["A10"].fill = YELLOW_FILL
    ws["A10"].alignment = Alignment(wrap_text=True, vertical="center", horizontal="left")
    ws["A10"].border = BORDER
    ws.row_dimensions[10].height = 36

    ws.freeze_panes = "A5"
    ws.print_area = "A1:E10"
    ws.print_title_rows = "1:4"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def build_facts_sheet(ws):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "B7C7D6"

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 82
    ws.column_dimensions["C"].width = 46

    ws.merge_cells("A1:C1")
    ws["A1"] = "数据依据 · 这些数字是怎么来的"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 34

    ws.merge_cells("A2:C2")
    ws["A2"] = (
        "只列本表用到的口径。代码行号对应当前 HEAD；"
        "名单分位是把 src/data/rosters.ts 里 655 个 ovr 排序后取的。"
    )
    ws["A2"].font = SUB_FONT
    ws["A2"].alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[2].height = 22

    headers = ["项", "数值 / 事实", "出处"]
    for idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=idx, value=header)
        style_cell(cell, font=HEAD_FONT, fill=HEAD_FILL, align=CENTER)
    ws.row_dimensions[4].height = 28

    for i, (item, fact, source) in enumerate(FACTS):
        r = 5 + i
        for idx, value in enumerate([item, fact, source], start=1):
            cell = ws.cell(row=r, column=idx, value=value)
            if idx == 1:
                style_cell(cell, font=Font(name="Microsoft YaHei", size=9, bold=True, color=NAVY),
                           fill=GREY_FILL if i % 2 else None)
            else:
                style_cell(cell, fill=GREY_FILL if i % 2 else None)
        ws.row_dimensions[r].height = 34 if len(fact) < 40 else 48

    ws.freeze_panes = "A5"
    ws.print_area = f"A1:C{4 + len(FACTS)}"
    ws.print_title_rows = "1:4"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def main():
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "待审表"
    build_review_sheet(ws1)

    ws2 = wb.create_sheet("赛程")
    build_schedule_sheet(ws2)

    ws3 = wb.create_sheet("数据依据")
    build_facts_sheet(ws3)

    wb.save(OUT)
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
