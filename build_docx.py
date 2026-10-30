# -*- coding: utf-8 -*-
"""构建《Vibe Coding 独立游戏制作人 · 全流程手册》DOCX。"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(HERE, "charts")
OUT = os.path.join(HERE, "Vibe Coding 独立游戏制作人-全流程手册.docx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2F, 0x6F, 0xA8)
TEAL = RGBColor(0x2E, 0x8B, 0x7E)
GREY = RGBColor(0x5B, 0x66, 0x74)
MUTED = RGBColor(0x8B, 0x95, 0xA3)
INK = RGBColor(0x1B, 0x1B, 0x1B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

CN = "微软雅黑"
CN_SERIF = "宋体"


# ------------------------------------------------------------------ 基础工具
def set_run(run, size=10.5, bold=False, color=None, name=CN, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = name
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    rf.set(qn("w:ascii"), name)
    rf.set(qn("w:hAnsi"), name)
    rf.set(qn("w:eastAsia"), name)
    return run


def rich(p, text, size=10.5, color=INK, bold_color=None, name=CN):
    """支持 **粗体** 的简易内联解析。"""
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        r = p.add_run(part)
        set_run(r, size, i % 2 == 1, bold_color if (i % 2 == 1 and bold_color) else color, name)
    return p


def para(doc, text="", size=10.5, color=INK, bullet=False, indent=True,
         space_before=0, space_after=6, align=None, line=1.5, bold=False,
         keep_with_next=False, style=None):
    p = doc.add_paragraph(style="List Bullet" if bullet else style)
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if indent and not bullet:
        pf.first_line_indent = Pt(size * 2)
    if align is not None:
        p.alignment = align
    if keep_with_next:
        pf.keep_with_next = True
    if text:
        rich(p, text, size, color)
        if bold:
            for r in p.runs:
                r.font.bold = True
    return p


def bottom_border(p, color="1F3A5F", size=8):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def h1(doc, text, number=None):
    p = doc.add_heading(level=1)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    if number:
        r = p.add_run(number + "　")
        set_run(r, 17, True, TEAL)
    set_run(p.add_run(text), 17, True, NAVY)
    bottom_border(p, "C9D6E3", 6)
    return p


def h2(doc, text):
    p = doc.add_heading(level=2)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(text), 12.5, True, BLUE)
    return p


def strip_pic_border(inline):
    spPr = inline._inline.graphic.graphicData.pic.spPr
    ln = OxmlElement("a:ln")
    ln.append(OxmlElement("a:noFill"))
    spPr.append(ln)


def figure(doc, fname, caption, width_cm):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    shp = p.add_run().add_picture(os.path.join(CHARTS, fname), width=Cm(width_cm))
    strip_pic_border(shp)
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(12)
    set_run(c.add_run(caption), 9, False, MUTED)


def shade(cell, hexval):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexval)
    tcPr.append(sh)


def cell_margins(table, top=60, bottom=60, left=100, right=100):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for tag, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:w"), str(v))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def table_borders(table, color="CDD8E3", size=6):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def add_table(doc, header, rows, widths, size=9, header_size=9,
              zebra="F4F7FA", first_col_bold=True, caption=None, keep_together=None):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t)
    cell_margins(t)
    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); trPr.append(th)
    cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    for i, txt in enumerate(header):
        c = hdr.cells[i]
        c.width = Cm(widths[i])
        shade(c, "1F3A5F")
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        set_run(p.add_run(txt), header_size, True, WHITE)
    for ri, row in enumerate(rows):
        r = t.add_row()
        trPr = r._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        cells = r.cells
        for ci, txt in enumerate(row):
            c = cells[ci]
            c.width = Cm(widths[ci])
            if zebra and ri % 2 == 1:
                shade(c, zebra)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.2
            bold = first_col_bold and ci == 0
            rich(p, txt, size, INK)
            if bold:
                for r in p.runs:
                    r.font.bold = True
    # 表宽
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    if keep_together is None:
        keep_together = len(rows) <= 6
    if keep_together:
        for ri, row in enumerate(t.rows):
            for c in row.cells:
                for pp in c.paragraphs:
                    pp.paragraph_format.keep_with_next = ri < len(t.rows) - 1
    if caption:
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_before = Pt(4)
        c.paragraph_format.space_after = Pt(12)
        set_run(c.add_run(caption), 9, False, MUTED)
    return t


def note(doc, text, accent="2F6FA8", fill="EEF4FA"):
    t = doc.add_table(rows=1, cols=1)
    t.autofit = False
    t.columns[0].width = Cm(16.0)
    cell = t.rows[0].cells[0]
    cell.width = Cm(16.0)
    shade(cell, fill)
    tblPr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:val"), "single" if tag == "left" else "nil")
        el.set(qn("w:sz"), "18" if tag == "left" else "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), accent)
        borders.append(el)
    tblPr.append(borders)
    cell_margins(t, 90, 90, 160, 160)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.35
    rich(p, text, 9.5, RGBColor(0x33, 0x3B, 0x45))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_field(paragraph, code):
    r = paragraph.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = code
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "1"
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(it); r._r.append(f2); r._r.append(t); r._r.append(f3)
    set_run(r, 9, False, MUTED)


# ------------------------------------------------------------------ 文档
doc = Document()

st = doc.styles["Normal"]
st.font.name = CN
st.font.size = Pt(10.5)
st.font.color.rgb = INK
st.element.rPr.rFonts.set(qn("w:eastAsia"), CN)

sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.2)
sec.bottom_margin = Cm(2.0)
sec.left_margin = Cm(2.5)
sec.right_margin = Cm(2.5)
sec.header_distance = Cm(1.2)
sec.footer_distance = Cm(1.1)

# 页眉
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
set_run(hp.add_run("Vibe Coding 独立游戏制作人 · 全流程手册"), 8.5, False, MUTED)
bottom_border(hp, "DCE4EC", 4)

# 页脚
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(fp.add_run("— "), 9, False, MUTED)
add_field(fp, "PAGE")
set_run(fp.add_run(" —"), 9, False, MUTED)

# ------------------------------------------------------------------ 封面
for _ in range(3):
    doc.add_paragraph()

bar = doc.add_table(rows=1, cols=1)
bar.autofit = False
bar.columns[0].width = Cm(4.6)
c = bar.rows[0].cells[0]
c.width = Cm(4.6)
shade(c, "2E8B7E")
c.paragraphs[0].paragraph_format.space_after = Pt(0)
set_run(c.paragraphs[0].add_run(" "), 2, False, WHITE)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(18)
p.paragraph_format.space_after = Pt(2)
set_run(p.add_run("Vibe Coding"), 30, True, NAVY)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(4)
set_run(p.add_run("独立游戏制作人"), 30, True, NAVY)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(6)
p.paragraph_format.space_after = Pt(26)
set_run(p.add_run("全 流 程 手 册"), 15, False, TEAL)
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(28)
set_run(p.add_run("从一句话的想法，到上线之后的第一个补丁"), 11.5, False, GREY)

rule = doc.add_paragraph()
rule.paragraph_format.space_after = Pt(18)
bottom_border(rule, "C9D6E3", 8)

for label, value in [
    ("适用前提", "不写代码，用 AI 当施工队；每周可支配 5 小时上下；第一款作品，不背收入压力。"),
    ("覆盖范围", "九个制作阶段 · 分工与验收 · 能力地图 · 工具链 · 节奏与风险。"),
    ("不覆盖", "题材、玩法、数值、美术风格、界面布局——这些是你的判断，本文件刻意留白。"),
    ("读法", "第一遍读第二、三章建立全局；动手时只翻当前阶段与第四、八章。"),
]:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.4
    set_run(p.add_run(label + "　"), 9.5, True, NAVY)
    set_run(p.add_run(value), 9.5, False, GREY)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(40)
set_run(p.add_run("2026 年 10 月"), 9, False, MUTED)
set_run(p.add_run("　　·　　文中数值均为经验区间，标注为【建议】的判断可直接否决"), 9, False, MUTED)

doc.add_page_break()

# ------------------------------------------------------------------ 导航
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(10)
set_run(p.add_run("本文导航"), 13, True, NAVY)
bottom_border(p, "C9D6E3", 6)

nav = [
    ("一　这份文件怎么用", "三类标记，以及为什么流程不是瀑布"),
    ("二　全流程总览", "九阶段一页看完，附时间量级"),
    ("三　九个阶段逐个过", "每个阶段：产出、你定的、AI 干的、过关标准"),
    ("四　Vibe Coding 的分工", "决策权迁移、规格写法、验收指标、AI 的边界"),
    ("五　能力地图", "哪些必须能判断，哪些够用就行"),
    ("六　时间与节奏", "5 小时怎么切，最小闭环"),
    ("七　工具链", "每个环节的最小可用方案与引入时机"),
    ("八　风险与对策", "九种死法，以及各自的挡板"),
    ("九　附录", "术语表"),
]
t = doc.add_table(rows=0, cols=2)
t.style = "Table Grid"
t.autofit = False
_nb = OxmlElement("w:tblBorders")
for _tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
    _el = OxmlElement(f"w:{_tag}")
    _el.set(qn("w:val"), "nil")
    _nb.append(_el)
t._tbl.tblPr.append(_nb)
cell_margins(t, 40, 40, 0, 0)
for name, desc in nav:
    cells = t.add_row().cells
    cells[0].width = Cm(5.4)
    cells[1].width = Cm(10.6)
    p0 = cells[0].paragraphs[0]
    p0.paragraph_format.space_after = Pt(3)
    set_run(p0.add_run(name), 10, True, NAVY)
    p1 = cells[1].paragraphs[0]
    p1.paragraph_format.space_after = Pt(3)
    set_run(p1.add_run(desc), 9.5, False, GREY)
t.columns[0].width = Cm(5.4)
t.columns[1].width = Cm(10.6)

# ------------------------------------------------------------------ 一
h1(doc, "这份文件怎么用", "一")

para(doc, "这份手册只回答一个问题：**一个不写代码的人，怎么用 AI 把一款游戏从一句话做到上线**，并在过程中把「制作人」该有的判断力长出来。")
para(doc, "全流程分九个阶段（P0–P8）。每个阶段说清四件事：这一步要产出什么、只有你能定的是什么、AI 能替你干什么、怎么判断这一步算过了。**题材、玩法、数值、界面布局一律不写**——那是你的判断，写进来就等于我替你做了决定。")

para(doc, "三类标记贯穿全文：", space_before=4, keep_with_next=True)
add_table(
    doc,
    ["标记", "含义", "你怎么用"],
    [
        ["【事实】", "可查证的做法、行业惯例或公开研究结论。", "可以直接依赖；有疑问就自己去查。"],
        ["【建议】", "我的判断，来自经验而非测量。", "可以直接否决，不需要理由。"],
        ["【你定】", "刻意留白的位置。", "只有你能填，填完才算真的开工。"],
    ],
    [2.4, 7.6, 6.0], size=9,
)
doc.add_paragraph().paragraph_format.space_after = Pt(0)

para(doc, "还有一个前提要先说清：**九个阶段不是瀑布**。真实项目里「做原型时发现概念不成立，回去改概念」是常态，尤其第一次做。流程图的作用不是让你按顺序打卡，而是让你随时知道自己漏了哪一步。")
note(doc, "**读这份文件的最快方式**：先看第二章那张图和表，建立全局；然后跳到你现在所处的阶段；动手卡住时回来看第四、八章。不要从第一页读到最后一页——那是学教材的方式，不是做东西的方式。")

# ------------------------------------------------------------------ 二
h1(doc, "全流程总览", "二")

para(doc, "九个阶段串起来是一条完整的生产链。每个阶段都有一件「只有做对了才允许进入下一步」的事，那是它的过关标准；跳过它，问题不会消失，只会在后面以返工的形式回来。")

figure(doc, "fig1-pipeline.png", "图 1　全流程九阶段：箭头是推荐推进顺序，不是硬性门禁", 16.2)

para(doc, "把同样的九个阶段压成一张表，方便你对照自己现在在哪一格。", space_before=2, keep_with_next=True)

add_table(
    doc,
    ["阶段", "核心问题", "关键产出", "谁定方向", "最容易死在哪"],
    [
        ["P0 定位与约束", "给谁玩、多大规模、多久做完", "一页约束清单", "你", "直接开工，三个月后发现规模是三年的"],
        ["P1 概念与循环", "玩家重复做什么，为什么重复", "一页纸 + 循环图 + 一条待验证假设", "你", "塞进五个系统，没有一个闭环"],
        ["P2 可玩原型", "最丑的核心还能玩吗", "能连玩 5 分钟的原型", "你", "先做菜单、存档、设置"],
        ["P3 纵向切片", "打磨之后是什么手感", "5–10 分钟「像成品」的片段", "你", "切片越做越大，成了半个游戏"],
        ["P4 内容量产", "怎么把切片扩成完整内容量", "可从第一关走到最后一关的版本", "AI 扩写 / 你验收", "一边扩内容一边改核心机制"],
        ["P5 打磨", "什么算够好了", "候选发布版", "AI 执行 / 你定标准", "没有完工定义，无限打磨"],
        ["P6 测试与平衡", "真实玩家卡在哪、停在哪", "行为观察报告", "你", "只找朋友测，只问「好不好玩」"],
        ["P7 发布准备", "陌生人怎么找到并看懂它", "商店页 + 构建 + 预告片", "AI 施工 / 你定文案", "上线前三天才做商店页"],
        ["P8 上线之后", "下一款要改什么", "补丁 + 复盘", "你", "上线即弃坑，或无限修"],
    ],
    [2.9, 3.9, 3.9, 2.1, 3.2], size=8.5, keep_together=False,
    caption="表 1　九阶段总表：核心问题、产出、决策归属与典型死法",
)

para(doc, "关于时间量级，先给一个校准数字。", space_before=2)
para(doc, "【经验估计】第一款 1–3 小时内容体量的小游戏，从零到能发布，新手通常需要 150–300 小时；每周 5 小时，约等于 **30–60 周**。注意这是「做完并发布」，不是「做出一个 demo」——两者之间隔着量产、打磨和测试三个阶段。")
para(doc, "所以「一年一款」不是保守，是**上限**。任何让你在第一款就想做 10 小时以上内容的方案，都不需要讨论可行性，直接砍。")

# ------------------------------------------------------------------ 三
h1(doc, "九个阶段逐个过", "三")

para(doc, "每个阶段固定四段：要达到什么、只有你能定什么、AI 能替你做、什么算过了。最后附一句最常见的死法。", space_after=4)

STAGES = [
    ("3.1　P0　定位与约束", "1–3 天",
     "把「我想做游戏」变成一组可执行的约束：平台、内容体量、单人还是多人、首版做多久、你每周真的能投入多少小时。",
     ["给谁玩——一个具体的人，不是「玩家」。",
      "一局多长、一共多长。",
      "首版必须有什么，以及**坚决不做什么**。"],
     "查同类作品的实际体量与定价、拆它们的商店页、估算内容量。要求它给来源，不要它给结论。",
     "你能用三句话说完「给谁、玩多久、为什么是你做」，并且说得出首版砍掉了什么。",
     "跳过这一步直接开工。三个月后发现自己选的方向需要三年、需要美术团队、需要联机。"),

    ("3.2　P1　概念与核心循环", "1–2 周",
     "一句能复述的循环、一页纸规则、以及一条你认为最关键但尚未验证的假设。",
     ["玩家每 10 秒、每分钟、每一局分别在做什么。",
      "失败与奖励的结构。",
      "节奏单位：一局 30 秒还是 30 分钟。"],
     "把循环翻译成状态机草图；列同类作品的循环结构对照；帮你把规则改写成没有歧义的句子——这个过程本身就是第一次验收练习。",
     "陌生人读完一页纸能复述你在循环什么；你能指出「如果这条假设错了，我第一步改哪里」。",
     "概念里放了五个系统，每个都只有半句话。或者核心描述是「玩法是探索」这种无法验收的东西。"),

    ("3.3　P2　可玩原型", "2–3 周",
     "最丑、但已经能玩的核心 60 秒。丑是刻意的，不是没做完。",
     ["手感的目标：要「重」还是「脆」。",
      "什么叫做对了——一个可观察的现象，不是形容词。",
      "这一版允许有多粗糙。"],
     "占位方块、临时 UI、最小场景、键盘或手柄输入。所有资源都用免费占位件。",
     "你自己愿意重复玩 10 次，并且每一次都能说出「哪里不对」。",
     "原型还没成立就先做菜单、教程、存档、设置。这些是壳，壳做完了里面还是空的。"),

    ("3.4　P3　纵向切片", "2–3 周",
     "5–10 分钟，但美术、音效、UI、转场全部按成品标准做的一段。它要证明「打磨之后到底成不成立」。",
     ["这一段要证明什么（通常只证明一件事）。",
      "哪些资源算达到标准。"],
     "把占位资源换成正式资源、加音效与打击反馈、做转场与字幕、补上引导。",
     "给 3 个陌生人不做任何解释地玩，他们主动问「完整的什么时候能玩」。",
     "切片越加越长，最后变成「半个游戏 + 剩下半个遥遥无期」。切片是证据，不是产品。"),

    ("3.5　P4　内容量产", "4–8 周",
     "从第一关到最后一关都能走完的完整版本——不打磨，但内容齐全。",
     ["内容清单与优先级：哪些必须有，哪些可以砍。",
      "每一关、每一天、每一局的差异点是什么。"],
     "同构扩写：按你给的模板批量产出关卡、对话、道具、数值表。你负责验收一致性。",
     "从头到尾能通关，没有阻断性 bug。",
     "一边扩内容一边改核心机制。返工率会让 8 周变成 20 周——这是量产期最大的时间黑洞。"),

    ("3.6　P5　打磨", "2–4 周",
     "从「能玩」到「玩着舒服」：手感、反馈、可读性、节奏。",
     ["什么算够好了——**写下来**。没有这句话，打磨会吞掉你所有剩余时间。",
      "哪些地方允许保持粗糙。"],
     "加反馈（短震动、粒子、音效、数字弹跳）、修 UI 间距与字号、键位与无障碍、加载与存档体验。",
     "你自己连玩 30 分钟不烦；新人 5 分钟内不会卡住。",
     "两种相反的死法：无限打磨，或者一点不磨直接发。前者更常见。"),

    ("3.7　P6　测试与平衡", "1–2 周（可与 P5 并行）",
     "拿到你没想到的行为数据。注意是行为，不是意见。",
     ["这次测试要回答哪些问题。不是「好不好玩」，而是「他们卡在哪、死在哪、在哪停下来」。",
      "测几个人、找谁测。"],
     "埋本地日志、记录每关的失败次数与停留时长、把数据汇总成表；也可以让它写一份观察记录模板供你填。",
     "10 个陌生人（不是朋友），你能列出 3 条完全没预料到的观察。",
     "只测熟人，并且只问「好玩吗」。你会得到礼貌的废话，然后带着错误的信心发布。"),
    ("3.8　P7　发布准备", "1–2 周",
     "一个陌生人能在页面上看懂这是什么游戏，并且当场能玩到或买到。",
     ["定价、平台、上线时间。",
      "文案里承诺什么——承诺什么，就会被按什么标准评价。"],
     "截图裁切与排版、封面图、商店页多语言、构建打包、把网页版部署到静态托管。",
     "把商店页给一个没听过这游戏的人看 30 秒，他能说出「这是什么类型、大概多少钱」。",
     "上线前三天才做页面。那时 wishlist 是 0，首发流量等于没有。"),

    ("3.9　P8　上线之后", "持续",
     "把「这一款的经验」变成「下一款的能力」。这是唯一能让第二款变快的东西。",
     ["修什么、不修什么、什么时候停。",
      "哪些反馈属于「我的设计没传达清楚」，哪些属于「玩家不是我的目标人群」。"],
     "修 bug、写补丁说明、把零散反馈归类、起草回复模板。",
     "发布后两到四周，你能写下「下一款我会改的三件事」，并且每件事都指得向具体证据。",
     "上线即弃坑（拿不到经验），或者无限修（拿不到下一款）。两者都让这款游戏白做了。"),
]

for title, duration, goal, yours, ai, done, death in STAGES:
    h2(doc, title)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run("约为 " + duration), 9, False, MUTED)
    para(doc, "**这一步要达到**：" + goal, space_after=3)
    para(doc, "**只有你能定**：", space_after=2)
    for y in yours:
        para(doc, y, bullet=True, space_after=1)
    para(doc, "**AI 能替你做**：" + ai, space_after=3, space_before=2)
    para(doc, "**算过了的标准**：" + done, space_after=3)
    para(doc, "**常见死法**：" + death, color=GREY, space_after=6)

# ------------------------------------------------------------------ 四
h1(doc, "Vibe Coding 的分工", "四")

para(doc, "「Vibe Coding」在游戏制作里的意思不是「让 AI 随便写」，而是**你负责意图与验收，AI 负责实现与穷举**。分工不清时，最先崩的不是代码，是你的设计。")

h2(doc, "4.1　决策权随阶段迁移")
para(doc, "下图是九个阶段里「你」与「AI」的注意力分配示意：越往后，执行越可以外包；但「什么算够了」「这个感觉对不对」始终在你手上。")
figure(doc, "fig2-authority.png", "图 2　九个阶段的决策与执行分配（示意，非测量值）", 16.0)
note(doc, "【经验判断】AI 会把你没说清的地方**替你快快地定死**。所以效率提升只发生在「你已经想清楚」的部分；你没想清楚的地方，它加速的是走错路的速度。")

h2(doc, "4.2　规格怎么写才不塌")
para(doc, "一条能用的规格有三个特征：描述**可观察的行为**、**一次只改一件事**、**包含不要做什么**。", keep_with_next=True)
add_table(
    doc,
    ["要避免的写法", "可执行的说法"],
    [
        ["「把跳跃手感调好一点」", "「起跳上升比下落慢 20%，落地后 0.1 秒内不能再跳」"],
        ["「加一个敌人」", "「一种敌人：沿直线来回走，碰到玩家扣 1 心，被打两次消失」"],
        ["「做个好看的开始界面」", "「开始界面只有三行：标题、开始、退出；按方向键切换，回车确认」"],
        ["「优化一下 UI」", "「主菜单按钮高度从 40 加到 56 像素，间距 16 像素，字号 20」"],
    ],
    [7.4, 8.6], size=9,
    caption="表 2　模糊说法与可执行说法的对照：右侧每一条都能被「看一眼」验收",
)
para(doc, "另外三条经验，来自踩过的坑：", space_before=2)
para(doc, "**用参照物代替形容词。**「像《蔚蓝》的空中微调，但弱一半」比「手感要飘一点」有效十倍。", bullet=True)
para(doc, "**把「不要做什么」写进规格。**否则它会顺手加存档、加音效、加设置菜单——这些都不在你这一步的验收范围内。", bullet=True)
para(doc, "**改之前先存一版。**一次只让它改一件事，改坏了能立刻退回去。没有版本控制时，这条几乎无法执行。", bullet=True)

h2(doc, "4.3　验收：预测一致率")
para(doc, "【建议】每次让 AI 动手之前，先写下你预期会发生什么——三行就够：会看到什么、不会看到什么、边界情况怎么表现。改完逐条对照。")
para(doc, "一致率高，说明你在指挥施工队；一致率低，只有两种可能：**规格没写清**，或者**你根本没验收**。这个指标比「学了多少」准得多，因为它测的是「你能不能预见结果」——那正是制作人的核心能力。")

h2(doc, "4.4　上下文怎么给")
for s in ["让它先读项目里的实际文件，再回答。凭记忆报的 API 经常和你装的版本对不上。",
          "报错贴原文，不要转述。转述会丢掉最关键的那一行。",
          "版本号写清楚：引擎版本决定 API，这一点 AI 不会主动问。",
          "一次对话只处理一个任务，做完开新对话。上下文越长，它越容易滑回「通用做法」。"]:
    para(doc, s, bullet=True)

h2(doc, "4.5　AI 的真实边界")
para(doc, "【经验判断】它擅长的事：同构扩写、样板代码、重构、解释报错、查 API、批量生成与格式转换、写测试。")
para(doc, "它不擅长的事：判断好不好玩；跨文件的长期一致性；你没写下来的隐含约束；对一个已经长大的项目做大改。最后一条最危险——项目越大，它的修改越像「重写」。")
para(doc, "**推论**：把它的产出限制在你能验收的范围内。它一次做十件事、你只能验收三件，那剩下七件就是它在替你决策——通常你事后才会发现。")

h2(doc, "4.6　三条红线")
para(doc, "下面三句话，说出口就等于把制作人的位置让出去：")
for s in ["「你觉得怎么改更好玩？」", "「帮我随便设计一下数值 / 关卡 / 剧情。」", "「你看着办吧。」"]:
    para(doc, s, bullet=True, color=RGBColor(0xB0, 0x4A, 0x4A))

# ------------------------------------------------------------------ 五
h1(doc, "能力地图", "五")

para(doc, "制作人的能力不是均匀的。下面这张雷达图把八项能力分成两条线：第一款游戏「够用」的线，和想长期做下去的水平线。")
figure(doc, "fig3-skill-radar.png", "图 3　八项能力的两条参考线（我的建议，非测评标准）", 14.2)

para(doc, "三个档位，投入策略完全不同：", space_before=2, keep_with_next=True)
add_table(
    doc,
    ["档位", "包含", "投入方式"],
    [
        ["必须能判断", "玩法设计、规格表达、验收判断", "持续投入。判断错了，执行越快越糟。"],
        ["能操作即可", "引擎基础、版本控制、构建发布", "够用就停，卡住再查。不要系统学。"],
        ["可外包或用工具", "美术、音频、本地化、营销", "第一款不必精通，但必须能验收别人的产出。"],
    ],
    [3.2, 6.0, 6.8], size=9,
    caption="表 3　能力三档：只有第一档值得你花固定时间",
)

para(doc, "至于先学哪个，下面这张图给的是排序依据，不是命令。横轴是「对第一款能不能做完的影响」，纵轴是「学习成本」。", space_before=4)
figure(doc, "fig4-priority.png", "图 4　能力的学习优先级：右下先学，左上先不学", 15.6)
para(doc, "读法很直接：**右下角是划算的**（影响大、成本低），左上角是不划算的（影响小、成本高）。规格表达、验收判断、玩法设计落在右侧；架构设计、Shader、联机、3D、C# 深学落在左上——它们不是没用，是在第一款作品里性价比最低。")
para(doc, "【建议】先补判断类，再补操作类，深度类第一款完全不碰。判断力是复利的，操作技能会过时。")

# ------------------------------------------------------------------ 六
h1(doc, "时间与节奏", "六")

para(doc, "每周 5 小时的最大问题不是总量，是**连续性**。同样 260 小时，摊在 52 周里能做完一款，摊在 3 个断掉的季度里大概率弃坑。")
figure(doc, "fig5-curve.png", "图 5　两条路径的能力曲线：同样的时间，差距来自是否在交付", 15.4)

h2(doc, "6.1　每周五小时怎么切")
add_table(
    doc,
    ["时长", "干什么", "谁来做"],
    [
        ["30 分钟", "定本周唯一目标，写成一句可验收的话", "你"],
        ["60–90 分钟", "写本周要实现的行为规格：输入、可见结果、边界", "你"],
        ["2–2.5 小时", "施工与验收来回，通常三到五个回合", "AI 做，你判"],
        ["30 分钟", "提交一版，写三行日志：做到哪、卡在哪、下周从哪开始", "你"],
    ],
    [3.0, 9.0, 4.0], size=9,
    caption="表 4　每周 5 小时的固定切法：写规格的时间不能省，那是你唯一不可外包的部分",
)
para(doc, "那三行日志是给「下周的你」和「下周的 AI」准备的上下文。断档一周，前 20 分钟都在恢复记忆；断档两周，很多人的实际选择是再也不打开。")

h2(doc, "6.2　最小闭环")
para(doc, "如果不想先花一年，可以先走一遍压缩版：把内容量压到最小，但九个阶段一个不少。目的是拿到「完整走过一遍」的经验，而不是做出代表作。", keep_with_next=True)
add_table(
    doc,
    ["目标", "过关标准"],
    [
        ["P0 + P1：约束与一页纸概念", "能三句话说清给谁玩、玩多久；陌生人能复述循环"],
        ["P2：可玩原型", "你自己愿意连玩 5 分钟，并说得出哪里不对"],
        ["P3：纵向切片", "3 个陌生人看完主动问「完整的什么时候有」"],
        ["P4：最小内容量产", "从头到尾能通关，无阻断 bug"],
        ["P5 + P6：打磨与测试", "10 个陌生人测完，你有 3 条没预料到的观察"],
        ["P7：发布到 itch.io", "陌生人打开链接就能玩，页面看得懂"],
    ],
    [9.4, 6.6], size=9,
    caption="表 5　最小闭环：内容量压到最小，阶段一个不省",
)
para(doc, "【建议】首款目标定在 1–3 小时内容、单平台、免费或 2–5 美元。目的不是收入，是把整条流程走通、拿到真实反馈，并留下一个能复用的方法。")

# ------------------------------------------------------------------ 七
h1(doc, "工具链", "七")

para(doc, "工具的选择几乎不影响「能不能做完」；**引入的时机**才影响。下表按环节列出最小可用方案，以及什么阶段才值得升级。", keep_with_next=True)
add_table(
    doc,
    ["环节", "最小可用", "什么时候升级", "升级成什么"],
    [
        ["引擎", "Godot 4（免费、开源、2D 强、脚本轻）", "遇到明确瓶颈时", "Unity / 虚幻 / 自研网页框架"],
        ["版本控制", "本地 git 仓库，一天一提交", "需要备份与多机时", "GitHub 私有库"],
        ["任务与记录", "项目里一个 .scratch/ 目录 + 纯文本", "条目超过三十个", "看板工具"],
        ["美术", "占位色块 → Aseprite / Krita", "P3 需要正式资源时", "外包，或 AI 生成后手工修"],
        ["音频", "免费音效库 + bfxr 生成音", "需要统一听感时", "委托作曲"],
        ["构建发布", "引擎自带导出 + itch.io 网页上传", "要上 Steam 时", "butler 命令行 / Steamworks"],
        ["数据", "本地日志 + 一张汇总表", "需要看留存时", "分析平台"],
    ],
    [2.4, 6.2, 3.4, 4.0], size=8.5, keep_together=False,
    caption="表 6　工具链：先把「最小可用」用起来，不要在 P0 阶段选工具选两周",
)
para(doc, "【事实】itch.io 上架免费、无审核，网页版可以直接在页面里玩，适合第一次发布；Steam 收 100 美元上架费、有审核流程，且商店页必须在上线前就存在。所以第一次发布优先 itch.io，几乎不需要犹豫。")

# ------------------------------------------------------------------ 八
h1(doc, "风险与对策", "八")

para(doc, "下面九条是这类项目最常见的死法，按「发生概率 × 后果严重度」排序。前三条几乎能解释大多数弃坑。")
figure(doc, "fig6-risks.png", "图 6　九种死法的相对严重度（5 小时/周、首款作品情境）", 15.0)

h2(doc, "8.1　每条死法的挡板")
RIES = [
    ("断档两周以上", "固定每周同一时间开工；收工前写三行日志；下次开工先读日志再动手。"),
    ("首款规模超过收尾能力", "首款砍到 1–3 小时；任何「再加一个系统」的想法写进下一版清单，不进当前版本。"),
    ("让 AI 替你定玩法与数值", "写规格之前，先自己回答「这一步要证明什么」。答不出来就说明还没准备好开工。"),
    ("没有完工定义，无限打磨", "P5 开始前写下「够了」的三条标准，贴在能看见的地方。"),
    ("先花三个月系统学编程", "按需学：卡住哪查哪。系统学习的最大成本不是时间，是它推迟了你第一次真实交付。"),
    ("核心循环没验证就量产", "P2 的过关标准不允许跳过。原型不好玩，量产只会放大问题。"),
    ("上线前才做商店页", "P3 就开始攒截图与素材；商店页先上线，用来积累 wishlist。"),
    ("只找朋友测", "找陌生人；问「你刚才想做什么」，不问「好玩吗」。行为比评价可靠。"),
    ("一边加内容一边改机制", "P4 冻结机制，只允许改数值与内容。机制改动一律排到 v2。"),
]
for i, (name, fix) in enumerate(RIES, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.left_indent = Pt(21)
    p.paragraph_format.first_line_indent = Pt(-21)
    p.paragraph_format.line_spacing = 1.45
    set_run(p.add_run(f"{i:02d}　"), 10, True, TEAL)
    set_run(p.add_run(name + "　"), 10, True, NAVY)
    set_run(p.add_run(fix), 10, False, RGBColor(0x33, 0x3B, 0x45))

# ------------------------------------------------------------------ 九
doc.add_page_break()
h1(doc, "附录：术语表", "九")

para(doc, "游戏制作里有一批词，中文语境经常混着用。这几个在本文里反复出现，先把定义对齐，后面的讨论才不跑偏。", keep_with_next=True)
add_table(
    doc,
    ["词", "一句话解释", "为什么对你重要"],
    [
        ["核心循环 Core Loop", "玩家反复执行的那组动作，以及它带来的反馈", "循环不成立，后面所有内容都是装饰"],
        ["原型 Prototype", "只为验证一个假设而做的最糙版本", "它的价值在结论，不在能玩"],
        ["纵向切片 Vertical Slice", "一小段达到成品品质的体验", "用来证明「打磨之后成不成立」，也是宣传素材"],
        ["本体感 Game Feel / Juice", "打击、震动、音效、缓动等反馈的总和", "同样的机制，手感不同，评价差一倍"],
        ["Scope 范围", "这个项目实际要做多少内容", "首款失败的第一原因永远是 scope 失控"],
        ["Polish 打磨", "让已有内容更顺、更清晰、更少摩擦", "必须有限度，否则永远做不完"],
        ["Playtest 试玩测试", "让目标玩家玩，观察行为而非收集意见", "你自己测不出「新人会在哪卡住」"],
        ["Wishlist 愿望单", "玩家把游戏加入关注、等发售", "小型独立游戏最重要的上线前指标"],
        ["Build 构建", "一个可运行的、能交给别人玩的版本", "P0 阶段就要打通一次，别等到最后"],
        ["占位资源 Placeholder", "临时顶替正式美术/音效的丑素材", "刻意用丑的，能防止你在原型期做美术"],
        ["Early Access", "以未完成状态先发售、边做边改", "第一款不建议；它会把「收尾」变成无限期"],
        ["Capsule 图", "商店列表里那张主视觉图", "它决定有没有人点进你的页面"],
    ],
    [4.2, 6.4, 5.4], size=8.5,
    caption="表 7　术语表：这批词在本文里都按此定义使用",
)

doc.add_paragraph()
note(doc, "**下一步不是读第二遍**，而是新建一个空文件，写下三句话：给谁玩、玩多久、为什么是你做。写不出来，说明你还在 P0，不在 P1——这一步 AI 帮不了你，它只会给你一个看起来很完整的假答案。")

doc.save(OUT)
print("saved:", OUT)
print("paragraphs:", len(doc.paragraphs), "tables:", len(doc.tables))
