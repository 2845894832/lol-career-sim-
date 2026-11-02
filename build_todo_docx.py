"""把 待处理.md 转成 待处理.docx（md 是源，docx 是给他看的版本）。"""
import io
import os
import re

import docx_kit as k

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "待处理.md")
OUT = os.path.join(HERE, "待处理.docx")

TOTAL_W = 16.0


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_table_sep(line):
    return re.fullmatch(r"\|[\s:|-]+\|", line.strip()) is not None


def plain(s):
    return s.replace("`", "")


def main():
    lines = io.open(SRC, encoding="utf-8").read().splitlines()

    doc = k.new_doc("待处理 · 上分（段位）的现状与改进")
    sub = ""
    i = 0
    if lines and lines[0].startswith("# "):
        main_title = lines[0][2:].strip()
        i = 1
    else:
        main_title = "待处理"

    # 找标题下的引用行当副标题
    j = i
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and lines[j].startswith(">"):
        sub = lines[j].lstrip("> ").strip()
        i = j + 1

    k.title(doc, main_title.split("：")[0], sub)

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s or s == "---":
            i += 1
            continue

        # 二级标题：## 一、xxx
        if s.startswith("## "):
            text = s[3:].strip()
            m = re.match(r"^([一二三四五六七八九十]+)、\s*(.+)$", text)
            if m:
                k.h1(doc, m.group(1), m.group(2))
            else:
                k.h1(doc, "·", text)
            i += 1
            continue

        # 三级标题：### 3.1 xxx
        if s.startswith("### "):
            k.h2(doc, s[4:].strip())
            i += 1
            continue

        # 表格
        if s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not is_table_sep(lines[i]):
                    block.append(split_row(lines[i]))
                i += 1
            if len(block) >= 2:
                head, rows = block[0], block[1:]
                n = len(head)
                w = round(TOTAL_W / n, 2)
                k.table(doc, head, rows, [w] * n, size=8.5)
            continue

        # 引用
        if s.startswith(">"):
            k.note(doc, plain(s.lstrip("> ").strip()))
            i += 1
            continue

        # 列表
        if s.startswith("- "):
            k.para(doc, plain(s[2:].strip()), bullet=True, after=3)
            i += 1
            continue

        k.para(doc, plain(s))
        i += 1

    doc.save(OUT)
    print("saved", OUT, "paragraphs", len(doc.paragraphs), "tables", len(doc.tables))


if __name__ == "__main__":
    main()
