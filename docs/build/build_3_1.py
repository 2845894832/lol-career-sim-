# -*- coding: utf-8 -*-
"""docs/3.1-技术方案.docx —— 按 game-docs-and-sheets-inventory.md 3.1 写。

清单要求：技术栈 / 模块划分 / 数据结构 / 依赖与版本锁定 / 已知技术风险。
事实来源：package.json、vite.config.ts、src/ 目录、dist 产物大小。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

OUT = os.path.join(ROOT, "docs", "3.1-技术方案.docx")


def main():
    doc = k.new_doc("3.1 技术方案 / 架构 · v0.1 · 2026-11-04")
    k.title(
        doc,
        "电竞选手模拟器 · 技术方案",
        "架构 · 模块划分 · 数据结构 · 依赖 · 风险 · v0.1 · 2026-11-04",
    )

    k.note(
        doc,
        "约束只有一条，但它决定了后面所有选择：**平台只收一个 index.html**——JS 与 CSS 全部内联，零外链、零后端。"
        "所以没有框架、没有路由、没有运行时依赖。事实来源：`package.json`、`vite.config.ts`、`src/` 目录、`dist/` 产物。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "技术栈")
    k.table(
        doc,
        ["项", "选择", "理由"],
        [
            ["语言", "TypeScript 5.9（strict）", "规则都在纯函数里，类型能挡住大部分低级错"],
            ["构建", "Vite 7.1 + vite-plugin-singlefile 2.3", "一个插件就把 JS/CSS 内联进单个 HTML"],
            ["框架", "无（原生 DOM + 模板字符串）", "6 屏、一个状态对象，框架只会增加 89KB 的十分之一"],
            ["运行环境", "手机浏览器 / 平台 webview，ES2020", "目标 es2020：可选链与 ?? 都能用，又不必降级到 ES5"],
            ["后端", "无", "不需要账号、不需要存档同步"],
            ["部署", "上传单个 `dist/index.html` 到平台", "平台要求；产物 88.5 KB（切片版 89.3 KB）"],
            ["测试", "Vitest 3.2（node 环境）", "61 个用例，测的是 core 的纯函数，不测 DOM"],
        ],
        [2.4, 6.4, 7.2],
        size=9,
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "模块划分（一处逻辑只在一个地方）")
    k.table(
        doc,
        ["层", "文件", "负责什么", "不许做什么"],
        [
            ["类型", "src/types.ts", "GameState、事件、动作、结局的全部接口", "不写逻辑、不写数值"],
            ["数值", "src/config.ts", "**唯一数值源**：所有参数与占位注释", "不写规则判断"],
            ["随机", "src/rng.ts", "可复现的伪随机（种子存进状态）", "不用 Math.random"],
            ["核心", "src/core/*.ts（10 个）", "纯函数规则：reduce 是唯一入口", "不碰 DOM、不碰 localStorage"],
            ["数据", "src/data/*.ts（4 个）", "事件库、S8–S15 队伍名单、决赛、行动反馈文案", "不含判断逻辑"],
            ["存档", "src/core/save.ts", "序列化、版本校验、读写 localStorage", "不含规则"],
            ["界面", "src/ui/main.ts + style.css", "渲染模板、事件绑定、页签切换", "不写规则、不写数值"],
            ["脚本", "scripts/*.mjs / *.ts", "截图、批量模拟、构建切片、发布校验", "不参与运行时"],
        ],
        [1.6, 4.6, 6.4, 4.0],
        size=8.5,
        caption="表 2-1　core 里的 10 个文件：actions / endings / events / growth / ladder / league / match / reduce / save / shop / state",
    )
    k.para(
        doc,
        "**单向数据流**：界面发一个 Action → `reduce(state, action)` 返回新状态与日志 → 界面整体重渲染 → 存一次档。"
        "界面不持有自己的游戏状态，也不做任何判定。",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "数据流")
    k.table(
        doc,
        ["步", "谁做", "做什么"],
        [
            ["1", "ui/main.ts", "点击 → 拼一个 Action 对象（selectAction / endWeek / chooseOption / retire / skipYear）"],
            ["2", "core/reduce.ts", "校验能不能做 → 调对应逻辑 → 返回新状态 + 日志"],
            ["3", "core/save.ts", "把新状态写进 localStorage（临时字段 temp 不存）"],
            ["4", "ui/main.ts", "用新状态整体重渲染（innerHTML 模板 + 重新绑定事件）"],
        ],
        [1.2, 4.4, 10.6],
        size=9,
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "核心数据结构")
    k.table(
        doc,
        ["分组", "字段（节选）", "说明"],
        [
            ["身份", "name, role, seed, year, week", "种子进存档，保证读档后走势不变"],
            ["六维", "attrs: operation/laning/teamfight/awareness/mentality/popularity", "0–100 整数"],
            ["资源", "stamina, maxStamina, money, coachTrust, injury, rankPoints, placement", "体力不自动回；排名由分数与周数推出来"],
            ["本周", "actionGrid[3], actionTargets[3], pendingEvent, eventDone", "pendingEvent 非空时锁全部操作"],
            ["生涯", "signed, teamId, freeAgent, failedWindows, honors[], flags[], yearGain", "flags 用于结局尾注"],
            ["记录", "seasonResults[], log[]（最多 60 条）, ledger, lastLedger", "日志不进存档"],
            ["结局", "ended, retired, peakScore, peakYear", "ended 一置位，所有操作被拒"],
            ["随机", "rngState", "每次抽签后写回，保证可复现"],
        ],
        [2.2, 9.4, 5.0],
        size=8.5,
        caption="表 4-1　共 39 个字段，与 3.2 数据模型文档一一对应",
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "第三方依赖与版本锁定")
    k.table(
        doc,
        ["依赖", "版本", "用途", "进产物吗"],
        [
            ["typescript", "^5.9.3", "类型检查与编译", "否"],
            ["vite", "^7.1.7", "构建与开发服务器", "否"],
            ["vite-plugin-singlefile", "^2.3.0", "把 JS/CSS 内联进 index.html", "否"],
            ["vitest", "^3.2.4", "单元测试", "否"],
            ["puppeteer-core", "^25.13.0", "截图脚本（用本机 Edge，不下载 Chromium）", "否"],
        ],
        [5.0, 3.0, 7.4, 3.0],
        size=9,
        caption="表 5-1　**运行时依赖 0 个**；产物里没有任何第三方代码或外链",
    )
    k.para(
        doc,
        "版本锁定靠 `package-lock.json`；升级前先跑 `npm test` 与 `npm run smoke`。许可：五者均为 MIT 或 Apache-2.0，"
        "且都不进产物，不涉及分发义务。",
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "命令")
    k.table(
        doc,
        ["命令", "做什么", "产物"],
        [
            ["npm run dev", "开发服务器（热更新）", "—"],
            ["npm run build", "类型检查 + 打包完整版", "dist/index.html（88.5 KB）"],
            ["npm run build:slice", "打包切片版（第 8 周收尾）", "dist-slice/index.html（89.3 KB）"],
            ["npm test", "61 个单测", "—"],
            ["npm run smoke", "22 项冒烟（真浏览器走一遍主流程）", "—"],
            ["npm run batch", "1000 局批量模拟，看数值分布", "—"],
        ],
        [4.0, 8.4, 6.8],
        size=9,
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "已知技术风险")
    k.table(
        doc,
        ["#", "风险", "现在怎么应对", "触发后的后果"],
        [
            ["1", "平台 webview 兼容性未知", "目标 es2020、不用最新语法糖、不依赖系统字体之外的东西", "白屏（最严重）"],
            ["2", "单文件 89 KB，内容再涨会更大", "事件文本进包；一期上限 60 条", "首屏变慢"],
            ["3", "localStorage 在隐私模式/嵌入 webview 里可能被禁", "写入包在 try/catch，失败不阻塞游戏", "刷新丢档"],
            ["4", "没有构建产物校验之外的线上监控", "`scripts/check-pushed.mjs` 只验推送后的文件与断言", "线上 404 或白屏只能靠用户反馈"],
            ["5", "iOS 的 100dvh 与安全区差异", "用 dvh + env(safe-area-inset-*)；未真机验证", "底部按钮被遮"],
            ["6", "截图/冒烟依赖本机 Edge 路径", "puppeteer-core 指定可执行文件", "换机器脚本失效（不影响产物）"],
        ],
        [1.0, 5.6, 6.6, 4.2],
        size=8.5,
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "规模")
    k.table(
        doc,
        ["项", "数值", "说明"],
        [
            ["源码行数", "3,576 行", "src 全部；不含脚本与测试"],
            ["模块数", "core 10 + data 4 + ui 2 + 根 3", "config / types / rng 在根"],
            ["测试", "61 个用例，1 个文件", "只测 core"],
            ["产物", "88.5 KB 单文件", "零外链"],
            ["队伍数据", "S8–S15 八个赛季，每季 14–17 支队 × 5 人，每人有 ovr", "由 scripts/build_rosters.py 生成"],
        ],
        [3.0, 7.4, 8.6],
        size=9,
    )

    k.note(
        doc,
        "这份文档里没有一个待你拍板的设计项，都是现状。唯一需要你确认的是第七节第 1、5 条："
        "平台 webview 与 iOS 真机 —— 只能靠真机试一次，试之前它们都是「未知」。",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
