# Issue tracker：本地 Markdown

本仓库的 issue 与 spec 以 markdown 文件存在 `.scratch/` 下。

## 约定

- 一个功能一个目录：`.scratch/<feature-slug>/`
- spec 是 `.scratch/<feature-slug>/spec.md`
- 实现用 issue 一个文件一张：`.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 编号，**不要**把所有 ticket 塞进一个文件
- 分诊状态写在每个 issue 文件顶部的 `Status:` 行（角色字符串见 `triage-labels.md`）
- 评论与对话历史追加到文件末尾的 `## Comments` 标题下

## 技能说「发布到 issue tracker」时

在 `.scratch/<feature-slug>/` 下新建文件（目录不存在就建）。

## 技能说「取相关 ticket」时

读取指定的文件路径；用户一般会直接给出路径或编号。

## Wayfinding 操作（`/wayfinder` 用）

**map** 是一个文件，每个子 ticket 一个文件。

- **Map**：`.scratch/<effort>/map.md`（Notes / Decisions-so-far / Fog 正文）
- **子 ticket**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 编号，正文写问题；`Type:` 行记类型（`research`/`prototype`/`grilling`/`task`），`Status:` 行记 `claimed`/`resolved`
- **阻塞**：顶部 `Blocked by: NN, NN`；所列文件全是 `resolved` 才算解开
- **前沿**：扫 `.scratch/<effort>/issues/`，取未完成、未解锁、未认领的，编号小的优先
- **认领**：动手前先写 `Status: claimed`
- **解决**：在 `## Answer` 下写答案，置 `Status: resolved`，再把摘要与链接追加到 `map.md` 的 Decisions-so-far
