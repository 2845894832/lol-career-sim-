# -*- coding: utf-8 -*-
"""docs/15-16-17-工程化三件-讲懂与选型.docx —— 决策地图 15/16/17 的材料。

要求：讲懂 + 摆选项与代价，**不替用户决定**。
事实来源（2026-11-05 核对）：
- CI：无 .github/ 目录；git ls-files '*.yml' 仅 pnpm-lock.yaml、pnpm-workspace.yaml
- 命令：package.json scripts（typecheck/test/build/build:slice/smoke/batch）
- 构建：vite.config.ts（viteSingleFile）；dist/index.html 88521 B、dist-slice/index.html 89300 B
- 网络：grep fetch/XHR/sendBeacon/WebSocket 于 src/ 与 index.html，0 处
- 错误捕获：window.onerror / unhandledrejection，0 处
- 存档：src/core/save.ts 三个函数均 try/catch
- 平台：虎扑官方账号 2026-05-27 帖 https://bbs.hupu.com/639560769.html（只在文档里引用，不作规则背书）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import docx_kit as k


# docx_kit.rich 只认 **粗体**；本文大量出现 `代码名`，让它以等宽字体落地，而不是留反引号。
_TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def _rich(p, s, size=10.5, color=k.K):
    for part in _TOKEN.split(s):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            k.set_run(p.add_run(part[2:-2].replace("`", "")), size, True, color)
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = p.add_run(part[1:-1])
            r.font.size = Pt(max(size - 0.5, 6.5))
            r.font.name = "Consolas"
            r.font.color.rgb = color
            rf = r._element.get_or_add_rPr().find(qn("w:rFonts"))
            if rf is not None:
                rf.set(qn("w:eastAsia"), "Consolas")
        else:
            k.set_run(p.add_run(part), size, False, color)


k.rich = _rich

OUT = os.path.join(ROOT, "docs", "15-16-17-工程化三件-讲懂与选型.docx")

# w:shd 之后允许出现的 pPr 子元素（OOXML 规定的顺序）
_AFTER_SHD = (
    "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
    "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd",
    "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents",
    "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
    "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
    "w:sectPr", "w:pPrChange",
)


def code_block(doc, text, size=8.5):
    """等宽字体 + 浅灰底，逐段上色（不用表格，免得自检时和真表格混在一起）。"""
    for line in text.strip("\n").split("\n"):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = 1.12
        pf.left_indent = Cm(0.3)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "F2F5F9")
        pPr.insert_element_before(shd, *_AFTER_SHD)
        r = p.add_run(line if line else " ")
        r.font.size = Pt(size)
        r.font.name = "Consolas"
        rf = r._element.get_or_add_rPr().find(qn("w:rFonts"))
        if rf is not None:
            rf.set(qn("w:eastAsia"), "Consolas")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


YAML = """
name: ci
on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 10
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm run typecheck
      - run: pnpm test
      - run: pnpm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/index.html
"""


def main():
    doc = k.new_doc("15–17 工程化三件 · v0.1 · 2026-11-05")
    k.title(
        doc,
        "CI · 自动部署 · 线上监控",
        "三件事讲懂 + 每条路的代价 · 不替你选 · v0.1 · 2026-11-05",
    )

    k.note(
        doc,
        "这份文档只做两件事：**把三件事讲懂**，**把选项和代价摆齐**。没有替你选——凡标「待你定」的，都等你点一个。"
        "事实核对日 2026-11-05，命令、路径、数字都来自仓库本身；可复现的核对命令在附录。",
    )

    # ---------------- 一 ----------------
    k.h1(doc, "一", "三件事，一眼看完")
    k.para(doc, "先用一句话说现状：**构建手动、发布手动、线上是瞎的**。三件都不是「必须做」，但每一件不做都有明确后果。")
    k.table(
        doc,
        ["事项", "一句话是什么", "现在状态（附证据）", "不做会怎样"],
        [
            ["CI（持续集成）",
             "每次 push，机器自动跑类型检查 / 测试 / 构建，错了当场红叉",
             "**0 个**。仓库没有 `.github/` 目录；`git ls-files '*.yml'` 只返回 `pnpm-lock.yaml`、`pnpm-workspace.yaml`，没有任何流水线文件",
             "漏跑一条命令就把坏包传上去；4.3 的 R9 记的就是这条"],
            ["自动部署",
             "构建完自动把产物送到「能被打开的地方」",
             "**0 步自动**。产物 `dist/index.html` 靠人手动上传或发邮件；平台没有公开 API（详见 3.1）",
             "每次投稿都要人工确认「文件对不对、是不是最新那份」"],
            ["线上监控 / 埋点",
             "玩家那边白屏、报错，你能知道；以及打开数、留存",
             "**0 处网络请求、0 处全局错误捕获**。`grep -rnE \"fetch\\(|XMLHttpRequest|sendBeacon|WebSocket\" src/ index.html` 无输出；`window.onerror` 也没有",
             "白屏只能等玩家来评论；连「有多少人打开过」都不知道"],
        ],
        [2.9, 4.2, 5.8, 3.1],
        size=8.5,
        caption="表 1-1　三件事都不是同一种东西：1 管「代码对不对」，2 管「送得到」，3 管「出事了知不知道」",
    )
    k.note(
        doc,
        "17 号与另外两件不一样：它要动的是你**已经写进宣传与合规里的「零请求」**（6.2 第六节）。"
        "所以它不是「补个功能」，是一次取舍——见第四节。",
    )

    # ---------------- 二 ----------------
    k.h1(doc, "二", "CI 到底是什么")
    k.h2(doc, "2.1 一段话 + 一个比喻")
    k.para(
        doc,
        "CI 是 Continuous Integration，持续集成。说人话：**你把代码推到 GitHub，GitHub 借一台干净的空机器，"
        "按你写的清单把命令重跑一遍；任何一条不过，就在提交记录上打红叉，并给你发邮件。**它不部署、不发布、不碰平台，只做检查。",
    )
    k.para(
        doc,
        "生活比喻：**小区门卫**。你每次进出门（push），门卫按固定清单核对：证件（类型检查）、行李（测试）、有没有带违禁品（构建）。"
        "门卫不替你搬家（部署），也不管你屋里怎么摆（业务代码）；但它能在你出门前说一句「你包里有个坏东西」。",
    )
    k.para(
        doc,
        "一个容易混的点：CI 里跑的**不是新东西**，就是你现在手动敲的那几条 npm 命令。CI 的价值不在「能跑」，而在「**不用你记得跑**」。"
        "所以「上不上 CI」其实是问：你愿不愿意接受一次性的配置成本，换掉「靠记性」这件事。",
    )

    k.h2(doc, "2.2 若上，具体跑哪几条（命令名从 package.json 抄）")
    k.table(
        doc,
        ["序", "命令（真名）", "定义在哪", "拦得住什么"],
        [
            ["1", "`pnpm install --frozen-lockfile`", "包管理器。仓库只有 `pnpm-lock.yaml`，没有 package-lock.json",
             "锁文件与 package.json 不一致；依赖装成别的版本"],
            ["2", "`npm run typecheck` → `tsc --noEmit`", "package.json `scripts.typecheck`",
             "类型错误（就是 4.3 里说的「临时删字段留下的 any」）"],
            ["3", "`npm test` → `vitest run`", "`scripts.test`；61 个用例在 `tests/core.test.ts`",
             "core 逻辑回归（数值、事件、存档）"],
            ["4", "`npm run build` → `tsc --noEmit && vite build`", "`scripts.build`；产物 `dist/index.html`，今天 88.5 KB",
             "构建失败；产物没出来或体积异常"],
            ["5", "`npm run smoke` → `node scripts/smoke.mjs`", "`scripts.smoke`；脚本里写死了本机 Edge 路径",
             "主流程点不动（**不建议进 CI**，见下）"],
        ],
        [0.8, 5.4, 5.4, 4.4],
        size=8.5,
        caption="表 2-1　第 2、4 条有重复（build 里也跑了 tsc），留着是为了报错更早、提示更清楚",
    )
    k.para(
        doc,
        "为什么第 5 条不建议进 CI：`scripts/smoke.mjs` 与 `scripts/check-pushed.mjs` 都把浏览器路径写死成 "
        "`C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`，GitHub 的 Ubuntu 机器上没有这个路径。"
        "要跑就得改成装 Chromium（多 1–2 分钟，且可能忽快忽慢）。这是代价说明，不是结论。",
    )

    k.h2(doc, "2.3 极简配置长什么样")
    k.para(
        doc,
        "下面这份约 20 行，放在 `.github/workflows/ci.yml` 就生效。**我没有创建这个文件**——仓库里现在仍然是 0 个 CI 配置；"
        "要不要上还没定，你点头后我再写。",
    )
    code_block(doc, YAML)
    k.para(
        doc,
        "两个细节：①仓库只有 pnpm 锁文件，所以用 `pnpm install --frozen-lockfile` 而不是 `npm ci`；"
        "②`node-version: 22` 是我随手填的 LTS，本机是 v24.14.0，两个都跑过构建，换成 24 也行——这个不影响结论。",
    )

    k.h2(doc, "2.4 上的代价")
    k.table(
        doc,
        ["代价", "具体是什么", "量级"],
        [
            ["一次性配置", "一个 yml 文件 + 一次 push；不需要任何 secret，CI 只读代码、不碰平台", "约 30 分钟"],
            ["每次 push 等待", "typecheck + test + build 大约 1–3 分钟，跑在 GitHub 的机器上，不占你电脑", "中，可以先去干别的"],
            ["免费额度", "公开仓库的 Actions 免费；私有仓库免费额度按月计（具体以你账号的 Billing 页面为准）", "**待确认**：仓库是 public 还是 private"],
            ["维护", "action 的大版本升级时跟着改一次", "半年一次"],
            ["它拦不住什么", "拦不住「逻辑对但不好玩」；拦不住平台 webview 兼容（R1）；smoke 不进 CI 就拦不住「点不动」", "重要，别期待错"],
            ["沙箱限制", "我这边的沙箱 `git push` 必失败（不能起 ssh 进程，3.3 第七节已写），配置我写、push 只能你在终端做", "已确认"],
        ],
        [3.0, 9.4, 3.6],
        size=8.5,
        caption="表 2-2　四项里前两项是「一次性」，后两项是「长期的」——这也是 CI 和「多跑一次测试」的区别",
    )

    # ---------------- 三 ----------------
    k.h1(doc, "三", "自动部署：能自动的只有一半")
    k.h2(doc, "3.1 现在的投稿路径（已核实的部分）")
    k.para(
        doc,
        "我去查了一次官方说明：虎扑官方账号「虎扑的步行街」2026-05-27 的帖子"
        "（bbs.hupu.com/639560769.html）。它写的收稿方式是两种——① 在话题 #虎扑vibe coding作品征集 下发帖，"
        "帖里介绍作品并**附一个可访问链接**；② 没有线上链接的，把 `.html` 文件发到 zhouzixuan@hupu.com。"
        "并明确「官方仅能帮助部署单个 .html 文件」「涉及后端、数据库、接口、登录鉴权的暂无法部署」。",
    )
    k.table(
        doc,
        ["步", "现在怎么做", "能不能自动"],
        [
            ["1", "构建：本地 `npm run build`，产物 `dist/index.html`（88521 字节 ≈ 88.5 KB）", "能"],
            ["2", "校验：3.3 的 6 步检查单，逐条手敲", "能（前 5 步；第 6 步要线上地址）"],
            ["3", "选文件：人看 `dist/` 与 `dist-slice/`，决定传哪个", "能（脚本打印一行「该传 dist/index.html」）"],
            ["4", "送平台：按官方帖，要么发帖附链接，要么邮件发 .html", "**不能**。没有公开 API；发帖、发邮件都是人工"],
            ["5", "平台部署：官方「仅能帮助部署单个 .html 文件」，审核通过后 2 个工作日内上线", "**不能**，是平台侧动作"],
            ["6", "上线自检：人打开链接看一眼；`check-pushed.mjs` 可代跑，但要先有 URL", "半自动"],
        ],
        [0.8, 10.6, 4.6],
        size=8.5,
        caption="表 3-1　6 步里只有第 1–3 步在你手里，第 4–5 步是平台的门，第 6 步要人判断",
    )
    k.note(
        doc,
        "两个限定：①这是 **2026-05 那期活动**的写法，不是常设文档，你现在投的那一期是否同一套要你确认；"
        "②整篇帖子没有提任何 API、上传接口或定时抓取，所以本文按「**没有 API**」处理，等你问到新信息再改。",
    )

    k.h2(doc, "3.2 能自动到哪一步（四档，不是推荐）")
    k.table(
        doc,
        ["档", "做什么", "你还要动手的", "代价"],
        [
            ["甲 本地一条脚本",
             "新加 `scripts/release.mjs`：构建 → 跑切片检查 → 复制一份 `.bak` → 打印版本号与「该传哪个文件」",
             "敲一条命令，然后手动上传", "半天。仍会「忘了跑」"],
            ["乙 甲 + Actions 出产物",
             "push 后自动跑同一串，把 `dist/index.html` 作为 artifact 传上去",
             "下载 artifact，再上传", "+1 天。artifact 有保留期（默认 90 天）"],
            ["丙 乙 + Pages 预发",
             "自动发布一个可访问链接，投稿时直接贴链接",
             "贴链接", "+1–2 天。要确认仓库 public/private 与 Pages 权限；这是预发地址，不是投稿入口"],
            ["丁 等平台 API",
             "不写代码", "—", "官方帖未提任何 API；没有时间表，等于不做"],
        ],
        [3.6, 6.4, 3.2, 2.8],
        size=8.5,
        caption="表 3-2　四档的差别不在「自不自动」，而在「你手上拿到的东西有多确定」",
    )
    k.para(
        doc,
        "甲/乙/丙 **都不解决第 4 步**，因为平台没接口。所以「自动部署」这件事的天花板是：**把「准备投稿的那一份」做到零疑问**，"
        "而不是「点一下就上线」。这一点如果不接受，丙 也没意义。",
    )

    k.h2(doc, "3.3 平台未知点（需要你去问）")
    k.table(
        doc,
        ["#", "问题", "为什么要问", "我核实到哪一步"],
        [
            ["1", "你这期投稿，是「话题下发帖 + 链接」还是「邮件发 .html」？还是都行？",
             "决定第 4 步是人发帖还是人发邮件；两者都不能脚本化", "只核到 2026-05 那期帖子的写法"],
            ["2", "平台后台给不给「打开数 / 留存 / 报错」？作品卡上目前只看到「支持数」",
             "决定 17 号的丙选项是否成立", "帖子里只提作品卡（名/作者/入口/支持数），没提后台"],
            ["3", "投稿后能不能改、能不能重传新版本？要不要重新审核？",
             "决定「回滚」和「热修」的真实成本", "未提及"],
            ["4", "有没有公开 API / 上传接口 / 定时抓取？",
             "决定 16 号丁档是否存在", "帖子未提，按「没有」处理"],
            ["5", "审核周期是否仍是 2 个工作日？",
             "决定上线节奏与「改完多久能被看到」", "帖子写 2 个工作日（2026-05）"],
            ["6", "对 .html 有没有体积 / 外链 / 网络请求的限制？",
             "直接决定 17 号能不能加请求", "未提及"],
        ],
        [0.8, 7.2, 4.6, 3.4],
        size=8.5,
        caption="表 3-3　这 6 个答案里，第 1、2、6 条会直接改掉 16/17 号的选项表",
    )

    # ---------------- 四 ----------------
    k.h1(doc, "四", "监控与埋点：先看清冲突")
    k.h2(doc, "4.1 冲突在哪")
    k.para(
        doc,
        "你的游戏现在是**真·零请求**：`src/` 与 `index.html` 里 fetch / XMLHttpRequest / sendBeacon / WebSocket **一处都没有**。"
        "这也是 6.2 里「不收集数据、不需要隐私弹窗」的依据。任何「自动上报错误」的方案，都会让这句话不再成立——"
        "这不是技术问题，是**你要不要保住这个宣传点**的问题。",
    )
    k.para(
        doc,
        "另一个事实：现在**没有全局错误捕获**。`window.onerror`、`unhandledrejection` 都没写，"
        "所以今天白屏了，除了用户手机上的控制台，什么痕迹都不留。",
    )
    k.note(
        doc,
        "存档是另一回事：`src/core/save.ts` 的 `loadSaved` / `persist` / `clearSaved` 都包了 try/catch，"
        "写不进去就静默返回 null 或忽略（隐私模式不崩）。**但「写不进存档」这件事本身没有任何记录**——"
        "玩家只会看到「进度没了」，你什么也收不到。",
    )

    k.h2(doc, "4.2 四条路与代价")
    k.table(
        doc,
        ["路", "具体做法", "拿到什么", "破不破零请求", "合规", "包体 / 工作量"],
        [
            ["甲 第三方错误上报（Sentry 一类）",
             "引入 SDK，自动收堆栈",
             "堆栈、设备、聚合看板；连「没反馈的人」的错也能收到",
             "**破**：上线即请求第三方",
             "要隐私说明与告知；可能涉及数据出境；要给用户一个「关掉」的说法",
             "+20–40 KB 起（未压缩口径，以你选的 SDK 为准）；接入半天–1 天；要注册账号"],
            ["乙 localStorage 错误日志 + 一键复制",
             "全局 onerror 写本地环形日志（上限 20 条），结局页放一个「复制诊断信息」",
             "愿意点复制的玩家的堆栈；拿不到沉默用户",
             "不破",
             "数据只在用户机器上；简介仍建议写一句「不收集信息」",
             "+1–2 KB；半天；要加 UI（而「一键复制」仓库里还没有，见 4.3）"],
            ["丙 只用平台自带数据",
             "不写代码，上线后看后台",
             "平台给什么拿什么（目前只见「支持数」）",
             "不破",
             "无",
             "0 KB / 0 天；但**数据口径不由你定**，没有就没有"],
            ["丁 不做",
             "看评论与私信",
             "只有愿意说话的人",
             "不破",
             "无",
             "0"],
        ],
        [3.0, 3.5, 3.4, 1.5, 2.4, 2.2],
        size=8,
        caption="表 4-1　甲 是唯一能拿到「沉默用户」数据的，也是唯一要改合规文案的",
    )
    k.para(
        doc,
        "关于包体：现在 `dist/index.html` 是 88.5 KB。甲 的 SDK 通常 +20–40 KB（不同 SDK 差很多）；乙 是手写，+1–2 KB。"
        "这个 88.5 KB 不是预算上限——上限在 3.4，本文不替你定。",
    )
    k.note(
        doc,
        "乙 的一个坑要说清：错误日志要用**独立 key**（例如 `lpl-career-proto:errlog`）并设条数上限。"
        "localStorage 有容量上限，日志写满后 `persist` 会静默失败（`src/core/save.ts:40-46`），"
        "玩家表现就是「丢档」——那比没有日志更糟。",
    )

    k.h2(doc, "4.3 如果选乙，要动哪两处（先看，不动手）")
    k.para(
        doc,
        "① `src/ui/main.ts` 加一个全局 `window.onerror` + `unhandledrejection`，把消息、堆栈、时间写进 localStorage；"
        "② 结局页或设置页加一个「复制诊断信息」按钮。**注意第二件不是白捡的**：仓库里现在 grep 不到 `clipboard`，"
        "5.5 的「战绩卡复制」也还是未完成项——乙 等于要顺手把「复制」这个交互做出来。",
    )

    k.h2(doc, "4.4 丙 的前提")
    k.para(
        doc,
        "丙 成立的前提是平台后台真的给数。官方帖只提到作品卡上的「支持数」，没提打开数、留存、报错。"
        "所以丙 现在**不能算已成立**——它挂在 3.3 的第 2 问上。这也是为什么我没有把「丙」写成「免费拿大盘数据」："
        "免费是事实，「有数据」还没被证实。",
    )

    # ---------------- 五 ----------------
    k.h1(doc, "五", "需要你拍板")
    k.para(
        doc,
        "每条只列选项与代价，不写推荐。三张 ticket 里原有的「我的推荐」只是当时的倾向，不是决定——你点哪个，我按哪个做。",
    )
    k.table(
        doc,
        ["#", "要定的", "选项", "代价", "不定会怎样"],
        [
            ["1", "CI 上不上", "甲 不上，继续 3.3 的 6 步手动检查单 / 乙 上极简 Actions（typecheck + test + build）",
             "甲：0 成本，靠记性；乙：一个 yml + 每次 push 等 1–3 分钟 + push 只能你做",
             "继续「漏跑一步发坏包」（R9 概率是「确定」）"],
            ["2", "自动部署到哪一档", "甲 本地一条脚本 / 乙 甲 + Actions 产物 / 丙 乙 + Pages 预发 / 丁 等平台 API",
             "见 3.2 表（半天 → 1–2 天 → 无时间表）", "每次投稿都要人工确认文件对不对"],
            ["3", "监控走哪条", "甲 第三方上报 / 乙 localStorage + 一键复制 / 丙 只用平台数据 / 丁 不做（可组合，如乙 + 丙）",
             "见 4.2 表（合规与包体差别最大）", "白屏只能等评论；打开数不知道"],
            ["4", "「零请求」这个点保不保", "保：只能走 乙/丙/丁；不保：可以走 甲",
             "保：拿不到沉默用户的数据；不保：6.2 第六节要改，要写隐私说明",
             "17 号定不了稿，因为方案取决于这一条"],
            ["5", "平台那 6 个问题谁去问", "你去问 / 我先按「没有 API」做，问到再改",
             "你问一次 ≈ 我在文档里猜十次", "16 号的「能自动到哪」永远悬空"],
        ],
        [0.8, 3.0, 6.4, 3.4, 2.4],
        size=8.5,
        caption="表 5-1　第 4 条是前置：它不定，第 3 条的四选一没有意义",
    )
    k.note(
        doc,
        "另外三件只有你能回答（不是选型）：① 这期官方要求的收稿方式；② 平台后台你能看到哪些数；"
        "③ GitHub 仓库是 public 还是 private（决定 Actions 免费额度，以及 Pages 能不能开）。",
    )

    # ---------------- 六 ----------------
    k.h1(doc, "六", "这次没做什么")
    k.para(
        doc,
        "没有创建 `.github/`（上面的 YAML 只贴在文档里）；没有改 `src/`；没有 commit / push（沙箱里 push 必失败）。"
        "三张 ticket 的 `Status` 仍是 open，`## Answer` 只写了「材料已备」。",
    )

    # ---------------- 附录 ----------------
    k.h1(doc, "附", "核对命令与结果（可复跑）")
    k.table(
        doc,
        ["核对项", "命令", "结果"],
        [
            ["CI 配置", "`ls .github` + `git ls-files '*.yml'`", "无 `.github` 目录；只有 pnpm-lock.yaml、pnpm-workspace.yaml = **0 个**"],
            ["网络请求", "`grep -rnE \"fetch\\(|XMLHttpRequest|sendBeacon|WebSocket\" src/ index.html`", "0 行"],
            ["全局错误捕获", "`grep -rnE \"onerror|unhandledrejection\" src/ index.html`", "0 行"],
            ["存档 try/catch", "读 `src/core/save.ts`", "3 个函数（loadSaved / persist / clearSaved）全包"],
            ["产物与大小", "`ls -l dist/index.html dist-slice/index.html`", "88521 / 89300 字节"],
            ["测试数", "`grep -c \"it(\" tests/core.test.ts`", "61"],
            ["远端", "`git remote -v`", "`git@github.com:2845894832/lol-career-sim-.git`（末尾是横线）"],
            ["本地与远端", "`git status -sb`", "`master...origin/master [ahead 23]`"],
        ],
        [3.2, 7.2, 5.6],
        size=8.5,
        caption="表 附-1　换个日期复跑，数字可能会变；结论「0 个 / 0 处」应当仍然成立",
    )

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
