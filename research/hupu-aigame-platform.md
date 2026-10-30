# 虎扑 AI Game 平台 / AI 工坊：上传作品的技术要求与流程

覆盖：2026-05-27「虎扑 VC 作品广场」官方公告、2026-08-26 与 09-20 两篇开发者内测招募帖、投稿站 shaper.hupu.com 的官方文档（产品简介/快速上手/常见问题）与其《AI互动作品创作者合作协议》、AI工坊（bbs.hupu.com/871）内开发者公开自述与已上线作品页。
不覆盖：内测报名表单的具体题目（问卷页需交互填写，未抓到题面）、人工审核的实际耗时（官方未披露）、平台技能包内部实现（需登录下载）。

## 1. 作品形态

结论：是**网页**。上传的是"可直接运行的前端产物"（`.zip` / 单个 `.html` / 拖拽文件夹），压缩包根目录或唯一一级子目录下必须有 `index.html`，不是源码仓库。平台另有"技能包 + AI 对话"路线，不写代码也能生成页面，但产物仍是同一套静态前端。

- 【官方文档】上传格式与结构要求：`.zip`、`.html`/`.htm`、文件夹仅拖拽；入口 `index.html` 必需；资源用相对路径（`./assets/...`，构建工具 base 设 `./`）。URL: https://shaper.hupu.com/docs/faq 、https://shaper.hupu.com/docs/getting-started
- 【官方文档】"上传可直接运行的前端产物，不是源码仓库"；推荐做法是本地用 AI 做完、把 `h5` 目录打成 `.zip`。URL: https://shaper.hupu.com/docs/faq
- 【官方公告 2026-05-27】旧通道（VC 作品广场）只部署**单个 .html**，纯前端静态包"可视情况协助转换成单个 .html，但不保证成功"。URL: https://bbs.hupu.com/639560769.html
- 【合作协议】"全部 AI 互动作品的素材、代码、交互逻辑、成品压缩包均由您独立完整制作"。URL: https://shaper.hupu.com/agreements/creator-cooperation

## 2. 屏幕方向与尺寸

结论：官方文档**没有**规定方向、固定画布尺寸或设计稿宽度（未找到）。实际约束是三条：预览就是手机竖屏框、官方游戏模板按"手机竖屏布局"写、线上页面 head 被注入 `width=device-width … viewport-fit=cover` —— 所以要按移动端自适应做，不能依赖固定像素画布。

- 【官方文档】第 5 步："上传并通过自动检测后，可在右侧**手机框**预览；点「扫码预览」用虎扑 App 扫码在真机查看"。URL: https://shaper.hupu.com/docs/getting-started
- 【平台内模板文案】塔防守城模板的 UI 段写"采用**手机竖屏**布局。顶部……底部提供 4 个防御单位按钮"（平台自带游戏模板，非第三方）。URL: https://shaper.hupu.com/ （站点前端包内模板库；属平台自有内容）
- 【线上作品页实测】已发布应用 head：`<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">`，另注入 CSP 与 `spm-id`。URL: https://activity-static.hupu.com/shaper/published/app_610ccec57c/index.html （出处帖 https://bbs.hupu.com/643360538.html ）
- 【未找到】任何"必须 750×1334""横屏/竖屏二选一""画布尺寸"的成文规定。

## 3. 素材限制与包体上限

结论：图片、音频、视频都能带，有明确额度：单个 ≤25MB、合计 ≤100MB；字体/WASM/数据等其它文件合计 ≤100MB。整包 ≤50MB，单个代码类文件（如 `index.html`）≤5MB，单包最多 300 个文件。

- 【官方文档·限制表】上传格式 `.zip`/`.html`/`.htm`；应用包总大小 ≤50MB；图片/音频/视频单个 ≤25MB 且合计 ≤100MB；文件数 ≤300；单个代码类文件建议 ≤5MB；其它文件合计 ≤100MB。URL: https://shaper.hupu.com/docs/faq
- 【官方文档·同额度的正文表述】"单个 HTML（及代码类文件）不超过 5MB""图片、音频和视频：单个不超过 25MB，合计不超过 100MB""单个包最多 300 个文件"。URL: https://shaper.hupu.com/docs/getting-started
- 【官方文档】应用 Logo 必填：PNG/JPEG/WebP、1:1、建议图上带应用名。URL: https://shaper.hupu.com/docs/faq

## 4. 是否需要联网后端 / AI 调用

结论：**不需要**，也**不能**指望平台给你后端。官方明确不部署后端服务、数据库、接口、登录鉴权；平台以"技能"形式提供部分能力（赛事与球员数据、投票、打分、抽奖、积分）。自己调外部 API 只能走纯前端 https 请求；平台不提供大模型 API。

- 【官方公告 2026-05-27】"涉及后端服务、数据库、接口服务、登录鉴权或必须依赖运行环境的项目，暂时无法部署"。URL: https://bbs.hupu.com/639560769.html
- 【官方文档】技能包＝平台按能力准备的能力包，"例如赛事与球员数据、投票、打分、抽奖、积分"；"部分虎扑技能需真机才能完整体验"。URL: https://shaper.hupu.com/docs/faq
- 【线上作品页实测】CSP 含 `connect-src 'self' https: wss:`——https/wss 外呼技术可行，明文 http 被禁。URL: https://activity-static.hupu.com/shaper/published/app_610ccec57c/index.html
- 【合作协议】禁止"私自接入境外未备案 AI 模型用于创作投稿"；广告、外链、充值导流只能由平台接入。URL: https://shaper.hupu.com/agreements/creator-cooperation

## 5. 上架流程与耗时

结论：报名（WJX 问卷）→ 资格审核 → **3 个工作日内**工作人员联系 → 拿邀请码登录 shaper.hupu.com → 建应用、下载技能包 → 本地用 Codex / Claude Code / Cursor 开发 → 上传 → 自动检测 → 补 Logo 与描述 → 提交人工审核 → 通过后自动发布 → 「集市 → 我的」查状态。报名 3 个工作日有明文；人工审核时长**未找到**。

- 【官方招募帖 2026-08-26】"提交报名信息后，工作人员会审核是否符合内测资格，符合资格的 JR 会由工作人员在**3 个工作日**内与你取得联系"；表单 https://v.wjx.cn/vm/myswiGK.aspx 。URL: https://bbs.hupu.com/642103239.html
- 【官方公告 2026-09-20】同一套说法，表单换成 https://v.wjx.cn/vm/OFwSW8f.aspx ；并给出 AI 工坊入口 https://aiworks.hupu.com/ 。URL: https://bbs.hupu.com/642512643.html
- 【官方文档】3 步流程：STEP01 环境准备（下载基础技能包，必需）→ STEP02 上传应用包（名称/描述/Logo/包体）→ STEP03 提交审核；"审核通过后应用会自动发布"；状态机：自动检测中→可提交审核→审核中→已退回修改→已发布；已发布可发新版本，过审前线上仍是旧版。URL: https://shaper.hupu.com/docs/getting-started
- 【官方公告 2026-05-27｜另一条通道，别混淆】VC 作品广场是"话题下发帖投稿或发 .html 到邮箱"，审核通过后"**2 个工作日**内上线到活动页面"。URL: https://bbs.hupu.com/639560769.html

## 6. 内容规定与 IP / 版权态度

结论：硬约束在《创作者合作协议》和提审前的自动检测里：素材/代码/形象/剧情必须原创或已获完整可转授权；作品一律按 AI 生成合成内容处理（平台加"AI 生成"角标 + 元数据溯源，不得遮挡）；禁止私域导流、第三方广告/外链/充值入口。关于真实选手名/战队名：**没有查到"禁止"的明文**，反而有在架先例。

- 【合作协议】3.2.1 原创或已取得完整可转授权、无侵权风险；3.2.2 平台可加"AI 生成"角标并写入隐式溯源标识，遮挡/篡改即严重违约；6.1.2 禁止无证经营、私域导流、第三方广告/外链/充值；6.1.7 禁止私接境外未备案模型；5.x 著作权归创作者但投稿即免费授予平台全球永久不可撤销可转授权，维权以平台名义且所得归平台。URL: https://shaper.hupu.com/agreements/creator-cooperation
- 【平台自动检测项｜安全+通用+性能+功能】安全类含"第三方 SDK 引入、外部资源、动态代码执行、跳转/外链/下载、请求设备权限"；通用类含"XSS/DOM 注入、敏感信息泄露、明文传输、存储安全、硬编码密钥"；功能类含"移动端适配、交互语义、可访问性、运行稳定性、状态容错"。URL: https://shaper.hupu.com/ （提审页"自动检测"结论分类，站点前端包内）
- 【IP 先例·官方口径】招募帖把《峡谷这一生》（LoL 题材）与《我创造的完美球员》《82-0》并列为平台已有小游戏。URL: https://bbs.hupu.com/642103239.html
- 【IP 先例·在架作品】AI工坊在架的《替补选手》是 LoL 生涯模拟，角色用虚构名（Volt）、战队用真实缩写（TT），帖子被标注"含虚构演绎内容"。URL: https://bbs.hupu.com/642922914.html
- 【IP 先例·NBA 真名】AI工坊版内大量真实球员名作品（"把欧文放进2011年""完美球员"等），说明体育真名+虚构演绎是常见做法。URL: https://bbs.hupu.com/871
- 【社区通用底线】政治敏感、色情、血腥暴恐、赌博、造谣、未授权广告与侵权资源均禁止。URL: https://bbs.hupu.com/26624652.html

## 7. 分成与收费

结论：用户端**免费**，没有付费下载/内购。唯一变现是 IAA 广告：由创作者在提交时**自主勾选**是否开启，平台统一接广告联盟；不开启就纯免费展示、零收益。分成按自然月结算，业务结束后约 15 个工作日审核，月收入 8 万元以内由第三方代扣税后打款。

- 【合作协议 1.5】"是否开启广告 IAA 商业化由您自主决定……若您选择不开启广告，作品仅免费展示，无任何广告收益结算"。URL: https://shaper.hupu.com/agreements/creator-cooperation
- 【合作协议 2.1–2.4】自然月结算、无需单独提交材料、数据异议 3 个工作日内提、审核周期一般 15 个工作日、8 万元以内由第三方代扣代缴后打款、税费创作者自担。URL: https://shaper.hupu.com/agreements/creator-cooperation
- 【合作协议 3.1.3 / 7.3】平台可提前 7 天通知无责单方终止；可单方面永久关停 AI 工坊板块（关停后 60 日内结清合规收益）。URL: https://shaper.hupu.com/agreements/creator-cooperation
- 【官方文档】收益口径含糊："有机会……可结合平台激励活动或后续开放的变现能力获取收益，具体规则以当期说明为准"。URL: https://shaper.hupu.com/docs/faq

## 没查到的

- 内测报名表单的具体题目与筛选标准（问卷页需交互作答，抓不到题面）。
- 人工审核的实际时长与驳回率（文档只说"等待平台审核"，无 SLA）。
- 技能清单全文与各技能能力边界（技能包需登录后下载）。
- 是否有"必须竖屏/禁止横屏"的成文条款；是否允许 canvas 固定尺寸（只能从模板与线上页面反推）。
- 真实选手名/战队名的**书面**授权规则；目前只有先例，没有规则文本。
- 分成比例（协议只写"后台展示预估收益"，未见百分比）。
