# 事件库、数值表、假设：一手来源笔记

**覆盖**：①叙事游戏「事件池 + 触发条件」的有名概念与可复现实现（storylet / QBN / ink / Twine / A Dark Room 源码）；②平衡数值从零建立与校准的方法（教材、开源数值表、Machinations 体系）；③「可验证假设」的写法与验证方法（假设映射、测试类型、纸原型）。
**不覆盖**：具体题材/文案写法；商业化与留存调优；引擎操作；对某套做法好坏的评判。
**检索时间**：2026-10-29。**环境限制**：gdcvault.com 全部重定向、schedule.gdconf.com 返回 403、Reigns 相关一手页与 StoryNexus 文档（Google Docs）均打不开；Routledge/Taylor & Francis 与 Wiley 出版社页不可达。相关条目只标「未核实」，不作结论依据。
**标注**：【机制】=工具/代码里写死的规则；【通用做法】=多个一手来源一致；【某人主张】=单一作者的看法，不是行业标准。

---

## 1. 事件库怎么设计

**结论（可直接用）**

1. **一条事件 = 内容 + 前置条件 + 效果**，三者缺一不可；这套结构叫 **storylet**。事件池不是「一堆文案」，是「同一组状态变量上的一批带条件的内容」。【通用做法】
2. **条件写成对世界状态的谓词**（数值比较、标志、是否见过某段内容），不要写进散文。状态变量（quality）是唯一真相：可增可减，能表示库存、技能、剧情进度、威胁值。
3. **两种选法别混**：QBN 让玩家从「当前合法的事件」里自己选；**salience-based** 由系统挑「最贴合当前处境」的那条（Emily Short 自称是她造的词）。手机上单按钮「下一天」更适合后者或纯随机。
4. **防重复有现成的四档语义，直接照 ink 抄**：默认选项用过即消失（once-only）；`+` 粘性选项可重复；`{once:}` 每条只出现一次；`{shuffle once:}` 洗牌抽完为止；`{shuffle stopping:}` 抽完停在最后一条兜底；`{cycle:}` 循环。
5. **空池必须显式兜底**，两种成熟做法：过滤后为空就顺延重抽（A Dark Room 的做法）；或永远保留一组「always available」的填充事件（Emily 描述 storylet 系统时明确列出这一项）。
6. **池子规模有两个已知坑**：事件太少时「内容没意思」（Emily 对 StoryNexus 的批评）；事件太多时可用列表会淹没玩家（Fallen London 后来加了排序、颜色、置顶）。中间规模才是 storylet 的舒适区。
7. **先定状态再做内容**：Emily 的实际流程是 写目标 → 画故事弧 → 找重复模式 → 定 quality → 最后写事件，并且先用卡片做纸原型跑几轮、再改数值。

**证据**

- storylet 三要素原文："there is a piece of content… there are prerequisites that determine when the content can play… there are effects on the world state" → https://emshort.blog/2019/11/29/storylets-you-want-them/ ｜作者原文
- QBN 定义与归属："Quality-based narrative is the term invented by **Failbetter Games** to refer to interactive narratives structured around storylets unlocked by qualities"；同文注脚：Failbetter 已停用该词。Emily 明确说 **salience-based narrative 是"a term I just made up"** → https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/ ｜作者原文（**纠正**：QBN 不是 Emily 造的词）
- 状态分工（进度/资源/威胁/关系）与「always available」元素、"one story can affect another" → https://emshort.blog/2019/12/03/storylets-play-together/ ｜作者原文
- 池子太小/太大两个坑与 FL 的排序着色对策 → 同上 Beyond Branching ｜作者原文
- 设计流程与纸原型（"writing storylets down on note-cards and putting stat ranges on them, then playing through a few cycles"）→ https://emshort.blog/2020/02/18/mailbag-development-process-for-storylet-based-interactive-fiction/ ｜作者原文
- ink 官方语法：默认 choice 只能用一次；`+` sticky；条件 `{ not visit_paris }`；`{stopping:}`/`{cycle:}`/`{once:}`/`{shuffle:}`；`{shuffle once:}` 抽完即止；`{shuffle stopping:}` 抽完停在最后一条 → https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md ｜官方文档
- ink 的随机与可复现：`RANDOM(min,max)`、`SEED_RANDOM(n)`（测试时固定随机种子）→ 同上 ｜官方文档
- Twine/Harlowe 官方手册：`(either:)` 随机取一；要取多个用 `(shuffled:)` 再切子数组（等价于不放回抽签）；想「同一次访问固定」就把结果存进变量 → https://twine2.neocities.org/#macro_either ｜官方文档
- Twine/SugarCube 官方文档：`visited("Passage")` 返回访问次数，用来做「只发生一次」的门 → https://www.motoslave.net/sugarcube/2/docs/ ｜官方文档
- 开源可跑的实现：A Dark Room `triggerEvent()` 先遍历 `EventPool` 用 `event.isAvailable()` 过滤，再等概率抽一条；**若 filtered 为空则 `scheduleNextEvent(0.5)` 顺延重抽**；事件条件就是普通 JS 谓词（如 `$SM.get('stores.fur', true) > 0`）→ https://github.com/doublespeakgames/adarkroom/blob/main/script/events.js ｜开源代码
- Twine 本体只提供 passage + link，**没有内建事件池**；随机/去重全靠上述格式宏 → 由上两条官方文档反证，属【机制】而非主张。

---

## 2. 数值表怎么定

**结论（可直接用）**

1. **先定义你要「平衡」哪一种**：单机难度是否合适 / 非对称起始是否公平 / 多条策略是否互有胜负 / 同类物件性价比是否一致。四类混在一起谈，数值永远定不下来（Schreiber）。【某人主张，但四分类本身可操作】
2. **物件用 cost/benefit 比值定**；成长曲线就是 **cost curve（transitive）**：线性、递减回报、递增回报三选一。它的问题是一错全错——所以适合「事后按 playtest 反推」，不适合开局拍脑袋。
3. **从零建表的标准动作**：把所有对象与属性先列进表格 → 用公式联动（改一个值立刻看到 DPS/收益变化）→ **一次只改一个值** → 不确定就差多少时用 **Rule of 2**（直接翻倍或减半，学到的信息更多）。
4. **概率与分布用表跑，不靠感觉**：Excel 里 `RAND()` + F9 反复重算就是 Monte Carlo，看结果区间和分布。
5. **复杂经济画成「源—池—汇—门—转换器」再模拟**：Dormans/Adams 的 Machinations 体系，官方说法是「一千次运行几秒钟出统计」；模式库（Escalating Challenge、Static/Dynamic Friction、Attrition 等）可以直接当成长/消耗曲线的模板。
6. **消耗与成长的配平基准是同一张表**：单位时间产出 vs 单位时间消耗、升级所需经验 vs 每局可得经验，都放进同一张联动表算比值。
7. **顺序不能反**：机制没定就调数值＝白调（Schreiber 原话：给不满足设计目标的游戏做平衡是浪费时间）。

**证据**

- Schreiber《Level 16: Game Balance》：balance 的四种含义；物件平衡＝相同 cost/benefit 比；transitive/cost curve、intransitive/RPS、"fruity" 三种；三种手段＝数学/直觉/playtest；「Learn to love Excel」（列对象、加总、模拟、看因果）、"Make one change at a time"、**Rule of 2** → https://gamedesignconcepts.wordpress.com/2009/08/20/level-16-game-balance/ ｜作者原文（免费课程）
- Schreiber 同篇："Game design is a process of discovery… you don't know what the correct numbers are"｜作者原文
- Dormans & Adams《Game Mechanics: Advanced Game Design》出版社官方样章：目录含 Ch4 Internal Economy、Ch5 Machinations、Ch8 **Simulating and Balancing Games**、附录 B 模式库（**Escalating Challenge**、Static/Dynamic Friction、Attrition…）；前言写明「对内部经济没把握？Machinations 让你几秒钟跑 1,000 次」 → https://ptgmedia.pearsoncmg.com/images/9780321820273/samplepages/0321820274.pdf ｜书籍（出版社样章 PDF）
- 开源数值表实例：Battle for Wesnoth 单位数值全在 `.cfg` 里（Peasant：`cost=8`、`movement=5`、`experience=19`、`level=0`），可直接算性价比与升级曲线 → https://github.com/wesnoth/wesnoth/blob/master/data/core/units/humans/Peasant.cfg ｜开源代码
- 开源数值表实例 2：UnCiv 用整份 JSON 存单位/建筑成本与强度（Civ V 规则集）→ https://github.com/yairm210/Unciv/blob/master/android/assets/jsons/Civ%20V%20-%20Gods%20%26%20Kings/Units.json ｜开源代码
- 数值与事件同表联动的一手例子：A Dark Room 事件里的战斗数值直接读 `World.getHitChance()`、武器 `damage`、`cost`，改表即改行为 → https://github.com/doublespeakgames/adarkroom/blob/main/script/events.js ｜开源代码
- 数值分类参考（货币/指标/工具/领地）由 Emily 引用 Tadhg Kelly 提出 → https://www.whatgamesare.com/2011/11/currencies-and-other-numbers-game-design.html ｜作者原文（**本次打不开，未核实**，仅作线索）

---

## 3. 怎么立「假设」

**结论（可直接用）**

1. 一条可验证假设的骨架：**「如果改 X，那么 Y 会从 a 变到 b，因为 Z」**，且一条只含一个自变量。写不出「被什么结果推翻」，就不是假设。
2. **先列再排序**：把假设摊开在「重要性 × 现有证据」二维上，先测**高风险 + 低证据**的那一格；并按 需求可行性/技术可行性/商业可行性/可持续性 四类分开列，避免只测好测的。
3. **把粗糙想法改写成 precise / discrete / actionable 的一句话**——这是假设映射方法里明确要求的产出标准，不是文风问题。
4. **测试类型要先说清**：fun test / usability test / balance test / bug test 目的不同、阶段不同；不知道这次要测哪一类，测了也读不出结论（Schreiber）。
5. **验证载体按阶段升级**：纸卡或表格原型 → 可玩原型 → 目标玩家 playtest。叙事池子最便宜的验证就是 Emily 的做法：事件写在卡片上、标好数值区间，手动跑几轮，再改数值。
6. **记录「预期 vs 实测」，一次只改一个变量**；数值平衡本身就是 discovery 过程，假设的价值在于让每次改动可回溯。

**证据**

- 假设映射（Strategyzer 官方方法页）：从 Desirability / Feasibility / Viability / Survivability 四个面向提取隐含假设；用 **2×2（重要性 × 证据）** 排出「高风险低证据」；再把原始假设提炼成 "precise, discrete, and actionable statements ready for validation" → https://www.strategyzer.com/programs/assumptions-mapping-prepare-to-test-your-business-idea-part-1 ｜官方方法页（作者方，非游戏业）
- Schreiber《Level 12: Solo Testing》：playtest 分 bug / focus / usability / balance / fun 五类，各有不同目标与适用阶段；"you need to know what your goal is before you can achieve it" → https://gamedesignconcepts.wordpress.com/2009/08/06/level-12-solo-testing/ ｜作者原文
- Schreiber 的「一次只改一个变量」与 Rule of 2（同上 Level 16）＝让假设可归因的操作纪律 → https://gamedesignconcepts.wordpress.com/2009/08/20/level-16-game-balance/ ｜作者原文
- 叙事设计的纸原型验证（卡片 + 数值区间 + 手动跑几轮）→ https://emshort.blog/2020/02/18/mailbag-development-process-for-storylet-based-interactive-fiction/ ｜作者原文
- **GDC 侧**：本次未能打开任何 GDC 演讲页（gdcvault.com 重定向到 gdconf.com；schedule.gdconf.com 403），因此**不引用任何 GDC 演讲内容**，只记录这一缺口（见下）。

---

## 未核实 / 未找到

- **「Emily Short 是 quality-based narrative 的作者」与原文不符**：她本人写「该词由 Failbetter Games 发明」；她自称发明的是 salience-based narrative（两处均见 §1 链接）。若需引用归属，按 Failbetter 写。
- **StoryNexus Reference Guide**（Failbetter 官方 QBN 工具文档，Google Docs）打不开，未能读到 quality/requirement 的原始写法 → 未核实。
- **Reigns 的一手设计说明**：只检索到 GDC Vault 条目（https://www.gdcvault.com/play/1028689/ ，重定向不可读）与中文二手翻译；**没有读到任何一手正文**，故本文件不写 Reigns 的卡池机制 → 未找到。
- **Machinations 官方文档正文**：docs 页面正文由前端渲染，只取到导航，未读到条款 → 未核实；§2 的 Machinations 描述改用 Dormans 出版社样章。
- **《Game Balance》(Schreiber & Romero) 出版社目录页**：Routledge 页面不可达（https://www.routledge.com/Game-Balance/Schreiber-Romero/p/book/9781315156422 ），Taylor & Francis 对应页 404 → 未核实，未引用其目录。
- **GDC 演讲页**：全部不可读（见 §3），未找到可引用的一手演讲页。
- **Twine 官方层面的「事件池」**：不存在；只有格式层（Harlowe/SugarCube）提供随机与访问计数 → 已核实为「没有」。
- **Tadhg Kelly 原文**（货币/指标/工具/领地四分类）打不开 → 未核实：该分类只能算 Emily 转述，不宜直接引用给开发者。
