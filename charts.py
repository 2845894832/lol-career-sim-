# -*- coding: utf-8 -*-
"""生成《Vibe Coding 独立游戏制作人 · 全流程手册》所需配图（Pillow 手绘，无 matplotlib）。"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_B = "C:/Windows/Fonts/msyhbd.ttc"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
os.makedirs(OUT, exist_ok=True)

INK, GRAY, MUTED = "#1b1b1b", "#5b6674", "#8b95a3"
NAVY, BLUE, TEAL = "#1f3a5f", "#2f6fa8", "#2e8b7e"
WARM, GREEN, RED = "#c07a2e", "#5b8c5a", "#b04a4a"


def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def canvas(w, h):
    im = Image.new("RGB", (w, h), "white")
    return im, ImageDraw.Draw(im)


def text(d, xy, s, size=22, bold=False, fill=INK, anchor="mm", spacing=8):
    d.multiline_text(xy, s, font=f(size, bold), fill=fill, anchor=anchor,
                     align="center", spacing=spacing)


def arrow(d, p1, p2, color=BLUE, width=4, head=15):
    import math
    (x1, y1), (x2, y2) = p1, p2
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    d.line([(x1, y1), (bx, by)], fill=color, width=width)
    d.polygon([(x2, y2),
               (x2 - head * 1.7 * math.cos(a - 0.4), y2 - head * 1.7 * math.sin(a - 0.4)),
               (x2 - head * 1.7 * math.cos(a + 0.4), y2 - head * 1.7 * math.sin(a + 0.4))],
              fill=color)


def dashed(d, pts, color, width=3, dash=12, gap=9):
    import math
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        L = math.hypot(x2 - x1, y2 - y1)
        t = 0.0
        while t < L:
            e = min(t + dash, L)
            d.line([(x1 + (x2 - x1) * t / L, y1 + (y2 - y1) * t / L),
                    (x1 + (x2 - x1) * e / L, y1 + (y2 - y1) * e / L)], fill=color, width=width)
            t = e + gap


# ---------------------------------------------------------------- 图 1 流水线
def fig_pipeline():
    W, H = 1600, 900
    im, d = canvas(W, H)
    boxes = [
        ("P0", "定位与约束", "一句话说清：给谁、多大、多久", "你"),
        ("P1", "概念与核心循环", "一页纸 + 循环图 + 一条待验证假设", "你"),
        ("P2", "可玩原型", "最丑但能玩的核心 60 秒", "你"),
        ("P3", "纵向切片", "一小段达到成品品质的体验", "你"),
        ("P4", "内容量产", "把切片扩到完整内容量", "AI（你验收）"),
        ("P5", "打磨", "手感、反馈、可读性", "AI（你验收）"),
        ("P6", "测试与平衡", "观察真实玩家的行为断点", "你"),
        ("P7", "发布准备", "商店页、素材、构建、多语言", "AI（你验收）"),
        ("P8", "上线之后", "补丁 + 复盘 + 下一款", "你"),
    ]
    pos = [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2)]
    bw, bh, gx, gy, x0, y0 = 458, 196, 36, 44, 74, 70
    colors = ["#eef3f8", "#e8f0f7", "#e2eef5", "#ddebf2", "#d8e8ef",
              "#d3e5ec", "#cee2e9", "#c9dfe6", "#c4dce3"]

    def rect(cx, cy):
        x = x0 + cx * (bw + gx)
        y = y0 + cy * (bh + gy)
        return x, y, x + bw, y + bh

    for i, (code, name, prod, who) in enumerate(boxes):
        cx, cy = pos[i]
        x1, y1, x2, y2 = rect(cx, cy)
        d.rounded_rectangle([x1, y1, x2, y2], radius=14, fill=colors[i],
                            outline=NAVY, width=3)
        d.rounded_rectangle([x1, y1, x1 + 74, y1 + 40], radius=10, fill=NAVY)
        text(d, (x1 + 37, y1 + 20), code, 22, True, "white")
        text(d, (x1 + 88, y1 + 21), name, 25, True, NAVY, anchor="lm")
        text(d, (x1 + 24, y1 + 84), prod, 18, False, GRAY, anchor="lm")
        text(d, (x1 + 24, y1 + 148), "主导：" + who, 17, True, TEAL, anchor="lm")

    # 连接箭头
    for i in range(len(boxes) - 1):
        (ax, ay) = pos[i]
        (bx, by) = pos[i + 1]
        x1, y1, x2, y2 = rect(ax, ay)
        X1, Y1, X2, Y2 = rect(bx, by)
        if ay == by and bx > ax:      # 向右
            arrow(d, (x2 + 4, (y1 + y2) // 2), (X1 - 6, (Y1 + Y2) // 2))
        elif ay == by and bx < ax:    # 向左
            arrow(d, (x1 - 4, (y1 + y2) // 2), (X2 + 6, (Y1 + Y2) // 2))
        elif bx == ax and by > ay:    # 向下
            arrow(d, ((x2 + x1) // 2, y2 + 4), ((X2 + X1) // 2, Y1 - 6))

    text(d, (W // 2, 838),
         "实线箭头为推荐推进顺序；真实项目常常从 P2 回退到 P1——回退不是失败，但每次回退都要写下「哪条假设错了」。",
         18, False, MUTED)
    im.save(os.path.join(OUT, "fig1-pipeline.png"))


# ---------------------------------------------------------------- 图 2 决策权
def fig_authority():
    W, H = 1500, 880
    im, d = canvas(W, H)
    rows = [("P0 定位", 92), ("P1 概念", 86), ("P2 原型", 62), ("P3 切片", 55),
            ("P4 量产", 34), ("P5 打磨", 30), ("P6 测试", 42), ("P7 发布", 48),
            ("P8 上线后", 72)]
    left, right, top, gap, bh = 250, 1400, 96, 78, 42
    span = right - left
    for i, (name, human) in enumerate(rows):
        y = top + i * gap
        text(d, (left - 22, y + bh / 2), name, 22, True, INK, anchor="rm")
        hw = span * human / 100
        d.rectangle([left, y, left + hw, y + bh], fill=NAVY)
        d.rectangle([left + hw, y, right, y + bh], fill="#9dc3dd")
        if human >= 20:
            text(d, (left + hw / 2, y + bh / 2), f"你 {human}%", 19, True, "white")
        if 100 - human >= 20:
            text(d, (left + hw + (span - hw) / 2, y + bh / 2), f"AI {100 - human}%", 19, True, NAVY)
    d.line([(left, 78), (right, 78)], fill="#d5dce4", width=2)
    text(d, ((left + right) / 2, 60), "「你」= 决策与验收　　「AI」= 实现与穷举", 19, False, GRAY)
    y = top + len(rows) * gap + 6
    text(d, (W // 2, y), "示意：越往后期，执行越可以外包，但「什么算够了」始终在你手上。", 19, False, MUTED)
    text(d, (W // 2, y + 30), "比例是经验判断，不是测量值。", 17, False, MUTED)
    im.save(os.path.join(OUT, "fig2-authority.png"))


# ---------------------------------------------------------------- 图 3 能力雷达
def fig_radar():
    import math
    W, H = 1400, 1260
    im, d = canvas(W, H)
    axes = ["玩法设计", "规格表达", "验收判断", "引擎操作", "内容量产",
            "美术/音频", "发行运营", "社区反馈"]
    near = [62, 78, 72, 46, 40, 34, 38, 26]
    far = [86, 86, 86, 80, 76, 58, 70, 62]
    cx, cy, R = W // 2, 610, 348
    n = len(axes)
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    def pt(v, a):
        return (cx + R * v / 100 * math.cos(a), cy + R * v / 100 * math.sin(a))

    for ring in (25, 50, 75, 100):
        d.ellipse([cx - R * ring / 100, cy - R * ring / 100,
                   cx + R * ring / 100, cy + R * ring / 100],
                  outline="#dfe6ee" if ring < 100 else "#c6d0da", width=2)
    for a in ang:
        d.line([(cx, cy), pt(100, a)], fill="#c6d0da", width=2)
    for i, a in enumerate(ang):
        x, y = pt(118, a)
        text(d, (x, y), axes[i], 24, True, INK)

    d.polygon([pt(v, a) for v, a in zip(far, ang)], fill="#f3e3d2")
    dashed(d, [pt(v, a) for v, a in zip(far, ang)] + [pt(far[0], ang[0])], WARM, 3)
    d.polygon([pt(v, a) for v, a in zip(near, ang)], fill="#cfe0ee")
    d.line([pt(v, a) for v, a in zip(near, ang)] + [pt(near[0], ang[0])], fill=BLUE, width=4)
    for v, a in zip(near, ang):
        x, y = pt(v, a)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=BLUE)

    lx, ly = 90, 1120
    d.rectangle([lx, ly - 16, lx + 42, ly + 16], fill="#cfe0ee", outline=BLUE, width=2)
    text(d, (lx + 56, ly), "第一款游戏：做到「能判断」（我的建议）", 20, False, INK, anchor="lm")
    d.rectangle([lx + 470, ly - 16, lx + 512, ly + 16], fill="#f3e3d2", outline=WARM, width=2)
    text(d, (lx + 526, ly), "长期目标：能持续做下去（我的建议）", 20, False, INK, anchor="lm")
    text(d, (W // 2, 1192), "曲线高低是相对刻度，不是测评结果；它的用途是提醒你：判断类比操作类更该先补。",
         18, False, MUTED)
    im.save(os.path.join(OUT, "fig3-skill-radar.png"))


# ---------------------------------------------------------------- 图 4 学习优先级
def fig_priority():
    W, H = 1500, 1060
    im, d = canvas(W, H)
    L, R, T, B = 190, 1380, 170, 880
    for v in range(11):
        x = L + (R - L) * v / 10
        d.line([(x, T), (x, B)], fill="#eef1f5", width=1)
        y = B - (B - T) * v / 10
        d.line([(L, y), (R, y)], fill="#eef1f5", width=1)
    d.line([(L, B), (R, B)], fill="#b8c2cd", width=2)
    d.line([(L, T), (L, B)], fill="#b8c2cd", width=2)
    text(d, ((L + R) / 2, B + 40), "对「第一款游戏能不能做完」的影响 →", 21, True, GRAY)
    text(d, (L - 70, (T + B) / 2), "学习成本 ↑", 21, True, GRAY, anchor="mm")
    # 用旋转文本更清晰：简化为左侧竖排提示
    text(d, (W // 2, 58), "右下（影响大、成本低）= 先学　　　左上（影响小、成本高）= 先不学", 19, False, GRAY)

    kinds = {"判断": "#b04a4a", "操作": "#2f6fa8", "深度": "#5b8c5a"}
    items = [
        ("规格表达", 9.2, 6.0, 18, "判断"), ("验收判断", 9.0, 6.8, 17, "判断"),
        ("玩法设计", 9.5, 7.6, 17, "判断"), ("诚实自评", 5.0, 3.0, 10, "判断"),
        ("引擎基础", 8.5, 5.0, 16, "操作"), ("版本控制", 6.5, 1.8, 12, "操作"),
        ("构建与发布", 6.0, 3.4, 12, "操作"), ("内容量产", 7.0, 4.0, 14, "操作"),
        ("美术/音频", 5.0, 7.0, 13, "操作"), ("发行与商店页", 6.5, 6.0, 13, "操作"),
        ("性能优化", 3.0, 7.6, 8, "深度"), ("架构设计", 3.5, 8.6, 8, "深度"),
        ("Shader", 2.0, 9.0, 6, "深度"), ("联机", 1.8, 9.6, 6, "深度"),
        ("3D", 3.0, 9.3, 7, "深度"), ("C# 深学", 2.5, 8.0, 7, "深度"),
    ]
    for name, x, y, r, k in items:
        px = L + (R - L) * x / 10
        py = B - (B - T) * y / 10
        c = kinds[k]
        d.ellipse([px - r, py - r, px + r, py + r], fill=c + "33", outline=c, width=3)
        off = -1 if x > 8.2 else 1
        text(d, (px + off * (r + 10) + (0 if off > 0 else 0), py - 2), name, 18,
             True, INK, anchor="lm" if off > 0 else "rm")

    lx, ly = L + 20, 118
    for i, (k, c) in enumerate(kinds.items()):
        x = lx + i * 190
        d.ellipse([x, ly - 11, x + 22, ly + 11], fill=c + "33", outline=c, width=3)
        text(d, (x + 32, ly), k + "类", 19, True, INK, anchor="lm")
    text(d, (W // 2, 985), "气泡大小 = 这项能力在第一款游戏里被反复用到的次数；坐标为定性判断，不是测量值。",
         18, False, MUTED)
    im.save(os.path.join(OUT, "fig4-priority.png"))


# ---------------------------------------------------------------- 图 5 时间-能力
def fig_curve():
    W, H = 1500, 900
    im, d = canvas(W, H)
    L, R, T, B = 150, 1360, 100, 760
    for v in range(0, 101, 20):
        y = B - (B - T) * v / 100
        d.line([(L, y), (R, y)], fill="#eef1f5", width=1)
        text(d, (L - 18, y), str(v), 18, False, MUTED, anchor="rm")
    for w in range(0, 53, 4):
        x = L + (R - L) * w / 52
        text(d, (x, B + 26), str(w), 18, False, MUTED)
    text(d, (R + 34, B + 26), "周", 19, True, GRAY, anchor="lm")
    text(d, (L - 70, (T + B) / 2), "能力", 19, True, GRAY)

    def curve(pts, color, width=5):
        d.line([(L + (R - L) * x / 52, B - (B - T) * y / 100) for x, y in pts],
               fill=color, width=width, joint="curve")

    slow = [(0, 0), (12, 18), (20, 26), (34, 38), (52, 52)]
    fast = [(0, 4), (6, 30), (12, 48), (20, 62), (30, 70), (40, 80), (52, 88)]
    curve(slow, "#b04a4a")
    curve(fast, BLUE)

    x12 = L + (R - L) * 12 / 52
    dashed(d, [(x12, T), (x12, B)], "#8b95a3", 2)
    text(d, (x12, T - 22), "同一时点", 18, True, MUTED)
    text(d, (x12 + 16, T + 20), "同样一段时间：一条线已经进到第三阶段，", 18, False, MUTED, anchor="lm")
    text(d, (x12 + 16, T + 46), "另一条才刚学完语法。", 18, False, MUTED, anchor="lm")

    text(d, (R - 120, B - (B - T) * 88 / 100 - 30), "边做边学", 21, True, BLUE, anchor="rm")
    text(d, (R - 120, B - (B - T) * 52 / 100 - 30), "先系统学编程", 21, True, RED, anchor="rm")
    text(d, (W // 2, 838), "纵轴为相对刻度，用来比较曲线的形状，不是能力评分。", 18, False, MUTED)
    im.save(os.path.join(OUT, "fig5-curve.png"))


# ---------------------------------------------------------------- 图 6 死法
def fig_risks():
    W, H = 1500, 900
    im, d = canvas(W, H)
    rows = [
        ("断档两周以上，忘了做到哪", 10),
        ("首款规模超过自己能收尾的量", 9.4),
        ("让 AI 替你定玩法与数值", 9.0),
        ("没有「完工」的定义，无限打磨", 8.4),
        ("先花三个月系统学编程", 8.0),
        ("核心循环没验证就量产内容", 7.8),
        ("上线前三天才做商店页", 7.0),
        ("只找朋友测，且只问好不好玩", 6.2),
        ("一边加内容一边改核心机制", 6.0),
    ]
    L, R, T = 520, 1330, 90
    gap, bh = 78, 40
    for i, (name, v) in enumerate(rows):
        y = T + i * gap
        text(d, (L - 20, y + bh / 2), name, 21, True, INK, anchor="rm")
        w = (R - L) * v / 10
        shade = "#1f3a5f" if i < 3 else ("#c07a2e" if i < 6 else "#9aa6b2")
        d.rounded_rectangle([L, y, L + w, y + bh], radius=6, fill=shade)
        text(d, (L + w + 14, y + bh / 2), f"{v:.1f}", 19, True, GRAY, anchor="lm")
    text(d, (W // 2, 830), "分值 = 发生概率 × 后果严重度，5 小时/周、首款作品情境下的定性排序。",
         18, False, MUTED)
    text(d, (W // 2, 858), "前三条几乎能解释大多数弃坑。", 18, True, NAVY)
    im.save(os.path.join(OUT, "fig6-risks.png"))


if __name__ == "__main__":
    fig_pipeline()
    fig_authority()
    fig_radar()
    fig_priority()
    fig_curve()
    fig_risks()
    for n in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, n)
        print(n, os.path.getsize(p) // 1024, "KB")
