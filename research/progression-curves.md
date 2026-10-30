# 属性成长的递减回报：一手来源笔记

**覆盖**：递减曲线的数学形式；Wesnoth / NetHack / Cataclysm-DDA / OSRS 的真实经验表；Schreiber 教材原文；接近上限与小数增量的处理。
**检索时间**：2026-10-29。**标注**：【机制】=代码/配置里写死；【作者主张】=单个作者的文章；【二手】=wiki，只在没有一手时用。
**先纠正一个前提**：Level 16 里没有「cost curve 的三种形式」。那篇的「三种」是三种平衡对象的方法——transitive（cost curve）/ intransitive（石头剪刀布）/ fruity（不可比）。曲线只在讲 transitive 时顺带提了线性与递减/递增。真正分三类曲线的是 2010 年的 Level 3。

## 结论

1. **数学形式**：一手能确认的是**分段指数**（NetHack）、**二次**（CDDA）、**每单位手写表**（Wesnoth）、**约 +10%/级的几何增长**（OSRS）。**平方根 / 对数没找到一手公式**（只有设计博客和 StackExchange 问答，未采信）。
2. **真实表长什么样**：全是整数阈值，不是连续函数；相邻两级的差值单调递增——OSRS 每级差 83→91→102→…→1,228,825；CDDA 1 万→4 万→9 万→…；NetHack 20→40→80→…→1 亿。没有哪个项目写「每次 +0.36 点」。
3. **教材**：Schreiber 只给方向不给公式，且明确「递增曲线，如三角或指数（triangular or exponential）」。
4. **上限**：没有统一做法。CDDA 到 10 级把增量直接设 0；NetHack 30 级封顶、溢出 XP 无收益；Wesnoth 满级转 AMLA，继续给但每次 +3 HP 而下次所需 XP +20%；OSRS 99 级后数字还能涨到 2 亿、无任何收益。
5. **小数值**：四个项目里属性/等级都是整数，小数只存在于「进度条」——CDDA 用 int 累加器、显示时除以 100；OSRS 把 XP 存成 ×10 的定点整数。没有一手来源支持「每次给属性 +0.36」这种写法。
6. **对你的 0.36**：【推算】624×0.36≈225 = 5 属性×45，正好是 55→100。所以曲线不用改总量，只需让「每点成本」由低走高；业内通用做法是把曲线放在**成本**上（整数 XP / 进度条），而不是放在**增量**上（0.36 点属性）。

## 1 曲线类型与公式

- **Schreiber, Level 16**：linear proportion，或 curved——"a law of diminishing returns, where you have to pay progressively more for each additional bit of benefit; or perhaps there are increasing returns"。只有定性描述，无公式 → https://gamedesignconcepts.wordpress.com/2009/08/20/level-16-game-balance/ ｜作者原文
- **Schreiber, Level 3（2010）**：把曲线分成四类——线性（"+1 cost means +1 benefit"，称其 "pretty rare"）；递增（"such as a triangular or exponential curve"）；递减；自定义（举 M:tG 法力曲线，5 费处拐点） → https://gamebalanceconcepts.wordpress.com/2010/07/21/level-3-transitive-mechanics-and-cost-curves/ ｜作者原文
- **NetHack：分段指数**（`newuexp`）：`lev<10 → 10·2^lev`；`10≤lev<20 → 10000·2^(lev-10)`；`lev≥20 → 10^7·(lev-19)` → https://github.com/NetHack/NetHack/blob/NetHack-3.6.7_Released/src/exper.c ｜开源代码
- **CDDA：二次成本**（`xp_to_level = 100*100*(level+1)^2`，`on_exercise_change` 里逐级扣减）→ https://github.com/CleverRaven/Cataclysm-DDA/blob/master/src/skill.cpp ｜开源代码
- **Wesnoth：查表，不拟合公式**——每个 `[unit_type]` 手写 `experience=` 整数 → 见下节 ｜开源配置
- **平方根 / 对数**：未找到一手。gamedev.stackexchange 与设计博客有讨论，属二手，未用作结论。

## 2 真实经验表（可核对）

**Wesnoth（同一兵种线，人类 Loyalist）**：Spearman L1 `experience=42` → Swordsman L2 `experience=80` → Royal Guard L3 `experience=150`，且 `advances_to=null` + `{AMLA_DEFAULT}`。42→80→150 约每级 ×1.9，是递增；但只有 3 档，本质是手写表。
https://github.com/wesnoth/wesnoth/blob/master/data/core/units/humans/Loyalist_Spearman.cfg ｜开源配置
https://github.com/wesnoth/wesnoth/blob/master/data/core/units/humans/Loyalist_Swordsman.cfg ｜开源配置
https://github.com/wesnoth/wesnoth/blob/master/data/core/units/humans/Loyalist_Royal_Guard.cfg ｜开源配置

**NetHack（升到下一级所需 XP）**：L1→2 20；L2→3 40；L3→4 80；…L9→10 5,120；L10→11 10,000；…L19→20 5,120,000；L20→21 10,000,000；…L29→30 100,000,000。前 19 级每级 ×2，之后改为每级 +1000 万。**是递减**（边际成本暴涨）。
同上 exper.c；`MAXULEV 30` 在 https://github.com/NetHack/NetHack/blob/NetHack-3.6.7_Released/include/global.h ｜开源代码

**Cataclysm-DDA（技能 0→10 所需练习量）**：L0→1 10,000；L1→2 40,000；L2→3 90,000；L3→4 160,000；…L9→10 1,000,000。严格二次。`MAX_SKILL = 10` 在 https://github.com/CleverRaven/Cataclysm-DDA/blob/master/src/game_constants.h ｜开源代码

**OSRS（累计 XP）**：L2 83；L3 174（本级差 91）；L4 276（差 102）；L92 6,517,253（正好是 L99 的一半）；L99 13,034,431（差 1,228,825）。约每级 +10%，每 7 级翻倍；上限 200,000,000。**是递减**。
https://oldschool.runescape.wiki/w/Experience ｜【二手】社区 wiki；但其中「XP 存为 32 位定点整数、1 位小数、上限 2 亿」直接引用 Jagex Mod Ash 原话，可作一手引文用。

## 3 教材原文（Schreiber）

- Level 16 只把曲线当作 transitive 平衡的一部分，并强调「math is hard, and it can be incorrect」；没有给出任何具体函数。
- Level 3 才是「cost curve」专章：先定成本/收益的数学关系（上节四类），再把所有效果折算成同一种资源；并说明「递增曲线」的一个实际理由——如果每点属性同价，玩家会全砸在一两个属性上，递增成本才逼出取舍。**这正是你要的「越高涨越慢」的教材依据，但它不给公式，只给方向。**
- 同章还给了一条可操作判据：越贵的曲线越把游戏推向后期；越平缓越偏前期。

## 4 接近上限时怎么办（两种都真实存在）

- **硬归零**：CDDA `if( unadjustedKnowledgeLevel() >= MAX_SKILL ) knowledge_amount = 0;`——到顶后练习量直接清零，不再累积。｜【机制】
- **硬封顶、溢出白给**：NetHack `newexplevel()` 只在 `u.ulevel < MAXULEV` 时升级；满 30 级后 XP 继续涨但不产生任何效果。｜【机制】
- **继续给，但越来越不值**：Wesnoth 满级后每次 AMLA 给 `increase_total=3`（最大 HP +3）并治疗，同时 `max_experience` +20%、`max_times=100`。即第 n 次 AMLA 的 XP 需求按 1.2^n 复利上涨，收益恒定 +3 HP。→ https://github.com/wesnoth/wesnoth/blob/master/data/core/macros/amla.cfg ｜开源配置
- **只留数字**：OSRS 99 级封顶，XP 仍可累到 2 亿但不再升级；2 亿后连 XP 都不给（"The skill can still be trained afterwards, but no experience will be received"）。｜【二手】+ Jagex 引文

**归纳**：单机/策略类倾向硬上限；长线养成/MMO 倾向「继续记数、无收益」或「给微量固定收益 + 成本复利」。你这种一局 624 次行动的生涯模拟，更像前者（局内封顶）。

## 5 小数增量怎么处理

- **CDDA：整数累加器 + 显示时除**。`_exercise` 是 `int`；`train(int amount, float catchup_modifier, ...)` 把浮点系数乘进去后仍累加进 int（截断）；对外显示用 `get_progress_level() = exercise()/100.0f`，`exercise(raw=false)` 再除以本级阈值。→ skill.cpp / https://github.com/CleverRaven/Cataclysm-DDA/blob/master/src/skill.h ｜【机制】
- **OSRS：定点整数**。Jagex Mod Ash：「stored as a 32-bit INT that's treated as a fixed-point number with one decimal place」；游戏内不显示小数，两笔 2.5 XP 会先后显示成 2 和 3。｜一手引文（经二手 wiki 转引）
- **NetHack / Wesnoth：根本没有小数**。奖励是整数（击杀/命中给整数 XP），阈值也是整数，小数只出现在「当前进度 / 下一级」的百分比里。｜【机制】
- **没有找到**任何一手来源说「每次行动给属性 +0.36 点，内部用浮点累加」。业内的等价做法是：**行动 → 整数 XP（或 ×100 的整数「毫点」）→ 攒够递增阈值 → 属性 +1**。属性对外始终是整数。

## 6 未找到 / 未核实

- 平方根、对数曲线在商业游戏里的**一手公式**：未找到（只有二手设计博客）。
- RuneScape 官方（Jagex 站点）的 XP 表页：未找到；只有 Mod Ash 推文引文。
- D&D 5e 官方 SRD 的升级 XP 表：本次未取（PDF 源，未核实）。
- Wesnoth 官方手册的「XP 如何获得」页：wesnoth.org/manual 返回 403/404，未核实；本文只用其 `.cfg` 配置与源码宏。

---
**你现在该自己决定的**：曲线放成本侧还是增量侧；满级是归零、封顶还是 AMLA；小数用 ×100 整数还是 float。这三件是设计取舍，上面只给证据和别人的选择。
