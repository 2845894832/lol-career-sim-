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
OUT = os.path.join(HERE, "P1-概念与核心循环.docx")

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
set_run(hp.add_run("P1 概念与核心循环 · v0.2"), 8.5, False, M)
border(hp, "DCE4EC", 4)


# ---------- 标题
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(6)
p.paragraph_format.space_after = Pt(2)
set_run(p.add_run("P1 概念与核心循环"), 24, True, N)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(10)
set_run(p.add_run("第二版：补上段位、胜负公式与当前实现进度　·　v0.2　·　2026-10-31"), 9.5, False, M)
border(p, "C9D6E3", 8)

para(doc, "这份文档是 P1 阶段的**完整口径**：核心循环怎么转、段位怎么爬、一场比赛怎么判胜负、事件怎么触发、数值怎么长、结局怎么收。凡是和代码不一致的地方，以本文为准，然后改代码。", after=10)

# ---------- 一
h1(doc, "一", "一句话")
note(doc, "18 岁入行，208 个比赛周。每周排三个行动、抽一个事件、打一场比赛，靠六维与可见概率走到一个结局。目标不是「通关」，是玩家看见熟悉的梗时**会心一笑**。")

# ---------- 二
h1(doc, "二", "核心循环")
para(doc, "一周固定三格行动，抽一个事件，有比赛就打一场，然后结周存档。", keep=True)
figure(doc, "p0-week.png", "图 1　周循环：内容只在「抽事件」和「比赛」这两格里", 15.6)

h2(doc, "八种行动")
table(doc,
      ["行动", "体力", "收益（每格）", "解锁"],
      [["上分", "14 起", "对线 **+1**、操作 **+1**；段位分数 ↑", "开局"],
       ["专项训练", "12 起", "**指定一维 +2**", "开局"],
       ["复盘录像", "8 起", "意识 **+1**", "开局"],
       ["训练赛", "16 起", "团战 **+1**、意识 **+1**、教练信任 **+2**", "签约后"],
       ["健身", "8", "体力上限 **+4**", "开局"],
       ["直播", "10", "钱 **+400**、人气 **+2**", "开局"],
       ["商业活动", "25", "钱 **+800**、人气 **+5**", "签约后"],
       ["休息", "0", "体力 **+（上限 × 25%）**", "开局"]],
      [3.0, 2.4, 8.6, 2.0], size=9,
      caption="表 1　八个行动：三格里排什么，就是你的策略")

para(doc, "四项训练（上分 / 专训 / 复盘 / 训练赛）的体力是**递增的**：「14 起」的意思是属性在 40–49 时收 14，之后每高 10 点加 3。", keep=True)
table(doc,
      ["行动", "基础", "40–49", "50–59", "60–69", "70–79", "80–89", "90–100"],
      [["上分", "14", "14", "17", "20", "23", "26", "29"],
       ["专项训练", "12", "12", "15", "18", "21", "24", "27"],
       ["复盘录像", "8", "8", "11", "14", "17", "20", "23"],
       ["训练赛", "16", "16", "19", "22", "25", "28", "31"]],
      [2.6, 1.6, 1.7, 1.7, 1.7, 1.7, 1.7, 1.9], size=8.5,
      caption="表 2　越练越贵：成本随属性上涨，收益始终是整数 1 点")

para(doc, "**收益固定 1 点**（专训 2 点），没有分段、没有成长加成。所以「越练越慢」完全落在成本侧：属性越高，同一格越贵。")

h2(doc, "体力与结周")
for t in ["每个行动点都要花体力；**体力不够支付三格，就不能结周**。",
          "**三个行动点必须排满才能结周**——排不满就拦下并说明原因。",
          "已排的格子**可以清空重排**，不强迫你接受第一次的选择。",
          "体力**每周不自动回满**：只有休息能恢复，一次回「当前上限的 25%」。开局 60 / 100，所以第一次休息回 25。",
          "体力上限初始 100，健身每次 +4，**封顶 999**。因为休息按上限比例回，**上限每 +4，每周就多回 1 体力**——健身因此从「纯亏」变成投资。",
          "健身有**最优次数**（约 20 次）：它真正的用处是填掉那些体力不够、本来要空着的格子。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 三
h1(doc, "三", "段位与签约")
para(doc, "段位是**两层**：分数决定你在哪一档，名次决定你能不能拿到最高的两档。分数和名次都**不显示**——玩家只看到段位名。")

table(doc,
      ["段位", "分数下限", "还要什么", "每周上分（花一格）"],
      [["黑铁 / 青铜", "0 / 400", "—", "900 / 810"],
       ["白银 / 黄金", "900 / 1500", "—", "720 / 630"],
       ["铂金 / 翡翠", "2100 / 2500", "—", "540 / 470"],
       ["钻石", "2700", "—", "410"],
       ["大师（开局）", "**2800**", "—", "380"],
       ["宗师", "3800", "**名次进前 600**", "350"],
       ["王者", "4500", "**名次进前 200**", "315"]],
      [3.4, 2.8, 3.6, 4.4], size=9,
      caption="表 2　分数 + 名次双重门槛；上分收益按档位递减")

para(doc, "**名次是相对位置**：榜上还有一万个对手，他们也每周在爬，而且同样按档位减速。所以「不练会掉」不是扣分，是别人超过你。", before=2)

for t in ["**开局就是大师 2800，第 6929 名**：实力够、但没人认识——这正是「从没人认识到被看见」的起点。",
          "**一次「上分」= 一周的排位打包**，收益随档位递减（黑铁 900 → 王者 315）。",
          "**王者要两样**：分数到 4500，且名次进前 200。分数够了名次不够，就封在宗师。",
          "**不扣分，但会掉名次**：一周不打，别人超过你。实测两周还稳在王者，第三周掉回宗师。",
          "**段位到王者，当周必定收到邀请函**：接受就直接签约，不等第 30 周窗口；拒绝可以继续当路人，第二年还会再来。人气不参与签约——人气只管商业赞助和钱。"]:
    para(doc, t, bullet=True, after=3)

para(doc, "实测曲线（每周花一格上分）：", before=6)
table(doc,
      ["时点", "名次", "段位"],
      [["开局", "第 6929 名", "大师"],
       ["第 3 周", "第 1846 名", "大师"],
       ["第 4 周", "第 521 名", "**宗师**"],
       ["第 5 周", "第 1 名", "**王者**"],
       ["不打第 2 周", "第 89 名", "王者"],
       ["不打第 3 周", "第 512 名", "宗师"]],
      [4.6, 5.0, 4.4], size=9,
      caption="表 3　目标是「4 周宗师、5 周王者、3 周不打掉回宗师」，已按此调参")

# ---------- 四
h1(doc, "四", "比赛怎么判胜负")
para(doc, "**所有比赛用同一条公式**，不管是每周的常规赛、事件里的比赛，还是决赛：", keep=True)

para(doc, "胜率 = 0.5 +（六维均值 − 对手强度）÷ 50 + 选项加成", color=G)
para(doc, "**「对手强度」这一项还没定。** 表里那四个数只让公式能跑起来，谁强谁弱、强多少，要等对手（队伍 / 选手）的能力表做出来才有意义。", after=6)
para(doc, "其中「六维均值」实际取五项：操作、对线、团战、意识、心态；**人气不参与比赛**。")

table(doc,
      ["对手", "强度", "六维 70 时的基础胜率"],
      [["常规比赛", "60（占位）", "70%"],
       ["春季赛决赛", "65（占位）", "60%"],
       ["夏季赛决赛", "70（占位）", "50%"],
       ["S 赛决赛", "78（占位）", "34%"]],
      [6.6, 4.0, 5.4], size=9,
      caption="表 3　这四个数是占位，不是设计决定——对手强度应由对手自身能力算出来，能力表还没做")

para(doc, "**选项只给加成，不决定胜负。** 比赛事件的每个选项带一个胜率加成，掷一次定输赢：")
table(doc,
      ["选项", "加成", "失败代价"],
      [["闪现进场开大", "+15%", "心态 −3、教练信任 −5"],
       ["拉扯等超级兵回推", "+5%", "人气 −2"],
       ["回守高地", "−15%", "人气 −1；失败再扣人气与信任"]],
      [7.0, 3.4, 5.6], size=9,
      caption="表 4　事件 1 的三个选项：加成写在选项上，后果写在状态上")

for t in ["**上下限 5% / 95%**：再强也可能翻车，再弱也有一线机会。",
          "**决赛拿冠军 = 赢下那场 + 对应荣誉**；春季赛、夏季赛、MSI、S 赛各一个决赛。",
          "**不做积分系统**：冠军只看那场决赛的胜负，不看常规赛累计。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 五
h1(doc, "五", "事件")
para(doc, "事件分三类，比例按「比赛最多、生活其次、特殊最少」排。", keep=True)
figure(doc, "p0-loop.png", "图 2　事件链：文本负责梗，骰子只决定成败", 15.0)
table(doc,
      ["类别", "多久一次", "写什么", "怎么出现"],
      [["比赛事件", "最高（有比赛的周）", "一场比赛的选项，影响胜负", "每周抽"],
       ["生活事件", "次之", "训练、采访、转会、队内摩擦", "按条件抽"],
       ["特殊事件", "最低（一年一两次）", "写死年份或条件的一次性剧情", "写死或低权重抽"]],
      [3.0, 4.4, 5.4, 3.2], size=9,
      caption="表 5　三类事件；特殊事件与「大事件」是两个维度，别混")

table(doc,
      ["环节", "规则"],
      [["篇幅", "**50 字左右，绝对不能长**"],
       ["结构", "文本场景 + 2–3 个选择；允许开头一句无选择的铺垫"],
       ["局势", "事件自带的环境变量，写死；比赛事件还带对手强度"],
       ["结算", "比赛事件走统一胜负公式；其它事件用属性均值"],
       ["梗", "无论输赢文本都带梗；主战场在反馈池"],
       ["后果", "只能落在状态表的一格，或写一个标记"],
       ["必成 / 必败", "非比赛事件可以必成、必败；比赛事件一律掷骰"],
       ["临时值", "只在当场有效，比赛结算后清零，不进存档"]],
      [3.4, 12.6], size=9,
      caption="表 6　事件的八条规则")

h2(doc, "触发与权重")
for t in ["**分桶**：成长期 / 巅峰期 / 衰退期分开，每桶数量不等。",
          "**标签 + 前置标记**：条件写成「某标签的事件发生过」「某个标记存在」。",
          "**权重**：特殊 : 常规 = 1 : 10。出现率由条数稀释：S ÷ (10C + S)。",
          "**兜底**：抽不到就落回无条件填充池；连它也没有，这周就不抽，照常结周。",
          "**必触发**：签约、首秀、决赛、退役写死，不参与抽签。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 六
h1(doc, "六", "反馈池：笑点在这里")
para(doc, "事件只有 50 字，放不下铺垫，所以「会心一笑」由**行动结束后那一句话**承担：事先写一批短句存着，点的时候随机抽一句。")
note(doc, "上分·成功：「对面是代练吧，五分钟三杀。」　上分·失败：「连跪三把，弹幕开始刷『就这』。」\n直播·成功：「有人送了个飞机，然后撤回了。」")
for t in ["**结构**：按「行动 × 成功 / 失败」两级分，先不做阶段差异。",
          "**量**：每个组合 20–30 句，约 320–480 句，每句 20–30 字。这是文本大头。",
          "**防重样**：每个行动维护「未用队列」，用完再重洗。",
          "**高光**：要写成有具体的人、动作、一句话的场面，不是「你表现很好」。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 七
h1(doc, "七", "状态表与成长")
figure(doc, "p0-stats.png", "图 3　五个维进比赛，人气管场外，场外再绕回比赛", 14.4)
table(doc,
      ["状态", "范围", "用在哪"],
      [["操作 / 对线 / 团战 / 意识 / 心态", "0–100", "比赛结算，每次只读其中一两个"],
       ["人气", "0–100", "只在场外；也是「名声」，不进比赛公式"],
       ["体力", "0–999", "每周三格的支付能力；健身提上限"],
       ["段位", "分数 + 名次，都隐藏", "上分结果；到王者必签"],
       ["金钱", "0–999999", "买资源，买不到胜利与六维"],
       ["伤病", "0–3", "3 = 赛季报销"],
       ["教练信任", "0–100", "能否上场、能否打训练赛；进胜负公式做微调"]],
      [5.4, 3.8, 6.8], size=9,
      caption="表 7　状态表是封闭集：后果只能落在这里，或写标记")

h2(doc, "成长")
for t in ["**年龄台阶为主**：每年一个涨幅上限，由年龄决定；训练与比赛决定吃到多少。",
          "**曲线放在成本上**：行动给整数经验，阈值随属性变高而变贵——「越高涨越慢」。",
          "**对外永远是整数**，进度条单独显示；100 硬封顶。",
          "**三阶段**：成长期 18–19 岁、巅峰期 20–23 岁、衰退期 24–25 岁。衰退只掉对线、操作、团战、意识；心态与人气不降。"]:
    para(doc, t, bullet=True, after=3)

# ---------- 八
h1(doc, "八", "场外经济与结局")
para(doc, "**场外链**：人气 → 赞助 → 钱 → 资源。资源分年度刷新与一次性两类，一次性只给条件、不给上限。")
para(doc, "**钱买不到**：比赛胜利、六维数值、段位。")

h2(doc, "结局")
table(doc,
      ["层", "由什么决定", "给玩家什么"],
      [["主结局（模板）", "六维 + 荣誉", "一段完整的「你的生涯是什么」"],
       ["事件尾注（小字）", "你触发过的标记", "「当年那个选择，让你变成了什么样」"]],
      [4.2, 6.4, 5.4], size=9,
      caption="表 8　结局两层：模板负责体量，尾注负责「这一局是我」")
para(doc, "**荣誉 7 种**：联赛冠军、MSI 冠军、S 赛冠军、常规赛 MVP、最佳阵容、最佳新秀、名人堂。")
para(doc, "**终结只有一个入口**：连续两个签约窗口无人可签。单次只是自由人，继续等。")

# ---------- 九
h1(doc, "九", "还没写的东西")
para(doc, "下面这些是**已经想清楚、但代码里还没有**的部分，按优先级排：")
table(doc,
      ["项", "缺什么", "影响"],
      [["邀请函", "签约窗口目前是静默判定，没有「收到邀请函」这个事件/界面", "玩家不知道自己是怎么进的队"],
       ["职业战队", "没有队伍实体：队名、队友、教练、转会都没建模", "联赛冠军、转会事件、队内摩擦都悬空"],
       ["春决 / 夏决", "E04 / E05 只在事件库里，代码里没有", "拿不到联赛冠军"],
       ["反馈池文案", "现在每个行动只有一句固定文案，没有池子", "「会心一笑」还没落地"]],
      [3.4, 7.6, 5.0], size=9,
      caption="表 9　未完成清单：这四项不补，系统就是半截的")

# ---------- 十
h1(doc, "十", "P1 的过关标准")
para(doc, "手册里 P1 的过关标准是两条：**陌生人读完能复述循环**；**你能指出「如果这条假设错了，第一步改哪里」**。")
para(doc, "第一条已经成立。第二条需要一条明确的假设：")
note(doc, "**假设**：如果每个选择都要用某种稀缺资源去换（体力、行动位、LP、人情），玩家就会感到取舍。\n**如果它错了**：玩家只会觉得「点什么都一样」，第一步改的是**行动位数量**（三格改两格，逼出取舍），不是改数值。")
para(doc, "验法：让人连点 10 周，问他「这周为什么这么排」。答不出取舍，假设就错了。")

doc.save(OUT)
print("saved:", OUT)
