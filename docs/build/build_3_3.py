# -*- coding: utf-8 -*-
"""docs/3.3-构建与发布流程.docx —— 按 game-docs-and-sheets-inventory.md 3.3 写。

清单要求：本地怎么跑、怎么打包、发布步骤、回滚方法、版本号规则。
事实来源：package.json、vite.config.ts、scripts/build-slice.mjs、scripts/archive-dist.mjs、scripts/check-pushed.mjs、README.md、git remote。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

OUT = os.path.join(ROOT, "docs", "3.3-构建与发布流程.docx")


def main():
    doc = k.new_doc("3.3 构建与发布流程 · v0.1 · 2026-11-04")
    k.title(
        doc,
        "电竞选手模拟器 · 构建与发布",
        "本地运行 · 打包 · 投稿 · 回滚 · 版本号 · v0.1 · 2026-11-04",
    )

    k.note(
        doc,
        "发布目标：**虎扑 AI 工坊**，交一个 `index.html`。没有服务器、没有 CI、没有自动部署——"
        "全部是「本地构建 → 人工验 → 上传」。数据来源：package.json、vite.config.ts、scripts/、git remote。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "本地跑起来")
    k.table(
        doc,
        ["命令", "作用", "备注"],
        [
            ["npm install", "装依赖（5 个 devDependencies）", "本机 Node v24 验证过；没有 engines 限制"],
            ["npm run dev", "开发服务器，热更新", "改 CSS 与 TS 立刻可见"],
            ["npm run typecheck", "只做类型检查", "等价于 build 的前半段"],
            ["npm test", "61 个单测（Vitest，node 环境）", "只测 core，不测界面"],
            ["npm run smoke", "真浏览器（本机 Edge 无头）走一遍主流程", "需要 Edge 路径存在；截图落 shots/"],
            ["npm run batch", "1000 局批量模拟，看数值分布", "调参数时用"],
        ],
        [4.6, 8.0, 6.6],
        size=9,
    )
    k.para(
        doc,
        "**环境依赖**：Node 18+（本机 24）、本机 Edge（`C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`）。"
        "puppeteer-core 不下载 Chromium，只借用本机浏览器；换机器要改脚本里的路径。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "两种产物")
    k.table(
        doc,
        ["命令", "产物", "大小", "内容"],
        [
            ["npm run build", "dist/index.html", "88.5 KB", "八年完整版，`__SLICE_AT__ = 0`"],
            ["npm run build:slice", "dist-slice/index.html", "89.3 KB", "切片版，`__SLICE_AT__ = 8`，打到第 8 周收尾"],
        ],
        [4.2, 5.0, 2.6, 6.4],
        size=9,
    )
    k.para(
        doc,
        "两者代码完全相同，只差一个编译期常量。`vite-plugin-singlefile` 把 JS 与 CSS 全部内联，"
        "产物**零外链、零请求**——双击能开，断网能玩。",
    )
    k.para(
        doc,
        "**仓库里只放切片版**（`dist-slice/index.html`），完整版在本地构建、不进版本库。"
        "这样 clone 下来的人打开就是能玩的试吃装，也不会让仓库变大。",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "发布前检查（按顺序，全过才上传）")
    k.table(
        doc,
        ["#", "检查", "命令", "不通过的典型原因"],
        [
            ["1", "类型干净", "npm run typecheck", "临时删字段留下的 any"],
            ["2", "单测全过", "npm test", "改了数值公式没改断言"],
            ["3", "构建成功且体积未爆", "npm run build", "事件太多，包体超 150KB"],
            ["4", "冒烟过", "npm run smoke", "某屏选择器改了名"],
            ["5", "切片检查", "node scripts/check-slice.mjs", "第 8 周截断条件坏了"],
            ["6", "推送后校验（可选）", "node scripts/check-pushed.mjs <url>", "线上文件与本地不一致"],
        ],
        [1.0, 5.0, 6.4, 6.8],
        size=9,
        caption="表 3-1　第 1–5 步在本地就能跑完；第 6 步需要先把文件推上去或起一个本地服务器",
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "投稿到平台（阶段 6 的步骤）")
    k.table(
        doc,
        ["步", "做什么", "要点"],
        [
            ["1", "准备素材", "标题（≤20 字，带钩子不夸张）、简介（3 句内）、封面、2–3 张截图（手机比例）、标签"],
            ["2", "确认尺寸规则", "**先查平台当前的投稿规范再出图**，不要最后改图"],
            ["3", "上传 `index.html`", "单文件，直接交；不要交 zip 里的 dist 目录"],
            ["4", "提交审核", "通常 1–3 个工作日；审核期间不要改线上版本"],
            ["5", "上线后自查", "手机流量能开、控制台无报错、刷新不丢档、战绩卡能复制"],
            ["6", "发帖", "2–3 个标题备选 + 可玩链接 + 一句战绩卡示例"],
            ["7", "发布后 24 小时", "记打开数、完成率、评论高频词、报错"],
        ],
        [1.2, 6.2, 10.6],
        size=9,
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "回滚（发布坏了怎么退）")
    k.table(
        doc,
        ["情况", "动作", "耗时"],
        [
            ["代码改了但没发", "git revert 或 git checkout -- <file>，重新构建", "5 分钟"],
            ["发了新版本，发现白屏/报错", "从 `dist/archive/` 取上一版 `index-<时间戳>.html`，平台上重传", "10 分钟"],
            ["数值改坏了但版本已上线", "改回 config.ts → 重建 → 重传；**不要**在平台上打补丁", "20 分钟"],
            ["存档结构与旧版不兼容", "把 `CONFIG.version` +1（旧档自动作废），重新构建", "10 分钟"],
        ],
        [5.6, 9.4, 3.0],
        size=9,
        caption="表 5-1　回滚的前提是「本地永远留着上一版产物」——每次构建成功后先跑一次 `npm run build:archive`",
    )
    k.para(
        doc,
        "**归档怎么做**：`npm run build && npm run build:archive`，脚本只读 `dist/index.html`、"
        "复制成 `dist/archive/index-YYYYMMDD-HHmm.html`，不改原文件。`dist/*` 已被 `.gitignore` 忽略，"
        "归档不进版本库；换机器或清 `dist/` 会丢，重要版本另打 git tag。",
    )
    k.para(
        doc,
        "**当前状态：一次也没发布过。** 所以「回滚」这条只是预案，等第一次投稿后需要按实际情况修正。",
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "版本号规则")
    k.table(
        doc,
        ["位置", "当前值", "怎么动"],
        [
            ["`package.json` version", "0.1.0", "发型版本：每次投稿 +0.1.0，修 bug +0.0.1；首发改 1.0.0"],
            ["`CONFIG.version`（存档）", "3", "**只有存档结构变了才 +1**；旧档直接作废，不做迁移"],
            ["产物文件名", "index.html", "不带版本号（平台只收一个文件）"],
            ["git tag", "无", "建议每次投稿打 `v0.1.0` 之类的 tag，便于回滚"],
        ],
        [4.8, 3.4, 9.8],
        size=9,
    )
    k.para(
        doc,
        "两个版本号**不是一回事**：`package.json` 对外讲故事，`CONFIG.version` 管存档兼容。改结构不改发型版本，是允许的。",
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "已知风险与缺口")
    k.table(
        doc,
        ["#", "缺口", "后果"],
        [
            ["1", "没有 CI，全部手动", "漏跑一步就可能发出坏包"],
            ["2", "没有自动部署", "每次上传都要人工确认文件对不对"],
            ["3", "本机沙箱里 `git push` 失败（不能起 ssh 进程）", "推送只能你自己在终端做，本地已有多个未推提交"],
            ["4", "没有线上监控与埋点", "白屏只能靠用户反馈"],
            ["5", "更新日志靠人记（已补 `CHANGELOG.md`）", "发版当天忘了写，就只剩 git log 可查"],
            ["6", "产物归档只在本地（已加 `npm run build:archive`）", "换机器或清 `dist/` 就没了；重要版本另打 git tag"],
        ],
        [1.0, 8.4, 6.6],
        size=9,
    )

    k.note(
        doc,
        "下面三条是流程里唯一需要你动手的：①终端里自己 `git push`；②第一次投稿前把平台规范截图/贴给我，我按规范出素材；"
        "③每次构建成功后跑 `npm run build:archive`，把产物留一份在 `dist/archive/`。其余都可以做成脚本。",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
