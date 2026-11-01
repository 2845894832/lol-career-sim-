# -*- coding: utf-8 -*-
"""P0/P1/P2 文档共用的 DOCX 组件（从 build_p1.py 抽出，避免脚本之间互相 import 触发构建）。"""
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(sz))
    e.set(qn("w:space"), "4")
    e.set(qn("w:color"), color)
    b.append(e)
    pPr.append(b)


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
    e.set(qn("w:val"), "clear")
    e.set(qn("w:color"), "auto")
    e.set(qn("w:fill"), v)
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
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "6")
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "CDD8E3")
        bd.append(e)
    tblPr.append(bd)
    mar = OxmlElement("w:tblCellMar")
    for tag, v in (("top", 50), ("left", 100), ("bottom", 50), ("right", 100)):
        e = OxmlElement(f"w:{tag}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
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
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "2F6FA8")
        bd.append(e)
    tblPr.append(bd)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.35
    rich(p, s, 9.5, RGBColor(0x33, 0x3B, 0x45))
    if spacer:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figure(doc, path, cap, w):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(w))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(12)
    set_run(c.add_run(cap), 9, False, M)


def new_doc(header_text):
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
    set_run(hp.add_run(header_text), 8.5, False, M)
    border(hp, "DCE4EC", 4)
    return doc


def title(doc, main, sub):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run(main), 24, True, N)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run(sub), 9.5, False, M)
    border(p, "C9D6E3", 8)
