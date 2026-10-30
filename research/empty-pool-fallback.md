# 事件池筛空后怎么办：一手证据

覆盖：A Dark Room 源码、ink 官方文档、Yarn Spinner 官方文档、Harlowe 官方手册、Failbetter/StoryNexus 官方手册与博客、Emily Short 原文。
不覆盖：Unity/Godot 通用实现、商业手游个案、SugarCube 等其他 Twine 格式、中文社区。

## 结论（可直接用）

1. **顺延重抽**（ADR）：定时器重排，池空就等下一轮再试 —— 代价：出现空窗；若条件永不恢复则无限静默，且不会报错。
2. **常驻/兜底池**（StoryNexus Always deck、Yarn `when: always`、ink fallback choice）：把"永远可抽"的条目排除在随机池之外 —— 代价：内容重复，需长期维护一份兜底内容。
3. **填充事件**（StoryNexus 官方建议：一打以上无前置的 Sometimes 卡）—— 代价：内容量大、易水；官方自己说 Sometimes deck "very demanding of content"。
4. **空即跳过/隐藏/报错**（StoryNexus：牌堆空了从界面消失；Harlowe：显示兜底文字或什么都不显示；ink：无 fallback 直接 runtime error）—— 代价：玩家当下无事可做，或直接崩。
5. **降级匹配**（Yarn：自定义 saliency 策略可把条件不满足的 storylet 也纳入）—— 代价：破坏前置条件语义，需另写排序规则。

## 1. 顺延重抽 —— A Dark Room 源码

`triggerEvent` 收集 `isAvailable()` 为真的条目；为空时只是重排定时器：

```js
if(possibleEvents.length === 0) { Events.scheduleNextEvent(0.5); return; }
```

`_EVENT_TIME_RANGE: [3, 6]`（分钟），`scheduleNextEvent(scale)` 把随机值乘 `scale`，故空池时 1.5–2.5 分钟后重试，正常时 3–6 分钟。
来源：开源代码 https://github.com/doublespeakgames/adarkroom/blob/master/script/events.js#L1316-L1336 、#L1413-L1418
补充：空池分支无日志无告警；`scheduleNextEvent` 本身会 `Engine.log('next event scheduled in ...')`。

## 2. ink（inkle 官方文档）

- 无 fallback 时：`Runtime error ... ran out of content. Do you need a '-> DONE' or '-> END'?`
- 官方解法：`Fallback choices are never displayed to the player, but are 'chosen' by the game if no other options exist.`
- `{stopping:}`：序列，抽完"continues to show the final element"（停在最后一条）。
- `{shuffle:}` 是 shuffled cycle：抽完重洗再来，**永远抽不干**；`{shuffle once:}` 抽完 do nothing；`{shuffle stopping:}` 洗前 n-1 条，抽完 stick on the last entry。
来源：官方文档（作者=inkle）https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md#L490-L522 、#L626-L630 、#L1530-L1550
要点：ink 没有"事件池"抽象，"抽干"实际表现为"条件选项全不满足 → out of content 错误"，兜底必须作者显式写 fallback choice，工具不自动补。

## 3. Emily Short（作者原文）

- 《Storylets Play Together》(2019-12-03) 把 always available 列为 storylet 系统提供的内容之一："contextually relevant options ... plus any 'always available' elements." https://emshort.blog/2019/12/03/storylets-play-together/
- 《Mailbag: Development Process for Storylet-based IF》(2020-02-18) 把 pacing 目标写成 "make sure the player always has something to do"。 https://emshort.blog/2020/02/18/mailbag-development-process-for-storylet-based-interactive-fiction/
- **未找到**她列"always available 元素清单"、论证"为什么必须有"、或讨论"池子空了会怎样"的段落；《Storylets: You Want Them》与《Pacing Storylet Structures》全文均无此内容。

## 4. Yarn Spinner（官方文档）

- 节点组（同名 node + `when:`）：文档要求其中一个写 `when: always` —— "this is required with node groups to say 'this one is always available'"。 https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/node-groups
- 内建策略 "first filter out storylets with failing conditions, though custom strategies can include failing conditions if desired."（降级匹配的官方口子） https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/storylets-and-saliency-a-primer
- 未核实：无任何节点可跑时的运行时错误文案（文档未写，源码未查）。

## 5. Twine / Harlowe（官方手册）

- Harlowe 3.2+ 有 `(storylet:)` / `(open-storylets:)` / `(link-storylet:)`。无可用条目时："If there is no storylet available for the link ... the optional final string will be displayed. If it isn't given, nothing will be displayed."
- 来源：Harlowe 官方手册 https://twine2.neocities.org/#macro_link-storylet
- 这是 Harlowe 宏，不是 Twine 引擎本身；其他格式未覆盖。

## 6. articy:draft

**未找到**"无可用内容"机制。官方 help 的 Conditions 只在 input-pin 上放行/拦截（Flow → Conditions & Instructions），文档里没有 deck/pool 概念，也没有空池兜底说明。 https://articy.com/help/legacy/Flow_Conditions_Instructions.html

## 7. Fallen London / Failbetter（官方手册 + 官方博客）

StoryNexus Reference Guide（Failbetter Games，v1.04）：
- Always deck vs Sometimes deck："Cards in an Always deck are always available if the player fulfils the requirements."
- 空池的引擎行为："If there are no playable cards in a Sometimes or Always deck, the deck disappears from the game interface until cards become available."（工具强制）
- 作者规则（因玩家不能弃牌）："you should put one branch in a card that you can reasonably expect they can always access."
- 填充池建议："a deck of Sometimes cards (a dozen or more) that don't have any requirements at all."
- 代价："Because you need a lot of cards to give a Sometimes deck a sense of real variety, it's very demanding of content."
https://docs.google.com/document/d/1K1wnNJoBhxr17fe3kHQTnpvWLdyxeKWZBKivDQHsdJg/mobilebasic （Failbetter 撰写的手册副本）

Failbetter 官方博客《Narrative Snippets: StoryNexus Tricks》(2012-09-09)：
- "You need at least one [branch] (and you need one that's always playable on any Sometimes storylet)."
- Sometimes deck 越大，单卡出现机会越低；Sometimes 卡适合资源/重复内容，不适合主线目标。
https://www.failbettergames.com/news/narrative-snippets-storynexus-tricks

## 未核实 / 未找到

- Emily Short 关于"池空"与 always available 必要性的专门论述：未找到。
- Yarn Spinner 无匹配节点时的运行时报错：未核实。
- articy:draft 空池处理：未找到（仅确认文档无该概念）。
- SugarCube 及其他 Twine 格式：未覆盖。
- StoryNexus 手册在 failbettergames.com 的原始地址：未核实（用的是 Google Docs 副本，正文署 FAILBETTER GAMES v1.04）。
- ink fallback choice 的运行时选择顺序：仅据文档，未读引擎源码。
