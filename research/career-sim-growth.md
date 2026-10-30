# 球员能力成长与衰退：一手来源调研

> 调研日期 2026-10-29。只收一手（官方手册 / 官方 FAQ / 开发者官方博客 / 开源代码）。标「二手」的只作线索，不作依据。

## 结论

1. **FM 没有公开的 CA/PA 文档。** 官方站点 sitemap（2222 条 URL，含 `/help`、`/help/tutorials`）里检索不到 CA/PA、成长速率或衰退年龄；官方论坛（`community.sports-interactive.com`、`community.sigames.com`）一律返回 Cloudflare 403 → SI 员工发言**未核实**。
2. 本次能核实到的一手模型只有四个：OOTP（官方手册）、EA SPORTS FC 27（官方 Pitch Notes）、NBA 2K26（官方 Game Guide）、ZenGM（开源代码）。
3. **上限结构**：OOTP 是 OVR/POT 双值，且都"相对同位置联盟平均"；EA FC 27 把潜力做成会随表现漂移的 Dynamic Potential；ZenGM 根本不存 PA，潜力由"当前 OVR + 年龄"回归/蒙特卡洛估算。
4. **年龄曲线形状**：OOTP 官方只定性说"年轻会成熟、老将会退化，与当代 MLB 一致"，可调 aging modifier；EA FC 27 用 6 种 Growth Profile 取代统一曲线；ZenGM 代码是分段台阶（≤21 +2、≤25 +1、27 归零、之后 −1/−2/−3/−4）。
5. **衰退起点**：足球科学一手给"峰值 25–26 岁、32 岁后显著下滑"（Branquinho 2025）；ZenGM 27 岁转负；2K 不给年龄曲线，只给属性上限。
6. **训练 vs 潜力**：OOTP 两者都算，并明确"高潜力未必兑现"；EA FC 27 反向改（教练不再直接加属性，只影响潜力评估精度）；ZenGM 教练只把年度变化乘约 ±9%。
7. 一手来源里没有"18 岁入行、8 年生涯"这种短周期样本，27 岁前后见顶属于**可辩护但需你拍板**的参数（此句是判断，不是事实）。

## 1. Football Manager（Sports Interactive）

- **官方手册 / FAQ：未找到。** 检索了官方 sitemap（https://www.footballmanager.com/sitemap.xml ，2222 条）与官方教程页（https://www.footballmanager.com/help/tutorials ），无 CA/PA 说明、无成长速率、无衰退年龄。
- **官方论坛：未核实。** https://community.sports-interactive.com/forums/topic/87746-current-ability-potential-ability-and-current-potential-ability/ 、https://community.sigames.com/forums/topic/572524-can-potential-ability-change/ 均被 Cloudflare 403 拦截，无法读到 SI 员工原帖。
- **二手（仅线索）**：fminside 指南称 PA 为上限、CA 受训练/比赛/年龄影响（https://fminside.net/guides/positional-guides/76-current-potential-ability ）；NGA 帖讨论"固定潜力/活动潜力"（https://ngabbs.com/read.php?tid=38087592 ）。
- 因此"CA 涨到 PA 封顶、训练加速、年龄到点回落"这套说法，本次**没有一手证据**，只能当二手。

## 2. Out of the Park Baseball（官方手册）

来源：http://manuals.ootpdevelopments.com/index.php?man=ootp24&page=player_development （官方手册，类型：官方文档）

- 官方列出的发展因素：教练/经理评分、上场时间、潜力与个人特质、年龄、挑战、伤病、春训、运气、发展 modifier。
- 潜力：「Very talented players often (but not always) develop more quickly... You might be baffled by the high-potential player who fails to live up to expectations.」
- 上场时间：「Minor league players who get little playing time might not develop as quickly as others. However, major league players... develop normally even without playing time.」（只在小联盟生效）
- 年龄：「Younger players might mature with age. Older players' skills might begin to diminish. Not all players will lose their skills at the same time」，并称「Players age in a model that is relatively consistent with modern-day baseball players」，可用 player aging modifier 调。
- 挑战：「a player who is tearing up Double A... might not be developing very quickly, because he isn't being challenged」；越级上场也可能伤发展。
- 运气：「Sometimes, the light bulb inside a player's head will just go on... Some players will never live up to their potential.」

OVR/POT 定义：http://manuals.ootpdevelopments.com/index.php?man=ootp24&page=overall_rating ——「OVR ratings are based exclusively on underlying actual ratings... compared to the average actual ratings for all players at that position or role」，POT 同理用 potential ratings。

退役：http://manuals.ootpdevelopments.com/index.php?man=ootp24&page=player_retirement ——「There is no preset age when this will happen」，且只在赛季末发生。

## 3. EA SPORTS FC 27 生涯模式（官方 Pitch Notes，2026-07-31）

来源：https://www.ea.com/games/ea-sports-fc/fc-27/news/pitch-notes-fc27-career-mode-deep-dive （类型：官方开发者博客）

- **Growth Profiles**：新增 6 种成长档案决定"能力平台期"，理由是「Historically, player development followed a relatively standardised trajectory... Real football rarely works that way」；「Some players break through early and peak young. Others continue improving into their late twenties.」
- **Dynamic Potential**：上限会动——「players who consistently exceed expectations can raise their ceiling. Likewise, prolonged periods of poor Form can lead to a loss of development momentum.」
- **教练权重下调**：「Coaches no longer directly improve player Attributes but will contribute to understanding and projecting player Potential」，教练水平只决定"能否估准上限"。

## 4. NBA 2K26（官方 Game Guide）

来源：https://nba.2k.com/2k26/game-guide/myplayer-builder/ （类型：官方游戏指南）

- Cap Breakers：「a way to push your build's attribute potential beyond the cap」；每个属性最多用 5 次，永久生效不可重分配。
- 上限本身还受建模限制：「The max potential rating of attributes can also be limited by the height, weight, and wingspan of your build.」
- 加点收益递减设定：「raise your highest-rated and strongest attributes by a single point, but if you choose to apply them to a lower-rated attribute, you'll see an even greater boost.」
- 注意：这是"上限可被外部奖励突破"的设计，没有年龄衰退曲线。

## 5. 开源代码：ZenGM（足球/篮球/棒球/冰球同源）

仓库：https://github.com/zengm-games/zengm

- 年度基础变化（足球）：https://github.com/zengm-games/zengm/blob/master/src/worker/core/player/developSeason.football.ts
  「age ≤21 → +2；≤25 → +1；≤27 → 0；≤29 → −1；≤31 → −2；≤34 → −3；否则 −4」，再叠加噪声（≤23 岁 `truncGauss(0,5,-4,15)`；≤25 岁 `truncGauss(0,5,-4,7)`；其后 `truncGauss(0,3,-2,3)`）。
- 训练权重：`val *= 1 + sign(val) * coachingEffect(level)`，而 `coachingEffect = 0.09 × levelToEffect(level)`（https://github.com/zengm-games/zengm/blob/master/src/common/budgetLevels.ts ）→ 教练最多把年度变化拉动约 ±9%。
- 分属性修正：速度 27 岁后 −2、30 岁后 −4；耐力 23 岁前 `+uniform(0,9)`；技术/球商用 iqFormula（≤21 +3、≤23 +2、27 归零、31 后 +2 以减缓下滑），且 19 岁单年上限可到 +32（`7 + 5 × (24 − age)`）。
- 没有 PA：单属性硬上限 100（`limitRating`），潜力由 `potEstimator` 估算，例如篮球线性式 `72.31 − 2.33 × age + 0.833 × ovr`，`age ≥ 29` 时直接返回当前 ovr（https://github.com/zengm-games/zengm/blob/master/src/worker/core/player/potEstimator.ts ）。

## 6. 年龄曲线的一般形状（体育科学一手）

- Branquinho et al. 2025, *J Funct Morphol Kinesiol* 10(4):385（98 名职业球员、5203 场、Catapult 追踪）：峰值速度 25.7 岁、耐力 24.8 岁、爆发力 26 岁；「players over 32 years experienced declines in high-intensity and explosive actions, while endurance remained relatively stable」；17–26 岁整体最高。https://doi.org/10.3390/jfmk10040385
- Allen & Hopkins 2015, *Sports Medicine*（系统综述）：峰值年龄按项目差异极大——爆发/冲刺类约 20 岁（游泳）到 27 岁（投掷），耐力类 20–39 岁（超长距离自行车）。https://doi.org/10.1007/s40279-015-0354-3
- 提醒：这两项量的是体能/成绩，不是游戏属性，迁移时需自己换算。

## 7. 训练 vs 潜力：一手说法对照

| 来源 | 上限 | 训练/教练 | 上场时间 |
| --- | --- | --- | --- |
| OOTP | POT，且"高潜力未必兑现" | 教练评分影响发展 | 小联盟缺时间会慢 |
| EA FC 27 | Dynamic Potential，表现可抬高 | 不再加属性，只提评估准度 | 隐含在"表现"里 |
| ZenGM | 无 PA，单属性封顶 100 | 年度变化 ×(1±9%) | 不建模 |
| NBA 2K26 | 属性 cap + Cap Breaker 突破 | 训练/奖励加点 | — |
| FM | 未核实 | 未核实 | 未核实 |

## 未找到 / 未核实

- FM 的 CA/PA 官方定义、成长速率、衰退起始年龄：官方无文档；论坛 403 → 未核实。
- FIFA/EA 旧世代（FC24 及以前）的成长公式：未查。
- MLB The Show、NBA 2K MyCAREER 的年龄衰退曲线：未找到官方文档。
- 电竞选手的峰值年龄/衰退曲线：未找到一手估计，只找到生涯长度与相对年龄效应研究（如 2025 年 esports career longevity 论文）。
