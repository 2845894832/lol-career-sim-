# 游戏行业的 concept / pre-production 实际安排（一手来源笔记）

**覆盖**：从「有想法」到「正式开工」这一段——概念期与预制作里的阶段划分、开工前产出物、原型与纵向切片、独立开发者自述、平台侧硬性时间/费用、小体量内容的工作量参照。
**不覆盖**：production 之后的排期/外包/QA/本地化细节；引擎操作；中国版号与国内发行；对哪种做法更好的评价。
**检索时间**：2026-10-28。**环境限制**：`itch.io`、`globalgamejam.org`、`gamedeveloper.com` 在本机不可访问（DNS/Cloudflare 拦截），相关条目一律标「未核实」，不作结论依据。

## 0. 怎么读

- 每条证据标**来源类型**：官方文档 / 平台文档 / 作者原文 / 演讲 / 书籍。
- **【机制】**＝平台或厂商流程强制、或官方文本明写的；**【方法论】**＝某个作者/某本教材主张的做法。二者不混用。
- 「存疑」＝我读到的表述与另一来源不一致，或只有一个来源。 「未核实」＝页面打不开，我没读到正文。

---

## 1. 阶段划分：pre-production 与 production 的边界

**结论**

1. **没有一个跨公司统一的官方阶段模型。** 被官方文件真正钉死的是**平台流程节点**（Xbox 概念审批、Steam 商店页、build 审核），不是 concept→prototype→vertical slice→production→alpha/beta/gold 这套词。
2. 最接近「通用序列」的公开文本都是**个人或教材版本**，措辞各不相同，不能当行业标准引用。
3. 教材侧的分界线在**原型**：原型阶段结束＝概念与可玩性被验证；之后才进排期、预算、pitch、组队。
4. 平台侧的边界在**可审的 build**：Valve 要求提交审核的 build「包含商店页上描述的全部特性」，即 production 至少要先走到「特性齐全」。
5. alpha/beta/gold 的**确切定义没有官方统一文本**——本次未找到，标注存疑。

**证据**

- Rami Ismail《Prototypes & Vertical Slice》：给出 8 段序列 Ideation → Prototyping → Vertical Slice → Production → Alpha (Feature Complete) → Beta (Content Complete) → Release Candidate → Release。他称这是 "the most common timeline"，但没有调研数据支撑 → **【方法论】/存疑**。https://ltpf.ramiismail.com/prototypes-and-vertical-slice/ ｜作者原文
- Heather Chandler《The Game Production Toolbox》(2020) 出版社官方目录：Part 2 **Creating the Prototype**（Ch4 Laying the Groundwork、Ch5 Creating Concept、Ch6 Prototyping）→ Part 3 **Establishing Requirements**（Ch7 Schedule、Ch8 Budget、Ch9 Pitching Your Game）→ Part 4 组队 → Part 5 Executing the Plan → Part 6 Launching。即该教材把「概念+原型」整块放在排期/预算/融资之前，且**不叫 pre-production，叫 prototype 阶段**。https://www.taylorfrancis.com/books/mono/10.1201/9780429440021/game-production-toolbox-heather-chandler ｜书籍（出版社目录页）
- Steamworks《Release Process》：build checklist 要求 "Upload a mostly final build default branch (The build should include all the features described on your store page…)"；商店页须**先于** build 提交审核。https://partner.steamgames.com/doc/store/releasing ｜平台文档
- IGDA《Game Industry Standards》只定义伦理、署名、crunch 等标准，**没有阶段模型**。https://igda.org/resourcelibrary/game-industry-standards/ ｜行业组织文件 → 结论：**未找到 IGDA 官方的阶段划分一手来源**。

---

## 2. 开工前的产出物：concept / one-pager / pitch deck / GDD

**结论**

1. **真正「必须」的只有平台流程要的那几样**：Xbox 要一个被批准的 game concept；Steam 要商店页素材（品牌图 + 文字描述 + 截图，最好有 gameplay trailer）。
2. **没有一手证据表明「完整 GDD」是开工门槛。** 教材把概念文档写成方法建议，不是平台要求；本次未找到任何官方文件要求提交 GDD。
3. **「一页纸概念」没有公开标准写法。** 能找到的官方结构化模板只有 Xbox 的 concept 表单（分项字段）；Steam 商店页字段事实上就是「对外的一页纸」。
4. Valve 官方把商店页定位成**验证与建受众工具**，并明确建议：对美术方向和核心功能集「比较有把握」时再公开。
5. **哪些常被跳过**：只有开发者自述这类一手材料（见 §4），**没有统计口径的官方数据** → 不能量化。

**证据**

- Microsoft Learn《Join ID@XBOX》："An approved game concept is required for all XBOX games"；concept 表单字段＝开发者/发行商、key features、游戏描述、目标发售日、平台、市场与定价、网络功能与 UGC、可选 gameplay 视频/预告；审核常规 10–15 个工作日。https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-submit-game-concept ｜官方文档【机制】
- Microsoft Learn《Pitch your game for funding》：拿到 approved concept 之后才能向 ID@Xbox pitch 融资（Game Pass、Developer Acceleration Program）。https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-pitch-your-game ｜官方文档
- Steamworks《Coming Soon》：需要 "a set of branding images, written description, and ideally a gameplay trailer"；发布前**至少两周**上线；审核 3–5 个工作日、建议提前 7 天提交；作用＝wishlist + Community Hub + 收集反馈；并建议 "wait to start showing off your game publicly until you are pretty confident on your art direction and core feature set"。https://partner.steamgames.com/doc/store/coming_soon ｜平台文档【机制】
- Chandler 目录把 **Ch5 Creating Concept** 与 **Ch9 Pitching Your Game** 单列成章 → 教材视「概念文件」与「pitch」为两份独立交付物。https://www.taylorfrancis.com/books/mono/10.1201/9780429440021/game-production-toolbox-heather-chandler ｜书籍
- **未找到**：可公开访问的发行商/孵化器 pitch 模板一手页面（多在申请门户或 NDA 内）；本次只拿到 Xbox 的表单化流程。

---

## 3. 原型（prototype）与纵向切片（vertical slice）

**结论**

1. 两者**目的不同**：prototype 回答「该不该做这个游戏」（快速验证玩法假设，糙、可丢弃）；vertical slice 回答「做不做得出来」（用接近最终的质量跑通一段，**验证生产管线**）。
2. 上述区分是 Rami 的个人表述；他同时指出很多独立开发者把两者混用（把 VS 当 pitch 素材），**说明业内定义并不统一** → 存疑。
3. 平台文档**不给这两个词下定义**；Steam 只说 demo 是「游戏的一小段可玩部分，展示部分核心机制」。
4. 实际路径常见为：纸面/文字原型 → 小型 VS → 该 VS 直接变成 demo → 拿发行 → 进 production（见 §4 的一手案例）。

**证据**

- Rami 原文："Prototypes are to help you figure out whether you **should** make a game, and the Vertical Slice is to help you figure out whether you **can** make it"；VS 的用途写作 "testing your production pipeline"；原型要 "fast, cheap, and precise"。https://ltpf.ramiismail.com/prototypes-and-vertical-slice/ ｜作者原文【方法论】
- Steamworks《Demos》：demo 是 "a small playable portion of your game that show some of the core mechanics"，且是独立 AppID。https://partner.steamgames.com/doc/store/application/demos ｜平台文档
- GDC Vault 演讲条目《The Vertical Slice》存在，但页面是 JS 应用，**正文未读到** → 内容未核实（存疑）。https://www.gdcvault.com/play/1022329/The-Vertical-Slice ｜演讲（仅确认条目）
- GodotFest 演讲页：作者描述自家 VS "became our demo, and it did its job, it proved the core mechanic worked"。https://godotfest.com/talks/the-price-of-rushing-preproduction/ ｜演讲

---

## 4. 独立开发者的现实做法（有署名自述）

**结论**

1. 有署名的公开自述存在，但**几乎都是事后复盘（postmortem/talk），不是开工前的计划清单**。
2. 一个两人团队的完整链条（可当真实样本看）：文字 roguelike 原型 → Godot 3 做的**小型 3D 纵向切片** → 该切片成为 demo → 靠它拿到发行资金 → 因发行档期**压缩预制作** → 代价在发售前几周集中爆发（故事、关卡、敌人设计、boss 的量级被低估）。
3. 作者事后的判断：预制作应当"锁定"东西、并度量机制改动的影响；把「以后再定」留到 production 会一路累积成风险。
4. **未找到**：大样本、有统计口径的「独立开发者开工前实际做了什么」一手来源（问卷/调查）。

**证据**

- Giovanni Beltran（两人工作室）《The Price of Rushing Preproduction — Vultures: A "Turn-Based Resident Evil" Postmortem》讲者页与摘要，含上述时间线与自述教训。https://godotfest.com/talks/the-price-of-rushing-preproduction/ ｜演讲（会议官方 talk 页，讲者本人自述）
- Rami 那篇是**从业者自述的方法论**，不是某款游戏的开局记录——引用时要分清。https://ltpf.ramiismail.com/prototypes-and-vertical-slice/ ｜作者原文

---

## 5. 平台侧的时间与费用要求（只取官方）

**结论**

1. **Steam 上架费**：每个 app **$100 USD**（不可退），累计 Adjusted Gross Revenue 达 **$1,000** 后返还。
2. **Steam 商店页必须先存在**：新品发布前 Coming Soon 页至少挂 **2 周**；商店页审核 3–5 个工作日、建议提前 7 天提交；build 审核是另一条独立流程。
3. **Steam Next Fest**：要求商店页已公开 + 有可玩 demo；每个标题**只能参加一次**；可在开发早期就参加。
4. 这些是**发售侧**约束，不是开工约束——但它们会反向压缩 pre-production 的可用时间。
5. **itch.io 全部未核实**：官方文档在本机打不开，费用/审核/build 要求我一条都不敢下结论。

**证据**

- Steam Direct Fee："$100 USD (or equivalent) fee for each new app"；"not refundable, but will be recoupable … at least $1,000.00 Adjusted Gross Revenue"。https://partner.steamgames.com/doc/gettingstarted/appfee ｜平台文档【机制】
- Coming Soon 至少两周 + 审核 3–5 天 + 提前 7 天提交。https://partner.steamgames.com/doc/store/coming_soon ｜平台文档
- Release Process：商店页通过后才能提交 build；"coming soon" 满 2 周 + build 通过才能点 Release。https://partner.steamgames.com/doc/store/releasing ｜平台文档
- Next Fest 资格：商店页已发布公开、开节时有可玩 demo、不得在节前发售、只能参加一次。https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest ｜平台文档
- **itch.io 未核实**，仅留官方入口供你自行核对：https://itch.io/docs/creators/faq ｜https://itch.io/docs/creators/getting-started ｜（官方文档，本次未读取）

---

## 6. 规模参照：1–3 小时内容 ≈ 多少工作量？

**结论**

1. **未找到任何官方或一手来源**给出「1–3 小时内容 ≈ 多少工时 / 多少资产量」的换算。这条我给不出可信数字。
2. 能找到的只有**定性**的体量描述：Steam 官方说 demo 是「一小段可玩内容」；没有任何官方文档按小时数描述体量。
3. Game Jam 有固定时长上限，但官方规则页本次取不到（Global Game Jam 被 Cloudflare 拦截、Ludum Dare 页面需 JS）→ 未核实。
4. **SteamDB / SteamSpy / HowLongToBeat 都不是 Valve 官方数据**，按你「只用一手来源」的口径不能用。
5. 建议：这一项只能靠你自己记工时（做完一个 30 分钟的原型用了多少天）来估，别引二手数字。

**证据**

- Steamworks《Demos》只说 "a small playable portion"，无小时数/工时。https://partner.steamgames.com/doc/store/application/demos ｜平台文档
- 未找到：Steamworks、IGDA、GDC 任何给出内容时长↔工作量换算的一手页。

---

## 7. 未核实 / 未找到 清单（一次性交底）

| 事项 | 状态 |
|---|---|
| itch.io 收费、审核、页面与 build 要求 | **未核实**（本机无法访问 itch.io） |
| GDC 演讲正文（如《The Vertical Slice》） | **未核实**（GDC Vault 为 JS 应用） |
| IGDA 官方阶段模型 | **未找到**（IGDA 标准页无此内容） |
| 发行商/孵化器公开 pitch 模板 | **未找到**（多在门户/NDA） |
| alpha/beta/gold 的统一定义 | **未找到官方文本**（存疑） |
| 1–3 小时内容的工作量换算 | **未找到** |
| 「哪些产出物常被跳过」的统计 | **未找到**（只有个案自述） |
