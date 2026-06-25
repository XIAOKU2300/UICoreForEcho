# -*- coding: utf-8 -*-
"""共鸣链区块: 6 节点竖向排列,已解锁节点有品质光晕。"""


def render(data, th):
    W = th.LEFT_TRACK[1]       # 380
    H = 452                    # 20 + 6*72
    layer, draw = th.new_layer(W, H)

    cx = 28                    # 圆心 x
    start_y = 20
    gap = 72
    r = 24

    locked_fill = (40, 46, 64, 160)

    # 先画串联竖线(连接相邻已解锁节点)
    for i in range(5):
        y_a = start_y + i * gap
        y_b = start_y + (i + 1) * gap
        ua = data.unlocked[i] if i < len(data.unlocked) else False
        ub = data.unlocked[i + 1] if i + 1 < len(data.unlocked) else False
        line_col = th.ACCENT_CYAN if (ua and ub) else th.DIVIDER
        draw.line([(cx, y_a + r), (cx, y_b - r)], fill=line_col, width=2)

    for i in range(6):
        cy = start_y + i * gap
        unlocked = data.unlocked[i] if i < len(data.unlocked) else False

        if unlocked:
            # 光晕效果
            th.glow_circle(draw, cx, cy, r, th.ACCENT_CYAN)
            # 已解锁: 明亮青环 + 内填色
            draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                         fill=(80, 220, 255, 50), outline=th.ACCENT_CYAN, width=2)
            text_color = th.TEXT_MAIN
        else:
            # 未解锁: 暗灰空心圆
            draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                         fill=locked_fill, outline=th.DIVIDER, width=1)
            text_color = th.TEXT_SUB

        th.text(draw, (cx, cy), str(i + 1), th.TextLevel.ACCENT,
                anchor="mm", color=text_color)

    return layer, H
