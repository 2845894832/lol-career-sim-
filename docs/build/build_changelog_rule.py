# -*- coding: utf-8 -*-
"""docs/更新日志维护规则.docx —— 一页规则：每次更新版本，同时更新日志。

内容源：AGENTS.md「更新日志（硬规矩）」、docs/CHANGELOG-维护规则.md、docs/build/build_6_4.py。
改规则时三处一起改：本脚本、CHANGELOG-维护规则.md、AGENTS.md。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

OUT = os.path.join(ROOT, "docs", "更新日志维护规则.docx")


def main():
    doc = k.new_doc("更新日志维护规则 · v0.1 · 2026-11-05")
    k.title(
        doc,
        "更新日志维护规则",
        "一条硬规矩 · 四条执行规则 · 发版三步 · v0.1 · 2026-11-05",
    )
    k.note(
        doc,
        "**每次更新版本，同时更新日志。** 日志没写，不算发完。"
        "这份是给人看的规则页；实际记录在 `CHANGELOG.md`，详细版在 `docs/6.4-更新日志.docx`。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "一条硬规矩")
    k.para(
        doc,
        "改 `package.json` 的 version、投稿、打 tag，都算「更新版本」。"
        "同一次操作里必须把日志落下来：新条目、日期、「影响谁」，一个都不能少。",
    )
    k.para(
        doc,
        "**怎么判断漏没漏**：翻开 `CHANGELOG.md`，最新一条还停在 `[Unreleased]` 而版本已经发出去了，就是漏了。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "四条执行规则")
    k.table(
        doc,
        ["问题", "答案"],
        [
            ["谁写", "AI 每次改完只说一句「这版要不要记、记什么」；条目与版本号由你拍板，AI 不替你定"],
            ["什么时候", "发版当天。平时改动先挂在 `CHANGELOG.md` 的 `[Unreleased]` 下，没发版的不写版本号"],
            ["写进哪", "`CHANGELOG.md` 写一版一行的对外摘要；详细说明、已知未修表、存档对照写 `docs/6.4-更新日志.docx`；版本条目冲突时以 `CHANGELOG.md` 为准"],
            ["格式三条", "①一条一句，只写玩家看得见的变化，不写内部重构；②必带「影响谁」（全体 / 已存档玩家 / 切片版玩家）与「重跑什么」；③版本号与 `package.json` 对齐"],
        ],
        [3.2, 12.8],
        size=9,
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "发版三步（照做，5 分钟）")
    k.table(
        doc,
        ["#", "动作", "做完的样子"],
        [
            ["1", "改 `package.json` 的 version", "版本号与即将写进 CHANGELOG 的一致"],
            ["2", "把 `[Unreleased]` 改成 `## [x.y.z] - YYYY-MM-DD`", "顶部再新开一个空的 `[Unreleased]`，下一条有地方放"],
            ["3", "详细说明补进 6.4：影响谁 / 重跑什么 / 已知未修", "重跑 `docs/build/build_6_4.py` 重新生成 docx"],
        ],
        [0.9, 7.3, 7.8],
        size=9,
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "文件在哪")
    k.table(
        doc,
        ["文件", "作用"],
        [
            ["`CHANGELOG.md`（仓库根）", "一版一行摘要：给仓库、agent 和想快速回看的人"],
            ["`docs/6.4-更新日志.docx`", "详细说明、已知未修表、存档版本对照：给人读"],
            ["`docs/CHANGELOG-维护规则.md`", "规则源文件，本文档与它同源"],
            ["`docs/build/build_6_4.py`", "6.4 的生成脚本；改内容必须重跑"],
            ["`docs/build/build_changelog_rule.py`", "本文档的生成脚本"],
            ["`AGENTS.md` 的「更新日志（硬规矩）」", "项目记忆：每次加载都提醒 AI 与你自己"],
        ],
        [7.6, 8.4],
        size=9,
    )

    k.note(
        doc,
        "版本号规则：发一版 `+0.1.0`，只修 bug `+0.0.1`，首发 `1.0.0`。"
        "存档结构变了才动 `CONFIG.version`——它和发型号不是一回事。",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
