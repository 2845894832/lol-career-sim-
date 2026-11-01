# 资源

一手来源优先。每条都写了「能从中拿到什么」，避免你自己再翻一遍。

## 1. 点击目标的大小

- [WCAG 2.2 · SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) —— 规定 **24×24 CSS px** 是下限（AA 级），且可用「足够间距」替代。这是能引用的原文。
- [Apple HIG · Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons) —— iOS 的触摸目标按 **44×44 pt** 做，比 WCAG 更严；你的界面在手机上跑，按 44 更安全。

**取哪个**：硬底线 24，实际按 44 做。中间差 20px，就是「点了没反应」和「一点就中」的差别。

## 2. 间距与栅格

- [Material 3 · What's new](https://m3.material.io/blog/whats-new-at-io26) —— 官方博客里贯穿的 8dp 栅格：所有间距/尺寸取 8 的倍数。
- [AdaptiveSpacing（material_layout 包）](https://pub.dev/documentation/material_layout/latest/material_layout/AdaptiveSpacing-class.html) —— 把「断点 → 间距」写成表，可以直接照抄成你的规格。

**取哪个**：间距单位定 **4px**，主要间隔用 8/16/24/32。好处是所有数字能被 4 整除，改一个数不会连锁。

## 3. 中文这一块（最容易被忽略）

- [W3C · Requirements for Chinese Text Layout（clreq）](https://www.w3.org/TR/2024/DNOTE-clreq-20241219/) —— 中文排版的正式需求文档：标点不能出现在行首、中西文之间要留空隙、数字用比例字体等。
- [中英文混排字体怎么搭配](https://www.hellofont.cn/article/chinese-english-font-pairing-2026) —— 二手，但给了几组能直接用的中西文搭配。

**取哪个**：正文行高 **1.7–1.8**（中文比英文需要更松），中西文之间手动留 1/4 个字宽，标点不许顶行首。

## 4. 还没找到一手来源的

- **过渡动画该多长**（Material 说 100–300ms 区间，但我没拿到官方原文，暂标「二手」）。
- **一屏放几件事**（没有官方数字，属经验值，需要在你的切片上试）。

## 怎么用这些资源

读的时候只找三样东西：**数字、单位、条件**。一句「按钮应该足够大」没用；「24×24 CSS px 或足够间距」才能写进规格表。
