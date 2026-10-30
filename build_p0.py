# -*- coding: utf-8 -*-
"""生成《P0 与核心循环结构》DOCX：两张图 + 定稿草案。"""
import os
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "charts")
os.makedirs(CH, exist_ok=True)
OUT = os.path.join(HERE, "P0-与核心循环结构.docx")

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_B = "C:/Windows/Fonts/msyhbd.ttc"
INK, GRAY, MUTED = "#1b1b1b", "#5b6674", "#8b95a3"
NAVY, BLUE, TEAL = "#1f3a5f", "#2f6fa8", "#2e8b7e"
WARM, GREEN, RED = "#c07a2e", "#5b8c5a", "#b04a4a"


def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def text(d, xy, s, size=22, bold=False, fill=INK, anchor="mm", spacing=8):
    d.multiline_text(xy, s, font=f(size, bold), fill=fill, anchor=anchor,
                     align="center", spacing=spacing)


def arrow(d, p1, p2, color=BLUE, width=4, head=14):
    import math
    (x1, y1), (x2, y2) = p1, p2
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    d.line([(x1, y1), (bx, by)], fill=color, width=width)
    d.polygon([(x2, y2),
               (x2 - head * 1.8 * math.cos(a - 0.42), y2 - head * 1.8 * math.sin(a - 0.42)),
               (x2 - head * 1.8 * math.cos(a + 0.42), y2 - head * 1.8 * math.sin(a + 0.42))],
              fill=color)


def box(d, x, y, w, h, title, sub="", fill="#eef3f8", edge=NAVY, tsize=24, ssize=17):
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=fill, outline=edge, width=3)
    if sub:
        text(d, (x + w / 2, y + h * 0.36), title, tsize, True, NAVY)
        text(d, (x + w / 2, y + h * 0.70), sub, ssize, False, GRAY)
    else:
        text(d, (x + w / 2, y + h / 2), title, tsize, True, NAVY)


def fig_loop():
    W, H = 1600, 880
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    y, h = 210, 150
    xs = [60, 390, 720, 1050]
    w = 260
    box(d, xs[0], y, w, h, "事件触发", "剧情 + 局势（写死）")
    box(d, xs[1], y, w, h, "玩家选择", "2–3 个选项", fill="#e8f2ec", edge=TEAL)
    box(d, xs[2], y, w, h, "结算", "数值 × 可见概率")
    box(d, xs[3], y, w, h, "后果", "数值 / 名声 / 后续", fill="#f7efe4", edge=WARM)
    for i in range(3):
        arrow(d, (xs[i] + w + 6, y + h / 2), (xs[i + 1] - 8, y + h / 2))

    # 大事件支线
    bx, by, bw, bh = 700, 530, 340, 120
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill="#fbf1ea",
                        outline=RED, width=3)
    text(d, (bx + bw / 2, by + bh * 0.36), "大事件：后续事件", 20, True, RED)
    text(d, (bx + bw / 2, by + bh * 0.72), "后果带进下一段，重奖重罚", 16, False, GRAY)
    arrow(d, (xs[3] + 40, y + h + 6), (bx + bw + 4, by + bh / 2 - 20), RED, 3)
    text(d, (bx + bw + 70, by + 8), "有分支", 17, False, RED)

    # 回流
    ly = 770
    cx3, cx0 = xs[3] + w / 2 + 60, xs[0] + w / 2
    d.line([(cx3, y + h + 20), (cx3, ly)], fill=BLUE, width=3)
    d.line([(cx3, ly), (cx0, ly)], fill=BLUE, width=3)
    arrow(d, (cx0, ly), (cx0, y + h + 12), BLUE, 3)
    text(d, (W / 2 + 40, ly + 36), "一个事件结束 → 下一个事件，直到赛季节点或退役", 18, False, MUTED)
    text(d, (W / 2, 120), "一条事件链：文本负责梗，骰子只决定成败，不决定好不好笑", 20, False, GRAY)
    d.rectangle([xs[2] - 2, y - 2, xs[2] + w + 2, y + h + 2], outline=GREEN, width=3)
    text(d, (xs[2] + w / 2, y - 34), "唯一用骰子的地方", 17, True, GREEN)
    im.save(os.path.join(CH, "p0-loop.png"))


def fig_stats():
    W, H = 1600, 740
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    text(d, (W / 2, 60), "六维只分两处用：五个进比赛，一个管场外——场外再绕回来", 21, False, GRAY)

    stats = ["操作", "对线", "团战", "意识", "心态"]
    sx, sw, sh = 70, 170, 64
    ys = [120, 190, 260, 330, 400]
    for s, y in zip(stats, ys):
        box(d, sx, y, sw, sh, s, "", "#eef3f8", NAVY, 23)
    d.line([(250, 152), (250, 432)], fill="#9dbbd4", width=3)
    for y in ys:
        d.line([(sx + sw + 4, y + sh / 2), (250, y + sh / 2)], fill="#9dbbd4", width=3)
    arrow(d, (250, 292), (694, 292), BLUE, 4)

    box(d, 700, 217, 300, 150, "比赛事件结算", "读 1–2 个数值 × 可见概率", "#e8f2ec", TEAL, 22, 15)
    box(d, 1080, 217, 290, 150, "后果", "数值 / 名声 / 后续", "#f7efe4", WARM, 22, 16)
    arrow(d, (1006, 292), (1074, 292), BLUE, 4)

    # 场外链（右 → 左）
    ry, rh = 545, 110
    box(d, 1080, ry, 280, rh, "人气", "只在场外生效", "#fdf1e4", WARM, 22, 15)
    box(d, 760, ry, 260, rh, "赞助", "", "#fdf1e4", WARM, 22)
    box(d, 460, ry, 240, rh, "钱", "", "#fdf1e4", WARM, 22)
    box(d, 70, ry, 300, rh, "资源", "训练次数 / 陪练 / 队伍", "#fdf1e4", WARM, 22, 15)
    for a, b in ((1074, 1026), (754, 706), (454, 376)):
        arrow(d, (a, ry + rh / 2), (b, ry + rh / 2), WARM, 3)
    arrow(d, (1225, 373), (1225, ry - 8), WARM, 3)
    text(d, (1262, 450), "曝光", 16, True, WARM)

    # 训练回流
    arrow(d, (220, ry - 8), (220, 470), WARM, 4)
    text(d, (252, 500), "训练", 17, True, WARM)
    im.save(os.path.join(CH, "p0-stats.png"))


# ------------------------------------------------------------------ docx
CN = "微软雅黑"
N = RGBColor(0x1F, 0x3A, 0x5F)
B = RGBColor(0x2F, 0x6F, 0xA8)
T = RGBColor(0x2E, 0x8B, 0x7E)
G = RGBColor(0x5B, 0x66, 0x74)
M = RGBColor(0x8B, 0x95, 0xA3)
K = RGBColor(0x1B, 0x1B, 0x1B)
WH = RGBColor(0xFF, 0xFF, 0xFF)


def set_run(r, size=10.5, bold=False, color=None):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = CN
    if color is not None:
        r.font.color.rgb = color
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia"):
        rf.set(qn(a), CN)
    return r


def rich(p, s, size=10.5, color=K):
    for i, part in enumerate(s.split("**")):
        if part:
            set_run(p.add_run(part), size, i % 2 == 1, color)


def para(doc, s="", size=10.5, bullet=False, color=K, after=6, before=0,
         indent=True, keep=False):
    p = doc.add_paragraph(style="List Bullet" if bullet else None)
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.45
    if keep:
        pf.keep_with_next = True
    if indent and not bullet:
        pf.first_line_indent = Pt(size * 2)
    if s:
        rich(p, s, size, color)
    return p


def border(p, color="C9D6E3", sz=6):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz))
    e.set(qn("w:space"), "4"); e.set(qn("w:color"), color)
    b.append(e); pPr.append(b)


def h1(doc, num, s):
    p = doc.add_heading(level=1)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(num + "　"), 16, True, T)
    set_run(p.add_run(s), 16, True, N)
    border(p)
    return p


def h2(doc, s):
    p = doc.add_heading(level=2)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(s), 12, True, B)


def shade(c, v):
    tcPr = c._tc.get_or_add_tcPr()
    e = OxmlElement("w:shd")
    e.set(qn("w:val"), "clear"); e.set(qn("w:color"), "auto"); e.set(qn("w:fill"), v)
    tcPr.append(e)


def table(doc, head, rows, widths, size=9, caption=None, keep=True):
    t = doc.add_table(rows=1, cols=len(head))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    bd = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{tag}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6")
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "CDD8E3")
        bd.append(e)
    tblPr.append(bd)
    mar = OxmlElement("w:tblCellMar")
    for tag, v in (("top", 50), ("left", 100), ("bottom", 50), ("right", 100)):
        e = OxmlElement(f"w:{tag}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)

    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))
    trPr.append(OxmlElement("w:cantSplit"))
    for i, s in enumerate(head):
        c = hdr.cells[i]
        c.width = Cm(widths[i])
        shade(c, "1F3A5F")
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        set_run(p.add_run(s), size, True, WH)
    for ri, row in enumerate(rows):
        r = t.add_row()
        r._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for ci, s in enumerate(row):
            c = r.cells[ci]
            c.width = Cm(widths[ci])
            if ri % 2 == 1:
                shade(c, "F4F7FA")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.2
            rich(p, s, size)
            if ci == 0:
                for rr in p.runs:
                    rr.font.bold = True
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    if keep:
        for ri, r in enumerate(t.rows):
            if ri < len(t.rows) - 1:
                for c in r.cells:
                    for pp in c.paragraphs:
                        pp.paragraph_format.keep_with_next = True
    if caption:
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_before = Pt(4)
        c.paragraph_format.space_after = Pt(12)
        set_run(c.add_run(caption), 9, False, M)
    return t


def note(doc, s, spacer=True):
    t = doc.add_table(rows=1, cols=1)
    t.autofit = False
    t.columns[0].width = Cm(16.0)
    c = t.rows[0].cells[0]
    c.width = Cm(16.0)
    shade(c, "EEF4FA")
    tblPr = t._tbl.tblPr
    bd = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{tag}")
        e.set(qn("w:val"), "single" if tag == "left" else "nil")
        e.set(qn("w:sz"), "18" if tag == "left" else "0")
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "2F6FA8")
        bd.append(e)
    tblPr.append(bd)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.35
    rich(p, s, 9.5, RGBColor(0x33, 0x3B, 0x45))
    if spacer:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figure(doc, name, cap, w):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(os.path.join(CH, name), width=Cm(w))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(12)
    set_run(c.add_run(cap), 9, False, M)


fig_loop()
fig_stats()

doc = Document()
st = doc.styles["Normal"]
st.font.name = CN
st.font.size = Pt(10.5)
st.font.color.rgb = K
st.element.rPr.rFonts.set(qn("w:eastAsia"), CN)

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.9)
sec.left_margin = sec.right_margin = Cm(2.5)

hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
set_run(hp.add_run("P0 与核心循环结构 · 定稿草案 v0.1"), 8.5, False, M)
border(hp, "DCE4EC", 4)

# ---------- 标题
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(6)
p.paragraph_format.space_after = Pt(2)
set_run(p.add_run("P0 与核心循环结构"), 24, True, N)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(10)
set_run(p.add_run("第一款作品的约束与事件模型　·　定稿草案 v0.1　·　2026-10-28"), 9.5, False, M)
border(p, "C9D6E3", 8)

para(doc, "本文件只记录**你已经定下**的东西。带【建议】的段落是我提的，你可以直接划掉；带【待定】的是你还没答的。", after=10)

# ---------- 一句话
h1(doc, "一", "一句话")
note(doc, "做一个 LPL 题材的职业生涯模拟小游戏：玩家 18 岁入行，用 8 年在事件里做选择，靠六维数值与可见概率决定成败；目标不是“打通关”，是让他看见熟悉的梗时**会心一笑**。")

# ---------- P0
h1(doc, "二", "P0 结论")
table(doc,
      ["项", "你定的"],
      [["玩家", "虎扑上关注 LPL 的观众、英雄联盟玩家"],
       ["单局", "一次坐下来玩完，1–1.5 小时"],
       ["投入", "每周 5 小时"],
       ["平台", "只发虎扑 AI 工坊（内测，需报名审核）"],
       ["中途退出", "存进度，下次接着玩"],
       ["为什么是你", "玩过《峡谷这一生》：题材做成了，但荣誉没有兴奋感、没有 LPL 梗文化。你知道缺口在哪。"],
       ["首版砍掉", "不做比赛系统——比赛以**事件**出现"],
       ["成功标准", "陌生人打开就能玩，且能在 1–1.5 小时内玩完一次"]],
      [3.0, 13.0], size=9,
      caption="表 1　P0 的五条约束与两条边界")

para(doc, "**首版是**：第一个能发给陌生人的完整版本——从头能玩到尾、没有阻断 bug、能发布。不含打磨，不含后来想加的第二个系统。", before=2)

# ---------- 事件模型
h1(doc, "三", "核心循环：事件模型")
para(doc, "整个游戏就是一条事件链。比赛不单独做系统，它以事件的形式出现。", keep=True)
figure(doc, "p0-loop.png", "图 1　事件链：文本负责梗，骰子只决定成败", 16.0)

table(doc,
      ["环节", "你定的规则"],
      [["事件", "文本场景 + 2–3 个选择。有大小之分。"],
       ["局势", "事件自带的环境变量，**写死**；不同事件局势不同。"],
       ["结果", "**可变**——选择不同，比赛结果不同。"],
       ["结算", "个人**数值 + 可见概率** → 成败。有些选择风险极高，数值高可以弥补。"],
       ["梗", "**无论输赢，文本都带梗。** 梗是呈现，不是奖品。"],
       ["小事件", "无后续，结算完直接进下一个。"],
       ["大事件", "选项有后续分支，结尾重奖重罚。"],
       ["频率", "大大小小穿插；目标每 5–8 分钟一次“会心一笑”。【建议】"]],
      [3.0, 13.0], size=9,
      caption="表 2　事件模型的七条规则")

para(doc, "**分支的后果（你定的）**：不同选项带来不同后果——**名声、伤病、教练信任、心态提升、比赛结果**。", before=2)
para(doc, "**首版不做关系系统。** 教练信任是一个会涨会跌的数值，不是“每个 NPC 单独的好感度”。这条界线要在写事件时就守住，否则会悄悄长成一个系统。")

h2(doc, "事件怎么被触发：标签 + 分桶 + 兜底")
para(doc, "40 个事件不按顺序播。触发靠三样东西——**阶段分桶**、**标签**、**前置标记**，再加一条**兜底**规则防止抽空。", keep=True)
for t in ["**分桶**：按成长期 / 巅峰期 / 衰退期分开，每桶数量不等。",
          "**标签**：每个事件挂 2–3 个（`#采访` `#下路` `#转会`）。条件写成“某标签的事件发生过”，比写数值表达式省事。",
          "**前置标记**：大事件必须有前置。例如“先在采访里选过某句”，否则它不该出现。",
          "**兜底**：过滤后为空，就退回“无条件池”抽一个。这一步不做，条件写复杂了必然卡死。"]:
    para(doc, t, bullet=True, after=2)

para(doc, "示例（我写的，用来说明结构，不是你的文案）：", before=4, keep=True)
table(doc,
      ["事件", "标签", "阶段", "触发条件"],
      [["赛后采访：记者问「下路被压得这么惨，你怎么看」", "#赛后 #采访 #下路", "成长期", "无（进无条件池）"],
       ["复盘：教练让你复看一波团战", "#训练 #中路", "成长期", "意识 ≥ 30"],
       ["转会期：有队伍私下接触你", "#转会 #大事件", "巅峰期", "名声 ≥ 40 且已触发过 #采访"]],
      [7.4, 4.2, 2.2, 4.2], size=8.5,
      caption="表 3　三个事件的条件写法：从左到右就是一条筛选链")
para(doc, "**一次抽取是这样走的**（第 3 年休赛期）：取当前桶 → 去掉已触发的 → 按条件过滤 → 在剩下的里随机抽 → 抽不出就落回无条件池。", before=2)
para(doc, "**标记的复用**：在采访里选了「甩锅队友」，就写入 `#甩锅`。之后转会事件可以读它（“有队伍听说你不太好带”），结局尾注也读它（“那年采访里的那句话，后来一直跟着你”）。同一个标记，驱动后续和写结局，**不用写两遍**。")

# ---------- 六维
h1(doc, "四", "六维与场外经济")
table(doc,
      ["维度", "用在哪", "怎么变"],
      [["操作 / 对线 / 团战 / 意识 / 心态", "比赛事件结算，每个事件只读其中一两个", "经历事件、训练；**心态**随年龄变好，也能练出来"],
       ["人气", "只在场外生效", "事件与曝光累积"]],
      [5.6, 5.4, 5.0], size=9,
      caption="表 4　六维：前五个决定比赛，第六个决定你能拿到什么资源")
figure(doc, "p0-stats.png", "图 2　六维分工：五个进比赛，一个管场外，场外再绕回来", 15.0)

para(doc, "**场外链**：人气 → 赞助 → 钱 → 资源（训练次数、陪练、更好的队伍）。这条链让“刷人气”有回报，也让钱变成能权衡的东西。", before=2)
para(doc, "**钱买不到什么（你定的）**：买不到**比赛胜利**，也买不到**六维数值**。资源分两类——**年度刷新**（每年一次）与**一次性**（更好的队、更好的训练环境，例如提升六维成长速率）。一次性资源给的是**条件**，不是**上限**。")
para(doc, "一个自然结果（不是漏洞）：**成长速率是复利**，越早买越值，玩家会倾向攒钱早买。这是设计造成的，不是玩家钻空子。", color=G)
para(doc, "**一次性资源（定三种）**：每一种必须挂在一个已经有系统上，挂不上的就不做——所以「私人教练 / 分析师」被砍掉了，它会带出“持续付费”这个新系统。", before=2)
table(doc,
      ["候选", "给什么条件", "代价"],
      [["更好的住处", "非比赛期恢复更快（心态回升速度 +）", "心态"],
       ["更好的外设", "训练效率小幅提升（成长速率 +）", "成长速率"],
       ["康复与医疗", "伤病恢复更快、复发率更低", "伤病"]],
      [4.4, 8.0, 3.6], size=9,
      caption="表 5　一次性资源定三种：每种都挂在一个已存在的系统上，不新增系统")
para(doc, "一个提醒：只剩三种一次性资源，钱的去处就偏少——**主要去处得靠年度刷新资源**（训练次数、陪练、队医）。年度刷新那边至少要有三档，否则攒钱会变成死钱。", color=G)

# ---------- 时间
h1(doc, "五", "时间与结局")
para(doc, "初始 18 岁；生涯 8 年，但不固定——玩家可以随时退役，进入结局演算。")
para(doc, "这条要求写事件之前就定死：**结局演算必须能吃任意状态**。第 2 年、数值很低的局面也要能生成一个说得通的结局，不能事后补。")
para(doc, "**生涯三阶段（你定的）**：成长期 → 巅峰期 → 衰退期，**先上后下**。世界赛一年一次，8 年就是 8 次机会。")
para(doc, "**衰退掉哪几维（你定的）**：对线、操作、团战、意识四项随年龄下滑；**人气与心态不受影响**。")

h2(doc, "结局演算：模板 + 变量")
para(doc, "结局由两层组成，**模板是大头**：", after=2)
table(doc,
      ["层", "由什么决定", "给玩家什么"],
      [["主结局（模板）", "**六维 + 荣誉**（你定的）", "一段完整的“你的生涯是什么”"],
       ["事件尾注（小字）", "你触发过的事件", "“当年那个选择，让你变成了什么样”"]],
      [4.2, 6.4, 5.4], size=9,
      caption="表 6　结局的两层：模板负责体量，尾注负责“这一局是我”")
para(doc, "这条对实现有一个硬要求：**每个事件要带一个标记**（是否触发过）。结局读这些标记来生成尾注——现在不预留，后期补不上。", before=2)

# ---------- 内容量
h1(doc, "六", "内容量级（估算）")
para(doc, "**总数定在 40 个（你定的）**。注意这 40 个是**事件池**，不是一局能看到的量：")
para(doc, "按每 4 分钟一个事件、单局 1.5 小时算，一局大约走 **22–25 个**。剩下的十几个，取决于**随机**和你设的**触发条件**——每年塞几个事件，由这两件事决定，不是一个固定的数字。")
para(doc, "由此推出一件事：**40 个事件约等于 1.5 局的量。** 重玩价值全在池子里；测玩时要跑不止一局，否则会误判“内容太少”。两个数字都是【估计】，没有一手来源——它们只说明一件事：你每周 5 小时，主要会花在写这 40 段文本上。")

# ---------- 风险
h1(doc, "七", "已知风险（我的判断）")
for s in ["**梗有保质期。** 结构性梗（四保一、下路双人组、世界赛魔咒）比绑定具体选手的梗耐久；后者还牵涉 IP。",
          "**钱是唯一的中介。** 人气 → 赞助 → 钱 → 资源是一条单链，中间没有分叉。玩家迟早会发现“只要搞钱就行”，其余维度变成装饰。",
          "**数值分散导致成长感弱。** 六维里五维都能涨，单维在 40 个事件里只有十来次提升机会——这正是你批评《峡谷这一生》“提升太慢”的机制成因。",
          "**衰退要找得到体感。** 玩家得知道自己什么时候从巅峰开始下坡，否则衰退只是背地里扣数，感觉像被针对。",
          "**演出成本。** 梗若要靠镜头和动画呈现，产能会被吃掉；建议限制在文本 + 音效 + 节奏停顿。"]:
    para(doc, s, bullet=True, after=3)

# ---------- 待定
doc.add_paragraph().paragraph_format.space_after = Pt(0)
note(doc, "**下一步不是继续设计，是写 3 个事件**：一个带后续分支的大事件、两个小事件。写完拿给我，我只验两件事——**选项是否真的有分歧**、**梗有没有落在呈现上而不是结果上**。", spacer=False)

doc.save(OUT)
print("saved:", OUT)
