# -*- coding: utf-8 -*-
"""核对 80 条事件的触发条件：表/设计要求 vs 代码 requires。只读导出。"""
import re
import io
import subprocess
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

KIND = {"match": "比赛", "life": "生活", "special": "特殊"}
PHASE = {"growth": "成长", "peak": "巅峰", "decline": "衰退", "any": "任意"}


def blocks_text(s):
    out = {}
    for b in re.split(r"\n  \{\n    id: '", s)[1:]:
        eid = b.split("'", 1)[0]
        out[eid] = b
    return out


def field(b, name):
    m = re.search(rf"{name}: (.*),\n", b)
    return m.group(1) if m else ""


cur = blocks_text(io.open("src/data/events.ts", encoding="utf-8").read())  # 现代码 34 条
old80 = blocks_text(subprocess.check_output(
    ["git", "show", "bbede8e:src/data/events.ts"], encoding="utf-8"))  # 80 条版本

table = {}
for f in ["P1-事件库-梗驱动-初审.xlsx", "P1-事件库-人物梗-初审.xlsx"]:
    ws = load_workbook(f, data_only=True)["事件"]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0]:
            table[r[0]] = {"kind": r[1], "phase": r[2], "cond": r[3]}

NEW = {f"M{i:02d}" for i in range(10, 26)} | {f"L{i:02d}" for i in range(11, 33)} | {f"S{i:02d}" for i in range(4, 12)}

# 46 条新写的身份门槛判断（正文语境）
SIGNED = {"L12", "L13", "L14", "L17", "L18", "L19", "L20", "L21", "L22",
          "L23", "L24", "L25", "L26", "L27", "L28",
          "S05", "S07", "S08", "S09", "S10"}


def code_tokens(eid, b):
    r = field(b, "requires")
    kind = re.search(r"kind: '(\w+)'", b).group(1)
    t = set()
    if kind == "match" or "matchWeeksPerYear" in r:
        t.add("比赛周")
    if "!s.signed" in r:
        t.add("未签约")
    elif "s.signed" in r:
        t.add("已签约")
    for n in (30, 50):
        if f"coachTrust <= {n}" in r:
            t.add(f"教练信任≤{n}")
    for n in (50, 60):
        if f"popularity >= {n}" in r:
            t.add(f"人气≥{n}")
    for n in range(1, 9):
        if f"year === {n}" in r:
            t.add(f"第{n}年")
    for f in re.findall(r"flags\.includes\('#([^']+)'\)", r):
        t.add(f"标记#{f}")
    if "once: true" in b:
        t.add("一次")
    if re.search(r"weight: [12],", b):
        t.add("低权重")
    return t


def table_tokens(cond):
    t = set()
    if "比赛周" in cond:
        t.add("比赛周")
    if "未签约" in cond:
        t.add("未签约")
    if "已签约" in cond:
        t.add("已签约")
    for n in re.findall(r"教练信任 ≤ (\d+)", cond):
        t.add(f"教练信任≤{n}")
    for n in re.findall(r"人气 ≥ (\d+)", cond):
        t.add(f"人气≥{n}")
    for n in re.findall(r"第 (\d) 年", cond):
        t.add(f"第{n}年")
    for f in re.findall(r"已发生 #([^\s·]+)", cond):
        t.add(f"标记#{f}")
    if "标记#五十块到账" in t:
        t.discard("标记#五十块到账")
        t.add("标记#五十块")
    if "替补中" in cond:
        t.add("替补中")
    if "时刻" in cond:
        t.add("时刻")
    if "低概率" in cond:
        t.add("低权重")
    if "人气过中位" in cond:
        t.discard("标记#人气过中位")
        t.add("人气≥50")
    return t


rows = []
for eid in sorted(set(cur) | set(old80)):
    if eid in ("F01", "F02"):
        continue
    was80 = eid in old80 and eid in NEW
    b = cur.get(eid) or old80[eid]
    kind = re.search(r"kind: '(\w+)'", b).group(1)
    phase = re.search(r"phase: '(\w+)'", b).group(1)
    req = field(b, "requires") or "—"
    if eid in table:
        want = table_tokens(table[eid]["cond"])
        src = table[eid]["cond"]
        have = code_tokens(eid, b)
        missing = want - have
        extra = {x for x in have - want if x not in ("一次", "比赛周")}
        note = ""
        if eid in ("S01", "P08", "P12"):
            note = "表里是「时刻」，代码只按年随机；不会自动在固定周触发"
        if eid == "L03":
            note = "表要求「已发生 #本周赢过」：该标记不存在，且比赛在抽事件之后才结算，抽的时候不可能知道输赢"
        if eid == "L01":
            note = "表要求「已发生 #收到试训邀请」：代码里没有这个标记，也查不到谁设置它"
        if eid in ("L05", "M04"):
            note = "「替补中」没实现；M04 用「曾经替补过」(#坐过替补) 代替「现在在替补席」"
        judge = "不一致" if missing else ("一致" if not note else "部分一致")
        rows.append([eid, KIND[kind], PHASE[phase], src, req, judge, "；".join(sorted(missing)) or "—", note])
    elif eid.startswith("E"):
        continue
    else:
        # 46 条新写：没有表，按正文语境判断
        src = "—（新写，无表）"
        want = "已签约" if eid in SIGNED else ""
        missing = {"已签约"} - code_tokens(eid, b) if want else set()
        judge = "缺身份门槛" if missing else ("有门槛" if want else "不限身份")
        note = ""
        if eid.startswith("M"):
            judge = "缺身份门槛（比赛类通病）"
            note = "比赛事件只在比赛周抽，但没要求已签约；路人期第 1 年也能抽到职业赛画面"
        if eid == "M05":
            note = "已签约 · 本周排了直播（actionGrid 含 stream）；24 局模拟没排过直播，所以 0 次，不是死条件"
        if eid == "S03":
            note = "第 1 年 + 已签约 + 比赛周：24 局模拟 0 次，几乎不可达"
        rows.append([eid, KIND[kind], PHASE[phase], src, req, judge, "；".join(sorted(missing)) or "—", note])

wb = Workbook()
ws = wb.active
ws.title = "核对"
head = ["ID", "类型", "阶段", "触发条件（表/设计）", "代码 requires", "判定", "缺什么", "说明"]
ws.append(head)
for c in range(1, len(head) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = PatternFill("solid", fgColor="1F3864")
    cell.font = Font(color="FFFFFF", bold=True)
for w, i in zip([7, 7, 7, 34, 46, 18, 22, 58], range(1, 9)):
    ws.column_dimensions[get_column_letter(i)].width = w
for r in rows:
    ws.append(r)
ws.freeze_panes = "A2"
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.alignment = Alignment(vertical="top", wrap_text=True)

ws2 = wb.create_sheet("结论")
concl = [
    ("查的是什么", "80 条事件的触发条件（requires）与初审表「触发条件」列、以及正文语境对不对得上。代码现在 34 条，46 条在 bbede8e 里、内容同一份。"),
    ("1. 比赛类 30 条", "E01、M01–M25、P01/P02/P07/P10/P11 都只在比赛周抽（抽取逻辑自带），但全都没有「已签约」门槛：路人期第 1 年也能抽到职业赛画面。这是历史结构问题，不是这次新写带来的。"),
    ("2. 初审表没照搬的 4 条", "L01 要 #收到试训邀请、L03 要 #本周赢过——两个标记代码里根本不存在；L05 要「替补中」、M04 要「替补中」，代码用的是 #坐过替补（曾经替补，不是现在）。"),
    ("3. 3 条「时刻」事件", "S01/P08/P12 表里写「时刻」，代码只按年随机，不会在固定周触发。"),
    ("4. 实测触发不到", "S03（第 1 年·已签约·比赛周）24 局 0 次，几乎不可达；M05（本周排直播）0 次是因为模拟从不排直播，真人能触发。"),
    ("5. 46 条新写缺门槛", "17 条生活/特殊事件没写「已签约」：L12 L14 L17 L18 L19 L21 L22 L23 L24 L25 L26 L28 S05 S07 S08 S09 S10。30 条比赛事件同样没有这道门槛，其中 M10–M25 是新写的 16 条。"),
    ("结论", "不是漏了几个 requires，是三块系统缺口：身份门槛（比赛/生活）、标记不存在（#收到试训邀请、#本周赢过）、时刻没实现。改法要你定：只补 34 条 / 连 46 条一起补 / 在抽取逻辑里统一加「比赛事件必须已签约」。"),
    ("复跑", "本表由 scripts/06-events/check_triggers.py 生成；80 条取自 `git show bbede8e:src/data/events.ts`。"),
]
for i, (k, v) in enumerate(concl, 1):
    ws2.cell(row=i, column=1, value=k).font = Font(bold=True)
    ws2.cell(row=i, column=2, value=v).alignment = Alignment(wrap_text=True, vertical="top")
ws2.column_dimensions["A"].width = 22
ws2.column_dimensions["B"].width = 110

wb.save("P1-事件库-触发条件核对.xlsx")
print("rows", len(rows), "mismatch", sum(1 for r in rows if r[5] not in ("一致",)))
