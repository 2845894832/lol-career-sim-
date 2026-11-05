# -*- coding: utf-8 -*-
"""4.4 决策记录：只生成索引 docx。

2026-11-05 改：**不再从内置文案重写 `docs/adr/*.md`**。
旧版会把 12 条 ADR 从脚本里的 ADRS 列表整份覆盖，2026-11-05 加进去的
`- 出处：` 行、`> 出处未确认` 与「## 依据」会被静默抹掉。
现在 markdown 是唯一信源，本脚本只读它们、拼一份索引 docx。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

ADR_DIR = os.path.join(ROOT, "docs", "adr")


def load_adrs():
    out = []
    for path in sorted(glob.glob(os.path.join(ADR_DIR, "*.md"))):
        text = open(path, encoding="utf-8").read()
        head = text.splitlines()[0].lstrip("# ").strip()
        num, _, title = head.partition(" · ")

        def field(name):
            m = re.search(r"^- %s：(.*)$" % name, text, re.M)
            return m.group(1).strip() if m else ""

        cons = ""
        m = re.search(r"^## 后果\n\n(.+?)$", text, re.M)
        if m:
            cons = m.group(1).strip().split("。")[0] + "。"

        out.append(
            dict(
                num=num,
                title=title,
                status=field("状态"),
                prov=field("出处"),
                cons=cons,
                file=os.path.basename(path),
                unconfirmed="> 出处未确认" in text,
            )
        )
    return out


def main():
    adrs = load_adrs()
    ok = [a for a in adrs if not a["unconfirmed"]]
    todo = [a for a in adrs if a["unconfirmed"]]

    doc = k.new_doc("4.4 决策记录 · v0.2 · 2026-11-05")
    k.title(
        doc,
        "电竞选手模拟器 · 决策记录",
        "12 条回填 ADR + 索引 · v0.2 · 2026-11-05",
    )
    k.note(
        doc,
        f"正文是 `docs/adr/` 下的 {len(adrs)} 个 markdown 文件（每条一个文件，改一条动一个文件）。"
        "这份 docx 只是索引，由 `docs/build/build_4_4.py` **只读**那些文件生成。"
        "写法与出处要求见 `docs/决策记录规则.md`。",
    )

    k.h1(doc, "一", "12 条一览")
    k.table(
        doc,
        ["#", "决定", "状态", "一句话后果"],
        [[a["num"], a["title"], a["status"], a["cons"]] for a in adrs],
        [1.2, 6.4, 1.8, 6.6],
        size=8,
    )

    k.h1(doc, "二", "哪些有出处，哪些还没有")
    k.para(
        doc,
        "核对口径：`docs/adr/*.md` 里的 `- 出处：` 行。有出处的指到用户原话（含日期与轮次）；"
        "指不到的，文件头有 `> 出处未确认`，文末有「依据」。**这一节的判断由 AI 做出，"
        "2026-11-05 经用户认可 8 条「有出处」，其余 4 条仍是待确认。**",
        size=10,
    )
    k.table(
        doc,
        ["结论", "条数", "编号"],
        [
            ["有出处", f"{len(ok)} 条", "、".join(a["num"] for a in ok)],
            ["**待确认**", f"{len(todo)} 条", "、".join(a["num"] for a in todo)],
        ],
        [2.6, 2.4, 11.0],
        size=9,
        caption="表 2-1　待确认的 4 条：0012 只有「战绩卡四行」有原话；0008 用户 11-05 明确否认；0001 是平台约束；0010 是实现选择",
    )

    k.h1(doc, "三", "还没成为 ADR 的 3 件事（先记着）")
    k.table(
        doc,
        ["事", "为什么还没定"],
        [
            ["荣誉四种（MSI/MVP/最佳阵容/名人堂）要不要接", "代码里从没写入过；接了会改奖励结构，等用户拍板"],
            ["健身速通漏洞要不要压", "三个修法各有代价；只有用户能选"],
            ["数值表 → 代码 的 gen:config", "方向已认可（3.2），但还没做；做完才谈「单一数值源」"],
        ],
        [7.0, 9.0],
        size=9,
    )

    k.h1(doc, "四", "怎么写下一条 ADR")
    k.table(
        doc,
        ["步", "做什么"],
        [
            ["1", "先找出处：用户哪天哪一句点头，或哪张 ticket"],
            ["2", "复制任意一个 `docs/adr/00XX-*.md`，编号 +1"],
            ["3", "标题写「决定了什么」，不写「关于…」；必带 决定 / 日期 / 出处 / 待确认项"],
            ["4", "替代方案至少写一个，并写清**为什么没选它**"],
            ["5", "证据必须是能查的东西：提交号、文件行、模拟结果"],
            ["6", "用户没点头的：头部 `> 出处未确认`，状态 `待确认`，不许写成已定"],
        ],
        [1.4, 14.6],
        size=9,
    )

    out = os.path.join(ROOT, "docs", "4.4-决策记录.docx")
    doc.save(out)
    print("saved", out, "adrs", len(adrs), "unconfirmed", [a["num"] for a in todo])


if __name__ == "__main__":
    main()
