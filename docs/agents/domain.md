# 领域文档

工程类技能在探索代码库前，如何消费本仓库的领域文档。

## 探索之前先读

- 仓库根目录的 **`GLOSSARY.md`**，或
- 根目录的 **`GLOSSARY-MAP.md`**（如果存在）：它指向每个上下文各自的 `GLOSSARY.md`，读与当前话题相关的那些
- **`docs/adr/`**：读涉及你要动的那块的 ADR。多上下文仓库里还要看 `src/<context>/docs/adr/`

这些文件不存在时**安静地继续**：不要提示缺失，也不要提议先建。`/domain-modeling` 技能（由 `/grill-with-docs` 和 `/improve-codebase-architecture` 触达）会在术语或决定真正定下来时按需创建。

## 文件结构

单上下文仓库（绝大多数）：

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-xxx.md
│   └── 0002-yyy.md
└── src/
```

多上下文仓库（根目录有 `GLOSSARY-MAP.md`）：每个上下文在自己的目录下各有一份 `GLOSSARY.md` 与 `docs/adr/`，根 `docs/adr/` 放跨上下文决定。

**本仓库：单上下文。**

## 用词表里的词

输出里出现领域概念时（issue 标题、重构提案、假设、测试名），用 `GLOSSARY.md` 定义的词，不要飘到词表明确规避的同义词。

概念不在词表里，是一个信号：要么你在造项目不用的词（重想），要么真缺一条（记下来给 `/domain-modeling`）。

## 指出 ADR 冲突

输出与已有 ADR 相矛盾时，明说，不要静默覆盖：

> _与 ADR-0007（事件溯源订单）冲突，但值得重开，因为……_
