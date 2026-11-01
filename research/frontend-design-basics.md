# 前端设计：能直接写进规格的那些数字

为 P3 切片（第 1–8 周，手机竖屏单文件）准备。只收**能落成数字和条件**的条目；「要好看」这类不算。

## 一、触摸目标

| 来源 | 规定 | 性质 |
| --- | --- | --- |
| [WCAG 2.2 SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | 所有目标至少 **24 × 24 CSS px**，或周围有足够间距 | 标准原文，AA 级 |
| [Apple HIG · Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons) | 触摸目标按 **44 × 44 pt** | 平台指南 |

取用：**44 做，24 是底线**。差值来自手指接触面积（约 9mm ≈ 34 CSS px）加误触余量。

## 二、间距与栅格

- [Material 3](https://m3.material.io/) 全体系按 **8dp 栅格**：尺寸与间距取 8 的倍数。
- [AdaptiveSpacing](https://pub.dev/documentation/material_layout/latest/material_layout/AdaptiveSpacing-class.html) 展示了「断点 → 间距」的表格式写法，可直接抄成规格表。

取用：最小单位 **4px**，常用档 8 / 16 / 24 / 32。好处是所有值同源，改一处不连锁。

## 三、中文排版

- [W3C · Requirements for Chinese Text Layout (clreq)](https://www.w3.org/TR/2024/DNOTE-clreq-20241219/)：标点不可出现在行首、行尾避头尾、中西文之间留空、数字用比例字体等。
- [中英文混排字体搭配](https://www.hellofont.cn/article/chinese-english-font-pairing-2026)：二手来源，给了几组可用搭配。

取用：
- 正文行高 **1.7–1.8**（中文比拉丁文需要更松的行距）
- 中西文之间留 **1/4 字宽**（clreq 有对应条款）
- 标点避头尾用 CSS `line-break: strict` 或手动断

## 四、字号阶梯

没有官方规定，属经验值。常用四档：**32 / 22 / 17 / 13**（标题 / 段落标题 / 正文 / 注释）。规则是「档位尽量少」，一多层级就没了。

## 五、动画时长

Material 常被引用为 **100–300ms**，但我没拿到官方原文，标为**二手**。切片阶段先用 **200ms** 试，靠手感定。

## 六、没查到一手的

- 「一屏放几件事」——无官方数字，只能在你的切片上试。
- 游戏场景下字号可否小于 13px——移动端游戏常见 12–14px，但没有可引用的标准。

## 对 P2 现界面的直接结论

1. 结周按钮、行动槽的点击区都小于 44px（现在靠 padding 勉强接近），**先做成 ≥44**。
2. 第一屏同时显示 13 项信息，没有主次——**只能留一个主**。
3. 数值区 6 项等宽排列，读不出「哪项重要」——需要分档，不是分列。
4. 行高与间距目前混用多个值（6/8/10/12px），**归一到 4 的倍数**。

## 备注

这份文档只覆盖「界面形制」。玩法、题材、风格取向不在这里，归 P0/P1。
