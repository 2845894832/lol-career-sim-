# -*- coding: utf-8 -*-
"""笔记/13-14-一页图文-3张.docx —— 把三张一页图文抄成可搜索、可摘录的文档。

图的原件在 docs/13-14-一页图文/（1-三层.png / 2-三个词.png / 3-39个字段.png）。
文字与图一一对应，不改结论；只把图上的话落到文字，方便以后在笔记文件夹里翻。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

OUT = os.path.join(ROOT, "笔记", "13-14-一页图文-3张.docx")


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = k.new_doc("笔记 / 13-14 一页图文 · 2026-11-05")
    k.title(
        doc,
        "一页图文 · 3 张",
        "13 技术方案 / 14 数据模型 · 从图抄成文字版 · 2026-11-05",
    )
    k.note(
        doc,
        "这三段就是 `docs/13-14-一页图文/` 里三张图的内容，一字不改地抄下来，"
        "方便搜索和摘录。图是竖版 820×1160，手机上看得清；这里是可以选中复制的文字。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "这游戏，三层在干活")
    k.para(doc, "你看得见的只有第一层，另外两层在背后替它干活。")
    k.table(
        doc,
        ["层", "你看见什么", "改它等于", "代码在哪儿"],
        [
            ["界面层", "按钮、表格、红绿数字", "改长相和手感", "src/ui/main.ts"],
            ["规则层", "点「训练」之后算出来的数", "改玩法", "src/core/"],
            ["数据层", "看不见；存在浏览器里的 39 个字段", "改「能记什么」", "src/types.ts"],
        ],
        [2.6, 5.6, 4.2, 3.6],
        size=9,
        caption="表 1　三层各管一段：界面不改数字，规则不画界面，数据不带判断",
    )
    k.para(doc, "**在这游戏里：**", bullet=False)
    k.para(doc, "把「体力 60/100」换成一根进度条——只动界面层。", bullet=True)
    k.para(doc, "训练一次涨 1 点改成涨 2 点——整个难度就变了。", bullet=True)
    k.para(doc, "想多加一个「心情」——得先在数据层加一个字段。", bullet=True)
    k.note(
        doc,
        "打个饭馆的比方：**前厅点菜、后厨做菜、仓库记账**。"
        "三件事各归各的；串层，就是菜做好了却记错了库存。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "三个词，三句话")
    k.para(doc, "技术方案里翻来覆去的，其实只有这三个词。")

    k.h2(doc, "1　TypeScript —— 写错当场报错")
    k.para(doc, "给 JavaScript 加了「类型标签」：名字写错、单位用错，当场报错，不用等跑起来才发现。")
    k.para(doc, "比喻：寄快递先填单子，地址写错当场退回。代价：多一道编译。")
    k.para(doc, "在这游戏里：改 config.ts 写错字段名，编译就报错，不用等打开游戏。")

    k.h2(doc, "2　单文件打包（Vite）—— 装得下")
    k.para(doc, "把 src 下几十个源文件，压成一个 index.html（现在 88 KB），双击就能玩，不用装环境。")
    k.para(doc, "比喻：散装零件装成一台整机。代价：改完要重新打包。")
    k.para(doc, "在这游戏里：打包命令跑完，dist/index.html 就是能直接玩的成品。")

    k.h2(doc, "3　本地存档（localStorage）—— 存得住")
    k.para(doc, "浏览器给每个网站的一个小抽屉：关掉浏览器，抽屉里的东西还在。")
    k.para(doc, "比喻：关灯了，抽屉里的东西不会消失。代价：换浏览器或清缓存就没了。")
    k.para(doc, "在这游戏里：存档键叫 lpl-career-proto:v3，按 F12 就能看见。")

    k.note(doc, "三件事各管一段：**写不错 → 装得下 → 存得住**。记不住名字没关系，记住这三句就行。")

    # ---------------- 三 ----------------
    k.h1(doc, "三", "39 个字段，分三堆")
    k.para(doc, "整局游戏要记住的东西，只有这 39 个，按「你能不能看见」分。")
    k.table(
        doc,
        ["组", "个数", "一句人话"],
        [
            ["界面上看得见", "21", "你随时能查到的：他是谁、现在第几周"],
            ["藏在背后计数", "10", "界面不显示，但少了它，游戏会「记错」"],
            ["只属于本周", "8", "这一周过完就该清掉的临时状态"],
        ],
        [3.4, 1.8, 10.8],
        size=9,
        caption="表 2　21 + 10 + 8 = 39；存档时只少存一个 temp",
    )

    k.h2(doc, "看得见的那 21 个")
    k.para(
        doc,
        "playerName · role · year · week · attrs · stamina · maxStamina · money · rankPoints · "
        "placement · coachTrust · injury · honors · seasonResults · signed · teamId · freeAgent · "
        "owned · subs · ended · retired",
    )
    k.h2(doc, "藏在背后的 10 个")
    k.para(
        doc,
        "version · seed · rngState · exp · yearGain · flags · triggeredEvents · failedWindows · "
        "peakYear · peakScore",
    )
    k.h2(doc, "只属于本周的 8 个")
    k.para(
        doc,
        "actionGrid · actionTargets · pendingEvent · eventDone · ledger · lastLedger · temp · log",
    )
    k.note(
        doc,
        "存档时只少存一个 **temp**；其余 38 个都写进浏览器，其中 log 最多留 60 条。"
        "每个字段的类型 / 范围 / 默认值，在 docs/13-14-技术方案与数据模型-讲懂版.docx 的附录 A 里。",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
