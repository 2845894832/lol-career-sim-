# 一次对抗的概率结算模型：行业做法与一手来源

目标：给「胜率 = 0.5 + (能力均值 − 对手强度)/50 + 选项加成，夹 5%～95%」做校准参照。
标注：【一手】=官方规则/官方源码/原作者文档；【二手】=社区 wiki/攻略；【未核实】=打不开或没抓到原文。

## 结论

1. 公开的一手做法只有三类：**单骰 + 差值对目标数**（D&D、Fire Emblem、Wesnoth 全是）、**钟形骰/查表**（GURPS 3d6）、**差值过 logistic**（Elo/FIDE）。【事实】
2. 「差值 ÷ 常数 + 基准」最接近的先例是 **Elo 的 400 分尺度**，但它是非线性 logistic；纯线性差值直接当百分点的是 **Fire Emblem**（1 点 = 1%）。**没找到**「线性压缩 + 硬夹 5/95」同构的一手先例。【事实 + 未找到】
3. 线性 + 硬夹的代价是两端各一段**平台**：Δ≥22.5 之后全变 95%，这一段里能力差不再产生信息。行业一般用曲线或查表让每一点都还有意义，再单独留一个极小的必成/必败口子。【我的判断】
4. 分布：d20 每 +1 恒等于 5 个百分点，波动大；3d6 官方理由是「钟形更像人类学习曲线」，并**明确反对线性刻度**（SJG 原文）。【一手】
5. 上下限的官方依据是**叙事**不是数学：D&D SRD 说「有时命运眷顾或诅咒，让新手打中、老兵打空」；GURPS 让 17/18 永远失败，哪怕加值高到 +43。【一手】
6. 单掷的代价有工程解：Wesnoth 源码里有个「记账式 RNG」，让实际命中率逐步追平显示值。【一手】
7. 你的 /50 = 1 点换 2 个百分点，落在 FE（1 点=1%）和 d20（1 点=5%）之间；要校准，先定「多大能力差该等于 95%」，那个数才是常数。【需要你拍板】

## 一、「线性差值 + 夹上下限」的先例

- **D&D 5e SRD，攻击判定**【一手】：`d20 + 调整值 ≥ AC` 即命中，1 点 = 5 个百分点，本质是线性差值对目标数。→ https://api.open5e.com/v2/rules/srd_attacking_attack-rolls/?format=json
- **D&D 5e SRD，自然 1/20**【一手】：d20 掷 20 无视调整值与 AC 必中（重击），掷 1 必失。这是 5% 的硬上下限，不是 0/100。→ https://api.open5e.com/v2/rules/srd_attacking_rolling-1-or-20/?format=json
- **Fire Emblem**【二手，社区数据站】：命中 = 己方 Accuracy − 敌方 Avoid，Accuracy = Skill×2 + 武器命中 + 支援，Avoid = Speed + Luck + 地形；差值直接以「%」结算（1 点=1%），游戏内夹 0–100。FE1 更简单：命中 = 武器命中 + Skill −（地形 + 攻速）。→ https://beta.serenesforest.net/fire-emblem/Mystery_of_the_Emblem/Miscellaneous/Calculations ，https://serenesforest.net/shadow-dragon-and-blade-of-light/miscellaneous/calculations/
- **FIDE/Elo**【一手，官方手册】：200 分为一个 class interval；表 8.1.2 给差值→得分概率（0–3 分 → .50；375–391 → .91）。**没有硬夹**：0 分/1 分「必然是未定的，只记作 800」。→ https://handbook.fide.com/chapter/B022024
- **Battle for Wesnoth**【一手，源码】：`chance_to_hit = std::clamp(cth, 0, 100)`，基础值 = `100 − 敌方地形防御`，**只夹 0/100，没有 5/95**。→ https://github.com/wesnoth/wesnoth/blob/master/src/actions/attack.cpp
- 小结：**「差值÷常数」的先例是 Elo（除以 400 再过 logistic）；「夹 5%/95%」的先例是 D&D 的 1/20。两件事在公开规则里通常分开做，我没找到把它们合成一条线性公式的一手文本。**

## 二、d20 单掷 vs 3d6 钟形

- **D&D 5e SRD**【一手】：命中/豁免都是单颗 d20 + 调整值 vs 目标数；【优势/劣势】是「再掷一颗 d20，取高/取低」，且不叠加。→ https://api.open5e.com/v2/rules/srd-2024_d20-tests_advantage-disadvantage/?format=json
- **GURPS 官方为什么用 3d6**【一手，SJG 官方刊 *Roleplayer* #8，1988】：原文说六个面骰随手可得、3–18 的范围「正好落在 1–20 刻度上，均值 10.5 在中点」；**「最重要的因素是钟形曲线本身。钟形比线性系统更准确地模拟人类学习过程」**；并直接批评线性刻度：「在线性刻度上，把成功率从 90% 提到 95% 和从 15% 提到 20% 一样容易。」→ https://sphynx.sjgames.com/gurps/Roleplayer/Roleplayer8/GURPSTalk.html
- 同文给的 3d6 换算（可直接当「能力→胜率」表）：≤9 = 37.5%，≤11 = 62.5%，≤12 = 74.1%，≤13 = 83.4%，≤17 = 99.5%。
- **官方实测胜率**【一手，SJG *Pyramid* 文章】：「比对手高 1 级技能约 2/3 胜率，高 2 级约 80%，高 3 级就是一个带暴击/大失败的系统的上限了。」→ https://www.sjgames.com/pyramid/sample.html?id=1519
- 分布差别（算术，非引用）：d20 每 +1 恒 5 个百分点、两端各 5% 平台；3d6 中间一点约 12–13 个百分点、两端 3 和 18 各 0.46%，17–18 合计约 1.9%。【我的计算】

## 三、可核对的对抗公式（源码/官方）

- **Wesnoth**【一手】：每次攻击 = `num_blows` 次独立判定，`ran_num = get_random_int(0,99); hits = ran_num < cth`；伤害**不掷骰**，= 基础伤害 × 倍率（时段阵营 ±、领导力、抗性）；期望伤害 = `damage_done × cth × 0.01`，即方差全部来自命中。→ 同上 attack.cpp
- **Wesnoth 的补偿 RNG**【一手】：`biased_rng::roll_hit()` 用 `credit` 记账 —— `expected_hits = (chance_to_hit × strikes_left + credit)/100`，命中则 `credit += cth − 100`，未中则 `credit += cth`，让长程命中率收敛到显示值；cth 为 0/100 时不参与。这是「单掷让玩家觉得被坑」的官方工程解。
- **Fire Emblem**：见上（【二手】）。FE 的「真实命中率」（显示 90% 实际 98%）我**没找到一手出处**，只有社区称其用两次随机数（2RN），故不写数字。
- **Elo/Glicko**：FIDE 只公开了差值→概率表（【一手】）；常见写法 `We = 1/(1+10^(D/400))` 我没在 FIDE 正文里抓到原句（【未核实】）。Glicko 论文（glicko.net 上的 PDF）抓取失败（【未核实】），只能确认作者主页与文档存在：https://www.glicko.net/glicko.html

## 四、一次掷骰 vs 多次

- **多次**：Wesnoth 每次攻击含多段独立判定（`num_blows`），分布由 `attack_prediction.cpp` 算成完整 HP 概率矩阵，AI 用「P(杀死对方) − P(自己被杀)」比较战斗优劣（源码里 `better_combat`）。【一手】
- **单掷 + 第二个骰**：D&D 优势/劣势是「加一颗 d20 取高/取低」，官方把它定义为「环境有利/不利」，不是数值加成 —— 用分布而不是加法来表达强弱。【一手】
- **单掷让极端结果更常见、玩家觉得不公平**：我没找到官方文本直接这么说。【未找到】Wesnoth 的 `biased_rng` 与代码注释「new experimental prng mode」是目前最硬的一手证据（存在即承认问题）。
- **XCOM 的隐藏加成**：【未找到官方出处】。只有 Steam/StackExchange 讨论（【二手】）。Firaxis 的 Jake Solomon 有一篇 Gamasutra 访谈《on the careful use of randomness in XCOM 2》，archive.org 抓取失败（【未核实】）。

## 五、上限为什么存在（官方原文）

- **D&D SRD**【一手】原文：「Sometimes fate blesses or curses a combatant, causing the novice to hit and the veteran to miss.」—— 保留「新手可能赢老兵」的叙事，这是 5% 存在的理由。
- **GURPS**【一手】：技能再高，17/18 仍是失败/大失败（FAQ 3.4.2.4 的暴击失败阈值 17/18）；FAQ 3.2.12 那句更直白：「哪怕给到 +43（相当于行星地球那么大），你还是可能掷出 18。」→ https://www.sjgames.com/gurps/faq/FAQ4-3.html
- **GURPS 另一端**【一手，FAQ 3.1.3】：防御骰「总是可以尝试，掷 3 或 4 仍是暴击成功」，即使目标数低于 3；但 -7 或更差时，连掷 3 都算大失败。即两端各留一个不随数值变化的极小窗口。
- **FIDE**【一手】：从不用 0/1，1.0 与 0.0「只记作 800」，即在制度上不承认「必胜」。

## 没有数据的地方

- 「线性差值 ÷ 常数 + 硬夹 5/95」的**直接一手先例**：没找到。最接近的两半分别是 Elo（÷400，logistic，无硬夹）和 D&D（5% 硬夹，但不是差值压缩）。
- XCOM 隐藏命中加成的**官方**说明：未找到；Gamasutra 访谈原文：未核实（archive 抓取失败）。
- FIDE 正文里的 `We = 1/(1+10^(D/400))` 原句：未核实（页面被截断，只拿到表格）。
- Glicko / Glicko-2 论文正文：未核实（PDF 无法解析）。
- Fire Emblem 的 2RN「真实命中」：只有社区说法，未找到一手。
- Wesnoth 官方 wiki/manual 页面（wiki.wesnoth.org）：多次抓取失败，改以 GitHub 源码为一手依据。
