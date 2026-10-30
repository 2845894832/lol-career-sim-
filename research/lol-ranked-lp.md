# 英雄联盟 排位段位与 LP 规则（2026 年度口径）

> 用途：把现实段位映射到游戏内的隐藏进度条。口径 = **2026 年度（当前）**，历史变更单列 §5。
> 标注：【一手】Riot 官方支持页；【二手】Wiki/攻略站；【未核实】原页打不开、仅见转录；【未找到】官方未公布。
> 每条结论的 URL 与类型见下方 §1–§5 对应条目。

## 结论

1. 段位共 10 个：黑铁 < 青铜 < 白银 < 黄金 < 铂金 < 翡翠 < 钻石 < 大师 < 宗师 < 王者。
2. 黑铁～钻石各 4 个小段（IV→I），共 28 小段；每小段 100 LP，满 100 自动进下一小段且余量保留；每大段 = 400 LP。
3. 黑铁 IV 0 LP → 大师 0 LP = 28 × 100 = **2800 LP**（计算值，非官方数字，可直接当进度条满值）。
4. 晋级赛全部取消：2021 赛季起取消小段晋级赛，2023 年 7 月（13.14 补丁）取消大段晋级赛；黄金 I 满 100 LP 直接进铂金 IV。
5. 单场 LP 无官方固定值，由 MMR 与当前段位的差距决定；官方给过的是基准：2024 年翡翠以下 25（由 28 下调），2026 年 4 月起大师以上 30（实际约 +35/-25 ~ +25/-35）。
6. 普通段位 2026 赛季基准约 ±20，目前只有二手记录，官方原文未打开（见 §2）。
7. 降级：同大段内输光 LP 即掉小段；跨大段有保护，掉段后 LP 置 25/50/75（按 MMR 判断）。
8. 大师以上无小段，直接按 LP 排名；大师 0 LP 起，宗师/王者 = 赛区前 N 名 + LP 底线，每日刷新且有人数上限。
9. 赛季：2026 年度分 3 个赛季（1/4/8 月开始），年内不重置、跨年软重置；衰减从钻石开始（50 LP/天），大师以上 75 LP/天。

## 1. 段位结构

- 10 个段位；黑铁～钻石每段 4 个小段（IV 最低 → I 最高）——https://support.riotgames.com/en-us/league-of-legends/gameplay/ranked-tiers-divisions-and-queues （一手，更新于 2026-05-07）
- 大师/宗师/王者是"单一分区"（single division），无小段——https://support.riotgames.com/en-us/league-of-legends/gameplay/master-grandmaster-and-challenger-the-apex-tiers （一手）
- 每小段 100 LP："generally need 100 LP to climb up each division"——https://support.riotgames.com/en-us/league-of-legends/gameplay/mmr-rank-and-lp （一手）
- 定级赛：每个队列 5 场，最高只能定到钻石 III，定级赛输了不掉 LP——https://support.riotgames.com/en-us/league-of-legends/gameplay/placements-promotions-series-demotions-and-decay （一手，2026-05-29）
- 同一篇旧文（2025-05）写"新年最高从翡翠 I 开始"，与上一条的钻石 III 冲突，疑为过时表述——https://support.riotgames.com/en-us/league-of-legends/rewards/ranked-years-seasons-and-end-of-season-rewards （一手/存疑）

## 2. 单场 LP 变化

- 机制：MMR 高于段位 → 赢得多、输得少；低于段位 → 赢得少、输得多；连胜没有独立加成，只是把 MMR 拉高后间接放大收益——https://support.riotgames.com/en-us/league-of-legends/gameplay/mmr-rank-and-lp （一手）
- 2023 年翡翠～大师段约 50% 玩家遇到"负收益"（+21/-29）；2024 年官方把翡翠以下 LP 从 28 下调到 25——https://www.leagueoflegends.com/en-us/news/dev/dev-split-two-ranked-update/ （一手公告，本网络打不开，经 Wiki 转录 = 未核实原文）
- 2026 赛季普通段位基准约 ±20（无引用）——https://wiki.leagueoflegends.com/en-us/Rank （二手）
- 2026-04 Apex 重置公告：基准提高到 ±30，预期区间 +35/-25 ~ +25/-35——https://www.leagueoflegends.com/en-us/news/dev/dev-apex-tier-ranked-reset/ （一手公告，同上，未核实原文；转录见上条 Wiki）
- 补位/优先位（Aegis of Valor）胜利时 LP 翻倍——https://support.riotgames.com/en-us/league-of-legends/gameplay/mmr-rank-and-lp （一手）
- 队友挂机/送人头被判违规时可能全额退还该场 LP（Consolation LP，每周有次数上限）——同上 （一手）
- 与人双排时 LP 收益可能略低——同上 （一手）
- 推算（非官方）：按普通段位基准 20 LP/场，净胜 5 场 ≈ 升 1 小段（100 LP），与官方"100 LP 一小段"配套可直接用来定进度条速度。
- 官方"每场固定 ±X"的数字：未找到（官方只解释机制与基准，不承诺固定值）。

## 3. 晋级 / 降级

- 小段晋级：满 100 LP 自动进下一小段，余量保留（"hang on to any leftover LP"）——https://support.riotgames.com/en-us/league-of-legends/gameplay/placements-promotions-series-demotions-and-decay （一手）
- 大段晋级：在 I 段拿满 100 LP 自动进下一段 IV，不需要任何系列赛——同上 （一手）
- 跨大段降级：有保护；掉段后 LP 置 25 / 50 / 75（按 MMR 与段位差判断）——同上 （一手）
- 晋级保护盾：升入青铜～钻石后 10 场、升入大师后 3 场内不会掉段——https://wiki.leagueoflegends.com/en-us/Rank （二手）
- 历史：小段晋级赛 2020-11（V10.23，即 2021 赛季）取消；大段晋级赛 2023-07（V13.14，2023 Split 2）取消——https://wiki.leagueoflegends.com/en-us/Rank （二手）

## 4. 大师以上（Apex）

- 大师/宗师/王者共用一条榜；LP 无上限，赢多少涨多少——https://support.riotgames.com/en-us/league-of-legends/gameplay/master-grandmaster-and-challenger-the-apex-tiers （一手）
- 宗师/王者每天按当地时间 0 点重排一次（"rotating twenty-four hour schedule"）——同上 （一手）
- 人数上限（单双排，按赛区）：NA / EUW / KR / SEA / OC = 宗师 700、王者 300；BR / EUNE / LATAM-N / LATAM-S / TR = 500 / 200；JP / RU = 100 / 50——同上 （一手）
- 最低 LP 底线：宗师 ≥200 LP、王者 ≥500 LP；该段在支持页被大表格截断，只有二手来源——https://wiki.leagueoflegends.com/en-us/Rank （二手，未核实原文）
- 衰减：大师以上 75 LP/天；每打 1 场存 1 天，最多存 14 天；因不活跃衰减会掉回钻石 II——https://support.riotgames.com/en-us/league-of-legends/gameplay/master-grandmaster-and-challenger-the-apex-tiers （一手）
- 钻石衰减：50 LP/天；每场存 7 天，最多 28 天——https://support.riotgames.com/en-us/league-of-legends/gameplay/placements-promotions-series-demotions-and-decay （一手）
- 大师起点 0 LP（实际会带进位余量）——https://wiki.leagueoflegends.com/en-us/Rank （二手）

## 5. 赛季与历史变更（时间口径）

- 2019 赛季：新增黑铁与宗师，小段由 5 个减为 4 个——https://wiki.leagueoflegends.com/en-us/Rank （二手）
- 2021 赛季（V10.23）：取消小段晋级赛——同上 （二手）
- 2023 Split 2（V13.14，2023-07）：新增翡翠段位，同时取消大段晋级赛——同上 （二手）
- 2024 赛季（V14.1）：改为 3 个 split；LP 28→25（翡翠以下）——https://www.leagueoflegends.com/en-us/news/dev/dev-split-two-ranked-update/ （一手，未核实原文）
- 2025 赛季：改为"一年只重置一次 + 3 个赛季"，Apex 的 MMR 软重置更温和——https://www.leagueoflegends.com/en-us/news/dev/dev-ranked-update-season-one-2025/ （一手，未核实原文；转录见 Wiki）
- 2026 年度：3 个赛季（1/4/8 月），年内进度延续、跨年重置——https://support.riotgames.com/en-us/league-of-legends/rewards/ranked-years-seasons-and-end-of-season-rewards （一手）
- 2026-04：NA/EUW/EUNE/BR/LAN/TR 的大师以上做了一次硬重置，并把 LP 基准提到 ±30——https://www.leagueoflegends.com/en-us/news/dev/dev-apex-tier-ranked-reset/ （一手，未核实原文）

## 6. 未核实 / 未找到

- 未核实：leagueoflegends.com 的 dev 公告在本网络被重定向到腾讯站，原文打不开；文中 25 / 30 / ±20 这些数字来自 Wiki 转录，未与原文逐字核对。
- 未找到：官方"每场胜利/失败固定 ±X LP"的数字（官方只给机制，不给固定值）。
- 未核实：宗师/王者 200 / 500 LP 的最低底线（支持页该节被赛区表格截断，仅二手）。
- 未找到：宗师/王者的"固定 LP 门槛"（实际是"赛区前 N 名 + LP 底线"的动态线，每天变）。
