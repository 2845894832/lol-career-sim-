# -*- coding: utf-8 -*-
"""docs/3.2-数据模型.docx —— 按 game-docs-and-sheets-inventory.md 3.2 写。

清单要求：每个表：字段名、类型、含义、取值范围、默认值、谁写入；
与 Excel 数值表的对应关系（源头方向必须明确）。
事实来源：src/types.ts（GameState 39 字段）、src/core/state.ts（newGame 默认值）、
src/core/shop.ts、src/data/*.ts、xlsx 文件清单。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import docx_kit as k

OUT = os.path.join(ROOT, "docs", "3.2-数据模型.docx")


def main():
    doc = k.new_doc("3.2 数据模型 / 表结构 · v0.1 · 2026-11-04")
    k.title(
        doc,
        "电竞选手模拟器 · 数据模型",
        "存档结构 · 静态数据 · 与 Excel 的对应关系 · v0.1 · 2026-11-04",
    )

    k.note(
        doc,
        "只有一个存档对象 `GameState`（39 个字段），另外四类静态数据（事件、队伍、商店、反馈文案）。"
        "**结构的权威是 `src/types.ts`**，默认值的权威是 `src/core/state.ts` 的 `newGame()`，本文只是把它们写成字。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "原则")
    k.table(
        doc,
        ["原则", "含义", "违反的后果"],
        [
            ["一个对象", "整个存档就是一个 GameState，不做多表关联", "拆表就要写迁移，单机游戏不值"],
            ["结构在代码里", "字段增删改以 types.ts 为准，文档同步", "文档与代码分叉，三个月后没人知道哪个对"],
            ["临场不进存档", "`temp` 与 `log` 序列化时被丢掉", "读档后残留上一场的加成"],
            ["算法不落盘", "名次、胜率、段位都由分数与周数算出，不存", "存了就会和算法版本打架"],
        ],
        [3.0, 8.6, 4.8],
        size=9,
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "GameState：身份与时间（7）")
    k.table(
        doc,
        ["字段", "类型", "范围/含义", "默认", "谁写"],
        [
            ["version", "number", "存档版本，当前 3", "3", "初始化"],
            ["seed", "number", "本局种子", "玩家选或随机", "初始化"],
            ["rngState", "number", "当前随机状态", "= seed", "每次抽随机数后推进"],
            ["playerName", "string", "角色名", "开局填", "初始化"],
            ["role", "'TOP'|'JUNGLE'|'MID'|'ADC'|'SUP'", "分路", "开局选", "初始化"],
            ["year", "number", "1–8", "1", "跨年"],
            ["week", "number", "1–30", "1", "每周结周"],
        ],
        [2.6, 5.4, 4.4, 3.2, 3.4],
        size=8.5,
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "GameState：属性与成长（18）")
    k.table(
        doc,
        ["字段", "类型", "范围/含义", "默认", "谁写"],
        [
            ["attrs.*（6 项）", "Record<AttrKey, number>", "六维，0–100 整数", "五项 40–70 随机、人气 20", "训练/事件/比赛/衰退"],
            ["exp.*（6 项）", "同上", "旧的「攒经验换点」通道，现仅事件与测试用到", "0", "gainExp（遗留）"],
            ["yearGain.*（6 项）", "同上", "本年已涨点数，用于统计", "0", "gainPoints / applyAttrDelta"],
        ],
        [3.4, 6.0, 5.6, 4.4, 4.0],
        size=8.5,
        caption="表 3-1　`exp` 是遗留字段：`gainExp` 注释写明「保留给事件与测试调用」，正式玩法已不用",
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "GameState：资源与生涯（12）")
    k.table(
        doc,
        ["字段", "类型", "范围/含义", "默认", "谁写"],
        [
            ["stamina / maxStamina", "number", "体力 / 上限（上限可涨到 999）", "60 / 100", "行动扣、休息与住处加"],
            ["rankPoints", "number", "段位分，0–9999", "2800（大师）", "上分、掉分"],
            ["placement", "number", "全服名次（1 起），算出来的", "由分数与周数推出", "ladder.placementOf"],
            ["money", "number", "钱，0–999999", "0", "直播/商业/比赛/商店"],
            ["injury", "number", "伤病 0–3，≥2 不能上场", "0", "输比赛 12%、康复"],
            ["coachTrust", "number", "教练信任 0–100，>60 才首发", "40", "训练赛、比赛、事件"],
            ["signed / teamId / freeAgent", "boolean / string? / boolean", "是否签约 / 队伍 / 是否自由人", "false / null / false", "签约窗口"],
            ["failedWindows", "number", "连续无人可签的窗口数，到 2 结局", "0", "签约窗口"],
            ["honors", "HonorEntry[]", "荣誉流水（同年同荣誉可重复）", "[]", "比赛、跨年"],
            ["owned / subs", "string[] / {id,untilYear}[]", "买断物品 / 年费物品", "[]", "商店"],
            ["seasonResults", "SeasonResult[]", "今年每场比赛的胜负记录", "[]", "比赛结算"],
            ["peakYear / peakScore", "number", "巅峰年份与当时的六维总和", "1 / 0", "跨年"],
        ],
        [3.6, 6.0, 5.4, 3.6, 4.4],
        size=8,
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "GameState：本周与结局（8）")
    k.table(
        doc,
        ["字段", "类型", "范围/含义", "默认", "谁写"],
        [
            ["actionGrid", "(ActionId|null)[] 长度 3", "本周三格", "[null,null,null]", "selectAction / clearSlot / 结周重置"],
            ["actionTargets", "(AttrKey|null)[] 长度 3", "专训练哪一维", "[null,null,null]", "selectAction"],
            ["pendingEvent", "{eventId} 或 null", "非空时锁全部操作", "null", "drawEvent / 选完清空"],
            ["eventDone", "boolean", "本周事件是否已结算", "false", "结周重置"],
            ["ledger / lastLedger", "{label,amount}[]", "本周 / 上周流水", "[]", "收支动作、结周结转"],
            ["flags", "string[]", "事件标记，用于结局尾注", "[]", "事件后果"],
            ["triggeredEvents", "string[]", "已抽过的事件 id（once 去重）", "[]", "事件结算"],
            ["temp", "Partial<Stats>", "**不存**，临场加减", "{}", "比赛事件"],
            ["log", "LogEntry[] 最多 60", "**不存**，界面滚动日志", "1 条开场白", "reduce"],
            ["ended / retired", "Ending|null / boolean", "结局与是否主动退役", "null / false", "endWeek / retire"],
        ],
        [3.4, 5.6, 5.0, 4.2, 4.8],
        size=8,
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "静态数据（不进存档）")
    k.table(
        doc,
        ["表", "字段", "量与出处"],
        [
            ["GameEvent", "id / kind / phase / year? / week? / tags / text / options / once / weight / requires? / filler? / auto?", "代码里 4 条 + 2 条兜底（src/data/events.ts）"],
            ["EventOption", "label / risk / attrs? / bonus? / success? / fail? / successText? / failText? / matchResult?", "事件库 xlsx 里 55 + 36 条待入库"],
            ["Consequence", "attrs / temp / stamina / maxStamina / money / injury / coachTrust / honor / flag / signed / teamId", "六种落点 + 标记"],
            ["RosterTeam / RosterPlayer", "id / name / players[pos,name,ovr]", "S8–S15 八个赛季，每季 14–17 队 × 5 人"],
            ["ShopItem", "id / label / effect / shape(once|year|use) / price / needsContract?", "8 项（src/core/shop.ts）"],
            ["HonorEntry", "id / year", "7 种荣誉，其中 4 种从未被写入"],
            ["SeasonResult", "week / rivalId / won / kind(regular|spring|summer)", "每场一行"],
            ["LogEntry", "text / tone(good|bad|plain)", "界面日志，最多 60 条"],
            ["Ending", "kind / title / body / note", "4 种结局由 endings.ts 组装"],
        ],
        [3.2, 8.4, 5.4],
        size=8,
    )

    # ---------------- 七 ----------------
    k.h1(doc, "七", "与 Excel 的对应关系（方向必须明确）")
    k.table(
        doc,
        ["Excel", "对应代码", "现状", "该往哪个方向走"],
        [
            ["P3-数值总表.xlsx（73 参数）", "src/config.ts", "**双写、手抄**，谁也不是源头", "Excel 为源，脚本生成 config.ts（`gen:config`）"],
            ["P1-事件库-*.xlsx（34 事件）", "src/data/events.ts", "Excel 是策划源，代码里只有 4 条", "Excel 为源，入库脚本导入"],
            ["UI-界面与文案.xlsx（26 条）", "src/ui/main.ts 里的字面量", "双写、手抄", "Excel 为源，导出文案常量"],
            ["任务进度表.xlsx", "—（无代码对应）", "纯管理表", "无需对应"],
            ["测试用例与Bug表.xlsx", "tests/core.test.ts（61 用例）", "用例数对得上，逐条不对应", "可保持现状"],
        ],
        [5.2, 5.4, 4.6, 6.2],
        size=8.5,
        caption="表 7-1　**现状没有一个方向**——三张表都是手抄双份，这是当前最容易分叉的地方",
    )
    k.para(
        doc,
        "**我的建议（待你定）**：先只做一条——`P3-数值总表.xlsx → src/config.ts` 的反向生成。"
        "另外两条（事件、文案）手工量小，等事件入库时再一起考虑。理由：数值是最容易被改、也最容易被忘的地方。",
    )

    # ---------------- 八 ----------------
    k.h1(doc, "八", "存档格式")
    k.table(
        doc,
        ["项", "内容"],
        [
            ["键名", "`lpl-career-proto:v3`（版本号在键名里，换版本直接换键）"],
            ["外层", "{ version: 3, state: GameState }"],
            ["丢弃", "`temp`、`log`（序列化前清空）"],
            ["读档校验", "version 不等 → null；state 缺 year 或 attrs → null；异常 → null"],
            ["失败表现", "当没有存档，回开局屏；不弹错误框"],
            ["无迁移", "v2 旧档直接作废，不做转换"],
        ],
        [3.2, 12.8],
        size=9,
    )

    # ---------------- 九 ----------------
    k.h1(doc, "九", "已知缺口")
    k.table(
        doc,
        ["#", "缺口", "影响"],
        [
            ["1", "数值/事件/文案三处双写", "改一处忘了另一处，就会出现「表里 34 条、游戏里 4 条」"],
            ["2", "`exp` 是遗留字段但仍存在", "读代码的人会以为还有经验条"],
            ["3", "四种荣誉（MSI/MVP/最佳阵容/名人堂）从未被写入", "荣誉柜残缺"],
            ["4", "没有存档迁移机制", "每次改结构，老玩家存档作废（当前可接受，只有你自己玩）"],
            ["5", "`placement` 由 10000 个虚拟对手算出并对结果缓存", "改天梯参数后，缓存的旧结果要被清掉"],
        ],
        [1.0, 7.4, 7.6],
        size=9,
    )

    k.note(
        doc,
        "字段总数 39，与 3.1 表 4-1 的分组一致。改结构时按这个顺序改：types.ts → newGame 默认值 → save 版本号 → 本文档。",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
