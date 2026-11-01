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


def fig_week():
    W, H = 1600, 720
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    text(d, (W / 2, 54), "一周 = 三格行动 + 一个事件 + 一场比赛", 21, False, GRAY)

    ys = [150, 250, 350]
    for y, t in zip(ys, ["行动点 1", "行动点 2", "行动点 3"]):
        box(d, 90, y, 250, 86, t, "消耗体力", "#eef3f8", NAVY, 22, 14)
    arrow(d, (346, 293), (474, 293), BLUE, 4)
    text(d, (410, 262), "三格都由你安排", 15, False, MUTED)

    box(d, 480, 228, 270, 130, "抽一个事件", "随机 + 触发条件", "#e8f2ec", TEAL, 21, 14)
    arrow(d, (754, 293), (810, 293), BLUE, 4)
    box(d, 815, 228, 240, 130, "比赛事件", "有比赛的周", "#f7efe4", WARM, 21, 14)
    arrow(d, (1059, 293), (1112, 293), BLUE, 4)
    box(d, 1118, 228, 250, 130, "结周", "存档点", "#eef3f8", NAVY, 21, 14)

    d.rectangle([476, 224, 1063, 362], outline=GREEN, width=3)
    text(d, (770, 196), "内容都在这两格", 17, True, GREEN)

    d.line([(1243, 362), (1243, 630)], fill=BLUE, width=3)
    d.line([(1243, 630), (60, 630)], fill=BLUE, width=3)
    d.line([(60, 630), (60, 193)], fill=BLUE, width=3)
    arrow(d, (60, 193), (84, 193), BLUE, 3)

    text(d, (410, 470), "体力不够的那一格，只能排「休息」", 17, False, WARM, anchor="lm")
    text(d, (W / 2, 668), "结周即存档；下一周重新算体力，回到第一步", 18, False, MUTED)
    im.save(os.path.join(CH, "p0-week.png"))


fig_week()
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
set_run(hp.add_run("P0 与核心循环结构 · 定稿草案 v0.7"), 8.5, False, M)
border(hp, "DCE4EC", 4)


# ---------- 标题
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(6)
p.paragraph_format.space_after = Pt(2)
set_run(p.add_run("P0 与核心循环结构"), 24, True, N)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(10)
set_run(p.add_run("第一款作品的约束、周循环与事件模型　·　v0.7　·　2026-10-30"), 9.5, False, M)
border(p, "C9D6E3", 8)

para(doc, "本文件记录**你定下的东西**。带【建议】的是我提的，可以划掉；带「待测」的是你把数值留给测试，现在只定顺序。", after=10)

# ---------- 一
h1(doc, "一", "一句话")
note(doc, "做一个 LPL 题材的职业生涯模拟小游戏：18 岁入行，208 个比赛周，每周三个行动加一个事件，靠六维与可见概率走到结局。目标不是「通关」，是玩家看见熟悉的梗时**会心一笑**。")

# ---------- 二
h1(doc, "二", "P0 结论")
table(doc,
      ["项", "你定的"],
      [["玩家", "虎扑上关注 LPL 的观众、英雄联盟玩家"],
       ["单局", "一次坐下来玩完，1–1.5 小时为宜"],
       ["投入", "每周 5 小时"],
       ["平台", "只发虎扑 AI 工坊（纯前端网页，内测，需报名）"],
       ["存档", "每个比赛周结束存一次；**没有读档**"],
       ["为什么是你", "玩过《峡谷一生》：题材做成了，但荣誉没有兴奋感、没有 LPL 梗文化"],
       ["首版砍掉", "不做可玩的比赛系统——比赛以**事件**出现"],
       ["成功标准", "陌生人打开就能玩，1–1.5 小时内能走到一个结局"]],
      [3.0, 13.0], size=9,
      caption="表 1　P0 的约束与边界")

para(doc, "**首版是**：第一个能发给陌生人的完整版本——从头能玩到尾、没有阻断 bug、能发布。不含打磨，不含后来想加的第二个系统。", before=2)

# ---------- 三
h1(doc, "三", "一周怎么过")
para(doc, "每周固定三格行动，抽一个事件，有比赛就打一场，然后结周存档。", keep=True)
figure(doc, "p0-week.png", "图 1　周循环：内容只在「抽事件」和「比赛」这两格里", 15.6)

h2(doc, "八种行动")
table(doc,
      ["行动", "效果", "消耗", "解锁"],
      [["上分", "操作 · 对线 · 团战 · 意识 ↑", "体力", "路人期主力"],
       ["专项训练", "指定一项 ↑（比上分集中）", "体力", "限对线 / 团战 / 意识 / 操作"],
       ["复盘录像", "意识 ↑", "体力", "—"],
       ["训练赛", "团战 · 意识 ↑", "体力", "签约后"],
       ["健身", "体力上限 / 恢复速度 ↑", "体力", "—"],
       ["直播", "金钱 ↑ · 人气 ↑", "体力", "路人期主要名气来源"],
       ["商业活动", "金钱 ↑↑ · 人气 ↑", "体力（更多）", "签约后"],
       ["休息", "恢复体力", "—", "唯一的恢复手段"]],
      [3.2, 7.0, 2.4, 3.4], size=9,
      caption="表 2　八个行动：三格里排什么，就是你的策略")

h2(doc, "体力规则")
for t in ["每个行动点都要花体力；**体力不够支付三格，就不能结周**，只能把某一格改成休息。",
          "上限靠健身提升；恢复主要靠休息。**具体数值全部待测**，现在只定「先耗后补」这个顺序。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 四
h1(doc, "四", "事件")
para(doc, "事件分三类，比例按「比赛最多、生活其次、特殊最少」排。", keep=True)
table(doc,
      ["类别", "多久一次", "写什么", "怎么出现"],
      [["比赛事件", "最高（有比赛的周）", "一场比赛的选项，影响胜负", "每周抽"],
       ["生活事件", "次之", "训练、采访、转会、队内摩擦", "按条件抽"],
       ["特殊事件", "最低（一年一两次）", "写死年份或条件的一次性剧情", "写死，不进随机池"]],
      [3.0, 4.4, 5.4, 3.2], size=9,
      caption="表 3　三类事件：特殊事件与大事件是两个维度，别混")

para(doc, "**特殊事件 ≠ 大事件。** 特殊事件是「只出现一次」，大事件是「有分支、重奖重罚」。两者可以重叠，但要分开记，否则以后分不清是稀有还是重后果。", before=2)

h2(doc, "一个事件长什么样")
figure(doc, "p0-loop.png", "图 2　事件链：文本负责梗，骰子只决定成败", 15.4)
table(doc,
      ["环节", "你定的规则"],
      [["篇幅", "**50 字左右，绝对不能长**"],
       ["结构", "文本场景 + 2–3 个选择；允许开头一句无选择的铺垫"],
       ["局势", "事件自带的环境变量，写死；不同事件局势不同"],
       ["结果", "**可变**——选择不同，比赛结果不同"],
       ["结算", "个人数值 + **可见概率** → 成败；数值高能弥补高风险"],
       ["梗", "无论输赢，文本都带梗；但主战场已经移到反馈池（见第五章）"],
       ["大小", "小事件无后续；大事件有分支，结尾重奖重罚"],
       ["后果", "只能落在状态表的一格，或写一个标记"],
       ["必成 / 必败", "选项不强制掷骰：可以必成，也可以必败"],
       ["跨类", "一个事件可以同时是特殊事件和比赛事件（例如「第 3 年那场决赛」）"],
       ["临时值", "属性可以「临时 ±」：**只在本场比赛内有效，结算后清零，不进存档**"]],
      [3.0, 13.0], size=9,
      caption="表 4　事件的十一条规则")

h2(doc, "事件怎么被触发")
for t in ["**分桶**：按成长期 / 巅峰期 / 衰退期分开，每桶数量不等。",
          "**标签**：每个事件挂 2–3 个（`#采访` `#下路` `#转会`），条件写成「某标签的事件发生过」。",
          "**前置标记**：大事件必须有前置，否则它不该出现。",
          "**兜底**：过滤后为空，先落回「无条件填充池」抽一条；连它也没有，这周就不抽，直接走三格行动 + 比赛。"]:
    para(doc, t, bullet=True, after=2)

para(doc, "示例（我写的，用来说明结构，不是你的文案）：", before=4, keep=True)
table(doc,
      ["事件", "标签", "阶段", "触发条件"],
      [["赛后采访：记者问「下路被压得这么惨，你怎么看」", "#赛后 #采访 #下路", "成长期", "无（进无条件池）"],
       ["复盘：教练让你复看一波团战", "#训练 #中路", "成长期", "意识 ≥ 中位"],
       ["转会期：有队伍私下接触你", "#转会 #大事件", "巅峰期", "人气 ≥ 中位 且已触发过 #采访"]],
      [7.4, 4.2, 2.2, 4.2], size=8.5,
      caption="表 5　条件写法：从左到右就是一条筛选链（阈值先写「中位」，数值待测）")
para(doc, "**一次抽取**：取当前桶 → 去掉已触发的 → 按条件过滤 → 在剩下的里随机抽 → 抽不出就落回无条件池。", before=2)

para(doc, "**权重（你定的）**：特殊 : 常规 = **1 : 10**。但出现率不是一个数，它由条数稀释：")
para(doc, "特殊出现率 ≈ S ÷ (10C + S)　（S = 特殊条数，C = 常规条数）", color=G)
para(doc, "所以常规条数翻倍，特殊就稀一倍。**实际频率等事件总数定了再算**，现在不拍。倍率没有可查的行业惯例，最终靠测试改。")

h2(doc, "分支的后果")
para(doc, "不同选项带来不同后果：**名声（即人气）、伤病、教练信任、心态提升、比赛结果**。")
para(doc, "**首版不做关系系统**：教练信任是一个会涨会跌的数值，不是“每个 NPC 单独的好感度”。这条界线要在写事件时就守住。")

# ---------- 五
h1(doc, "五", "反馈池：笑点在这里")
para(doc, "事件只有 50 字，放不下铺垫，所以「会心一笑」由**行动结束后那一句话**承担：事先写一批短句存着，点的时候随机抽一句。")
para(doc, "**高光的判定**：有一个具体的人，在具体时刻，说了或做了什么。写成「你表现很好」是裁判念成绩；写成「教练合上本子问：什么时候能来」才是场面。")
note(doc, "上分·成功：「对面是代练吧，五分钟三杀。」　上分·失败：「连跪三把，弹幕开始刷『就这』。」\n直播·成功：「有人送了个飞机，然后撤回了。」")
for t in ["**结构**：按「行动 × 成功 / 失败」两级分，先不做阶段差异（18 岁和 28 岁同一句话，先接受）。",
          "**量**：每个组合 20–30 句，共约 8 个行动 × 2 组 ≈ **320–480 句**，每句 20–30 字。",
          "**防重样**：每个行动维护一个「未用队列」，用完再重洗——原则定下，公式等实现时写。",
          "**特殊性**：如果某句话只在特定阶段成立，它就是「特殊句子」，不进池子，写死在那个事件里。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 六
h1(doc, "六", "状态表 · 场外经济")
figure(doc, "p0-stats.png", "图 3　五个维进比赛，人气管场外，场外再绕回比赛", 15.0)

para(doc, "**这张表就是全部状态。** 事件、行动的后果只能落进这六个格子，或者写一个标记；写「六维 −」这种指不到位置的，不合格。", keep=True)
table(doc,
      ["状态", "范围", "用在哪", "怎么变"],
      [["操作 / 对线 / 团战 / 意识 / 心态", "0–100", "比赛事件结算，每个事件只读其中一两个", "行动、事件；**心态**随年龄变好，也能练出来"],
       ["人气", "0–100", "只在场外生效；也是「名声」", "直播、商业活动、事件曝光"],
       ["体力", "0–999", "每周三格的支付能力；不够就得休息", "消耗于行动；靠休息恢复、健身提上限"],
       ["段位", "十档分数 + 名次（王者须前 200、宗师须前 600）；分数与名次**都不显示**", "上分的行为结果；段位越高，六维经验越多", "上分"],
       ["金钱", "0–999999", "买资源；买不到比赛胜利，也买不到六维", "直播、商业活动"],
       ["伤病", "0–3（严重程度）", "3 = 赛季报销", "比赛事件与过劳"],
       ["教练信任", "0–100", "**能不能上场、能不能打训练赛**（出场概率的乘数）", "比赛表现、队内事件"]],
      [5.0, 4.2, 5.2, 5.4], size=8.5,
      caption="表 6　状态表：六个标量 + 一组六维，封闭集")

para(doc, "**刻度**：18 岁开场五项随机 40–70（心态不随），人气固定 20；小事件 +2～5、大事件 +8～12。段位按现实段位排十档（黑铁 · 青铜 · 白银 · 黄金 · 铂金 · 翡翠 · 钻石 · 大师 · 宗师 · 王者），有两层门槛：分数决定档位，**名次决定能不能拿到最高的两档**。", before=2)
para(doc, "**分数和名次都是隐藏的**：玩家只看到段位名，所以事件里不许写「你的段位提升了」或「你上了 500 分」，只能写它的后果——「有队伍愿意让你去试训了」。", before=2)

para(doc, "**比赛内临时值**：事件可以给「临时 ±10」，它只在当场比赛有效，比赛结算后清零，不写进存档——所以它不算第七个状态。", before=2)
para(doc, "**伤病**：体力归零仍被强制行动（或比赛失败带伤）就 +1；伤病期间每周扣体力上限，直到恢复。「休息」这个行动因此有了真实代价。", before=2)
para(doc, "**教练信任的硬规则**：低到一定值只能替补（能训练、不能首发），更低则下放（无比赛、只训练）。**阈值数字待测**，结构现在定。", before=2)
para(doc, "**场外链**：人气 → 赞助 → 钱 → 资源（训练次数、陪练、更好的队伍）。资源分**年度刷新**与**一次性**两类；一次性只给条件，不给上限。", before=2)

h2(doc, "成长怎么算")
for t in ["**年龄台阶为主**：每一年有一个「涨幅上限」，由年龄决定；训练和比赛决定你能不能吃到这个上限。",
          "**曲线放在成本上，不放在增量上**：行动给**整数经验**，攒够阈值属性 +1；阈值随属性升高而变贵，所以「越高涨越慢」。",
          "**对外永远是整数**：玩家看到的是「操作 57（进度 62/100）」，看不到 +0.36。",
          "**硬封顶**：100 就是 100，继续练不涨。"]:
    para(doc, t, bullet=True, after=3)

h2(doc, "一次性资源定三种")
table(doc,
      ["资源", "给什么条件", "挂在哪个系统"],
      [["更好的住处", "非比赛期恢复更快（体力 / 心态回升 +）", "体力与心态"],
       ["更好的外设", "训练效率小幅提升（成长速率 +）", "成长速率"],
       ["康复与医疗", "伤病恢复更快、复发率更低", "伤病"]],
      [4.4, 8.0, 3.6], size=9,
      caption="表 7　一次性资源：每种都必须挂在一个已存在的系统上")
para(doc, "**年度刷新那边至少要有三档**（训练次数、陪练、队医），否则攒钱会变成死钱。", before=2)

# ---------- 七
h1(doc, "七", "时间与结局")
para(doc, "18 岁起，8 年；每年 26 个比赛周（春 8 · MSI 4 · 夏 8 · S 赛 6）+ 年末休赛期 4 周，共 **208 个比赛周**。")
para(doc, "生涯三阶段（你定的）：**成长期 2 年（18–19 岁）→ 巅峰期 4 年（20–23 岁）→ 衰退期 2 年（24–25 岁）**，先上后下。")
para(doc, "衰退掉的是**对线、操作、团战、意识**；人气与心态不受影响——心态反而逐年变好。事件池的分桶就按这三段：成长期 = 第 1–2 年，巅峰期 = 第 3–6 年，衰退期 = 第 7–8 年。")

h2(doc, "结局：模板 + 变量")
table(doc,
      ["层", "由什么决定", "给玩家什么"],
      [["主结局（模板）", "**六维 + 荣誉**", "一段完整的「你的生涯是什么」"],
       ["事件尾注（小字）", "你触发过的标记", "「当年那个选择，让你变成了什么样」"]],
      [4.2, 6.4, 5.4], size=9,
      caption="表 8　结局两层：模板负责体量，尾注负责「这一局是我」")

para(doc, "**荣誉 7 种**：联赛冠军、MSI 冠军、S 赛冠军、常规赛 MVP、最佳阵容、最佳新秀、名人堂。每年可拿数量不限，后两个一次性。")
para(doc, "**荣誉怎么到手（按赛事结算）**：联赛冠军 = 春夏积分第一；MSI / S 赛冠军 = 对应决赛事件赢下；MVP 与最佳阵容 = 赛季末按六维排名；最佳新秀 = 第 1 年；名人堂 = 生涯结束时荣誉数达标。", before=2)
para(doc, "**终结只有一个入口**：**连续两个签约窗口无人可签**。单次无人可签只是回到自由人，继续等。窗口数量先按「两个」走，测试再调。")
para(doc, "**特殊结局一套模板 + 变量**（哪一年、什么数值、哪次选择）。它对实现有硬要求：**每个事件要带标记**，否则尾注生不出来。")

# ---------- 八
h1(doc, "八", "内容量级（估算）")
for t in ["**事件**：50 字 × 池子大小。**总数未定**——先写 3 个跑通，再定扩到多少。",
          "**空池**：普通周抽不到事件就不抽（照走三格行动 + 比赛）；另配少量「无条件填充事件」，防止连续几周空着。关键节点（决赛、转会、签约）不依赖池子，用写死的特殊事件。",
          "**反馈池**：8 个行动 × 2 组 × 20–30 句 ≈ **320–480 句**，每句 20–30 字。这是文本大头。",
          "**比赛**：208 场，不可能每场独立写——只能靠比赛事件模板池，特殊比赛（决赛级）单独写死。",
          "以上都是【估计】，没有一手来源；它们只说明一件事：**你的 5 小时/周，主要花在短句上，不在长文上**。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 九
h1(doc, "九", "已知风险（我的判断）")
for s in ["**50 字封顶 = 事件承载不了情节。** 好处是产能可控，坏处是「这一局的记忆点」必须靠事件之外的东西（反馈、荣誉演出）撑起来。",
          "**梗有保质期。** 结构性梗（四保一、下路双人组、世界赛魔咒）比绑定具体选手的耐久；后者还牵涉 IP。",
          "**钱是唯一的中介。** 人气 → 赞助 → 钱 → 资源是一条单链，玩家迟早会发现「只要搞钱就行」。",
          "**数值分散导致成长感弱。** 六维里五维都能涨，单维在几十个事件里只有十来次提升机会——这正是你批评《峡谷一生》「提升太慢」的机制成因。",
          "**衰退要找得到体感。** 玩家得知道自己什么时候从巅峰下滑，否则衰退只是背地里扣数。",
          "**没有后端 = 内容全写死。** 改一句文案也要重新上传、重新过审；所以文案一次要写对，别指望上线后热修。"]:
    para(doc, s, bullet=True, after=3)

# ---------- 十
h1(doc, "十", "平台给的技术边界（已查证）")
table(doc,
      ["项", "要求"],
      [["形态", "纯前端网页：`.zip` / 单个 `.html` / 文件夹，必须有 `index.html`"],
       ["后端", "**没有**后端、数据库、登录鉴权"],
       ["额度", "整包 ≤50MB；单个 HTML ≤5MB；图片音视频单个 ≤25MB、合计 ≤100MB；≤300 个文件（**总额度自相矛盾**，见下"],
       ["屏幕", "预览是手机竖屏框，线上注入 `viewport=device-width`；必须做移动端自适应"],
       ["变现", "只有 IAA 广告，由创作者勾选；没有付费下载"],
       ["IP", "没有明文禁令；有在架先例（LoL 题材 + 真实战队缩写 + 虚构选手 + 标注）"],
       ["依赖", "禁止外部 CDN / 外链资源 / 跳转下载；**所有依赖必须打进包里**"],
       ["著作权", "归你，但投稿即授予平台全球永久、不可撤销、可转授；维权以平台名义、所得归平台"]],
      [3.0, 13.0], size=9,
      caption="表 9　平台边界：来自 shaper.hupu.com/docs 与官方公告帖")

para(doc, "两条推论：**游戏里跑不了 AI**（没后端，调模型就得把密钥泄在前端），所以这里的「AI」只是你用它来做游戏；**50 字事件刚好一屏**，你选的字数和手机竖屏天然吻合。")
para(doc, "**额度那一行自相矛盾**：整包 ≤50MB，却又说图片音视频合计 ≤100MB。装不下。按最严的 50MB 规划——你的文本只有几百 KB，短期用不满，但将来加音频时它会先撞墙。")
para(doc, "**IP 的张力**：协议要求「原创或已获完整可转授权、无侵权风险」，而平台有「真实战队缩写 + 虚构选手」的在架先例。先例是默许，协议才是追责依据——你现在的写法是先例里最保守的一档，但它不受协议保护。")
para(doc, "**以上正文我没能独立核对**：文档与协议页都是前端渲染，直接抓只拿到页面标题。拿到邀请码后，自己登录把 5.x 与 6.x 读一遍。")


h1(doc, "十一", "下一步")
note(doc, "**下一步是 P2：一个能点的骨架**——竖屏、三格行动、抽事件、结算、结周存档。事件用现有的三个，数值用占位。目标不是好玩，是**能在手机上点通一周、刷新页面存档还在**。", spacer=False)

OUTDOC = OUT
doc.save(OUTDOC)
print("saved:", OUTDOC)
