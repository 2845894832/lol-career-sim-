# 可玩原型（playable prototype）有没有「标准与验收定义」——一手来源核查

检索时间 2026-10-31。口径：只收官方文档 / 官方资助页 / 出版社与教材 / 署名开发者原文；每条注类型与是否读到正文。

## 结论（10 行）

1. **没有跨公司统一的「playable prototype」官方定义，也没有公开的验收线。** 平台只公开到「concept 审批」（微软），发行商明说 build 要求「不可能列成清单」（Raw Fury）。
2. 真正有**官方定义**的只有两个词：**greybox**（Epic：做布局用的可玩粗稿，先别抛光外观）和 **demo**（Steam：面向买家的、质量要对得起正式版的一小段）。
3. **first playable / vertical slice 只在「钱」的语境里被当里程碑用**：欧盟 Creative Europe 的资助「到做出第一个可玩原型为止」，制作期从 first playable 起算；Screen Australia 把 vertical slice 写成「能进国际融资与 pitch 生态的质量」。
4. **能算「验收表」的公开文本只有资助方申请材料清单**：Screen Australia 要求原型「已测试、可运行」，附硬件要求/启动步骤/操作表/预期体验说明，「评审期打不开或玩不了可判不合格」。
5. 评审标准是**创作价值 + 可行性 + 影响力**（人打分），不是「乐趣达标值」；没有任何一手文本给出「原型几分算过关」。
6. 原型要回答的问题，一手表述高度一致：**该不该做这个游戏**（Rami）、**概念/某个机制的强弱**（Chandler）、**最便宜最快的验证**（Chandler、Unity）。
7. **不该做**也有一手依据：Rami 明确说原型不该高质量/结构好/可复用，用现成素材和基本几何体；Epic 说灰盒通过玩测后再加美术。
8. **原型 ≠ 可发布**的分界不在完成度，而在**用途**：原型对内回答问号、可丢弃；demo 对外帮买家决策、要「measures up to the real experience」，且是独立 AppID、走独立发布清单。
9. 微软公开流程里**根本没有原型里程碑**：只要一个被批准的 game concept（表单化，10–15 个工作日），之后才谈 pitch。
10. 所以「行业标准」可以说的是：**原型的定义按用途（回答问题）而非完成度；验收按「外人能否独立跑起来并看懂」+ 评审主观判断**。这是我从一手材料归纳的，不是任何机构发布的规范。

## 1. 术语：谁定义了什么

- **greybox / blockout｜官方引擎文档**：Epic 原文「Greyboxing (also known as blockout) is the process of making a playable rough draft of a level to get a sense of its gameplay before polishing its look」；用途是先测尺度与布局，「Add props and art once you are happy with how the level plays」。https://dev.epicgames.com/documentation/fortnite/greyboxing-in-unreal-editor-for-fortnite?lang=en-US
- **demo｜平台官方文档**：Steam 原文「generally are a small playable portion of your game that show some of the core mechanics and leave the player excited for more」；质量要求「high quality and measures up to the real experience」；demo 是独立 AppID、有独立 release checklist。https://partner.steamgames.com/doc/store/application/demos
- **prototype（教材）｜出版社章节摘要**：Chandler《The Game Production Toolbox》Ch6 摘要「A prototype can reveal the strengths and weaknesses of a concept or particular gameplay feature」；「focus on what is needed and the quickest way to get it done」；「Pen and paper prototypes can also be effective」；「spend a day… create a somewhat useful prototype」。https://www.taylorfrancis.com/chapters/mono/10.1201/9780429440021-8/prototyping-heather-maxwell-chandler
- **prototype（教材结构）｜出版社目录**：全书把 Part 2 **Creating the Prototype**（Ch4 打底、Ch5 概念、Ch6 原型）放在 Part 3 **Establishing Requirements**（排期/预算/pitch）之前 → 教材把原型当「定需求之前的一段」。https://www.taylorfrancis.com/books/mono/10.1201/9780429440021/game-production-toolbox-heather-chandler
- **prototype vs vertical slice｜作者原文（个人主张，非标准）**：Rami Ismail「Prototypes are to help you figure out whether you should make a game, and the Vertical Slice is to help you figure out whether you can make it」；原型要「fast, cheap, and precise」，且「should not be made to be high-quality, structured well, or reusable」。他自己把 Ideation→Prototyping→Vertical Slice→Production 称作「the most common timeline」，但无调研数据。https://ltpf.ramiismail.com/prototypes-and-vertical-slice/
- **first playable｜官方资助计划用法**：Creative Europe「Video games and immersive content development」（CREA-MEDIA-2026-DEVVGIM）写明资助开发「do vytvoření prvního hratelného prototypu/zkušební verze hry」＝到做出第一个可玩原型/试玩版为止；且「produkční fáze (začínající od vytvoření prvního hratelného prototypu…)」不得早于截止后 10 个月排期 → **first playable 被当作「开发资助终点 / 制作起点」的制度分界**。https://www.kreativnievropa.cz/detail-vyzvy/video-games-and-immersive-content-development-2026
- **vertical slice｜官方资助计划用法**：Screen Australia 把「creating a vertical slice that is of global competitive quality and enables a team to access the international funding and pitching ecosystem」列为可资助的显著里程碑 → 官方语境里 VS 是**融资/展示用**产物，不是内部验证品。https://screenaustraliafunding.smartygrants.com.au/d/files/dlm/b0fe9984a9a1581a39ee30301236a24f31b01d
- **pre-production / green-light｜引擎厂商课程**：Unity Learn 定义 pre-production 为「planning, prototyping, pipeline setup, and initial designs」；「iterate designs … while changing direction is still relatively cheap and easy」；结束时向股东/投资人展示并「green-lit」→ 未给任何完成度标准。https://learn.unity.com/tutorial/the-real-time-production-cycle

## 2. 验收标准：公开文本能到多细

- **Screen Australia（官方资助指南，2025-07 更新）**是最接近验收表的一手文本：申请门槛是项目已有「a playable prototype」；必交材料含 Playable Prototype（「please ensure that your prototype has been tested and is functional」）、30 秒实机视频、Prototype Details（最低硬件、逐步启动说明、操作/键位表、原型预期体验）、Production Plan（须含 milestones and acceptance criteria）。明确后果：「prototypes are inaccessible or unplayable after the close of the round may be deemed ineligible」。评审四条：Creative Merit / Viability / Impact / EDI。https://screenaustraliafunding.smartygrants.com.au/d/files/dlm/b0fe9984a9a1581a39ee30301236a24f31b01d
- **Raw Fury（发行商公开 pitch 页）**直接否认存在通用清单：「We wish we could put together a bullet list of what we want to see in a build … it's what you want in that build that matters」。它只给「有用但不强制」的四项：可跳过过场、分段存档点、英文字幕、操作说明；并说「we can't guarantee we'll play any build more than once」。https://rawfury.com/how-to-pitch-to-raw-fury/
- **微软（官方文档）**：公开流程只有「An approved game concept is required for all XBOX games」，表单字段＝开发者/发行商、key features、描述、发售日、平台、定价、网络与 UGC、可选 gameplay 视频；审核 10–15 个工作日；concept 通过后才可 pitch 融资。**没有原型/里程碑验收文本**。https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-join-id-at-xbox ｜https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-pitch-your-game
- **Creative Europe（官方资助计划）**：评审项是原创性、技术创新、叙事与视觉质量、美术与音效质量、开发与财务策略、销售潜力、营销策略——**没有「可玩性/乐趣」评分项，也没有原型完成度门槛**。https://www.kreativnievropa.cz/detail-vyzvy/video-games-and-immersive-content-development-2026

## 3. 原型该验证什么、不该做什么

- 该验证：**该不该做**（Rami，「answer the question marks in your idea」）；**概念/某机制的强弱并据此讨论最优版本**（Chandler 摘要）；**布局与尺度是否成立**（Epic 灰盒：车辆能否通过、平台高度是否可达）；**设计改动是否还便宜**（Unity：pre-production 是改方向最便宜的窗口）。
- 不该做：**不追求质量、结构、可复用性**（Rami 原文）；**不在玩法成立前上美术/道具**（Epic：「Add props and art once you are happy with how the level plays」）；**不必是数字原型**（Chandler：纸面原型同样有效）。
- 反例边界：Raw Fury 接受「红方块蓝球在灰房间里」，也接受「接近成品美术的一段谜题」，判断标准是「是否传达出你想做的东西」——**美术不是禁区，但也不是验收项**。https://rawfury.com/how-to-pitch-to-raw-fury/

## 4. 原型 vs 可发布：一手来源怎么划线

- **用途线**：原型回答「should we / can we」；VS 验证生产管线（Rami，作者主张）。官方侧同构：Creative Europe 以 first playable 结束开发资助、开始制作期。
- **质量线**：demo「high quality and measures up to the real experience」（Steam 官方）；原型「should not be high-quality」（Rami）。
- **流程线**：demo 是独立 AppID、独立发布清单、面向买家决策（Steam 官方）；原型无任何平台流程，只在资助/发行申请里作为材料出现（Screen Australia、Raw Fury）。
- **内容线**：Steam 要求提交审核的正式 build 用「mostly final build」，「The build should include all the featured described on your store page」（原文如此）——可发布＝商店页承诺全兑现，原型阶段远未到这条线。https://partner.steamgames.com/doc/store/releasing

## 5. 未核实 / 未找到

| 事项 | 状态 |
|---|---|
| 微软/索尼/任天堂对 prototype、first playable、vertical slice 的公开里程碑定义 | **未找到**（微软只公开 concept；PlayStation Partners、任天堂开发者门户需登录/NDA → 未核实） |
| 跨公司统一、可引用的「playable prototype 验收标准」 | **未找到**（现有只是一份资助指南 + 一家发行商口径） |
| 「乐趣/核心循环达标」的量化验收阈值 | **未找到**（所有一手评审项均为主观打分） |
| Godot 官方文档中的 prototype 定义 | **未找到**（查 best practices 索引无此条目）https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html |
| Emily Short 专门定义/验收原型的公开长文 | **未找到**（站内检索仅命中服务页与邮件问答）https://emshort.blog/?s=prototype |
| NYU Game Center / DigiPen 课程级原型验收要求 | **未核实**（NYU BFA 公告页无课程描述；DigiPen 课程列表 JS 加载）https://bulletins.nyu.edu/undergraduate/arts/programs/game-design-bfa/ ｜https://www.digipen.edu/academics/current-courses |
| Chandler《The Game Production Handbook》样章 / milestone 验收表正文 | **未核实**（gamedeveloper 样章页 403） |
| Devolver 公开 pitch/原型要求页 | **未找到** |
| 欧盟 call 英文原文（FTOP/PDF） | **未核实**（EACEA/FTOP PDF 被反爬拦截，只有国家信息点转述页读到） |
