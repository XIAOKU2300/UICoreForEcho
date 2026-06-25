# -*- coding: utf-8 -*-
"""中轨声骸汇总区块 (洛瑟菈需要)."""
from PIL import ImageDraw

def render(data, th):
    if data is None:
        return None

    W = th.MID_TRACK[1]

    # 高度计算：分两栏排版（左边基础属性，右边伤害词条）可以省空间
    # 取最长的那一列
    max_rows = max(len(data.base_props), len(data.dmg_props))
    H = 80 + 40 + (max_rows * 28) + 20

    layer, draw = th.new_layer(W, H)
    th.holo_panel(draw, (0, 0, W, H), highlight=True, accent_color=th.ACCENT_VIOLET)

    # 标题
    th.title(draw, 20, 30, "声骸加成汇总")

    # 评级和评分在右上角
    grade_str = (data.grade or "--").upper()
    score_str = f"{data.score:.2f}分" if data.score else "--"

    if grade_str:
        th.text(draw, (W - 20, 20), grade_str, th.TextLevel.TITLE, anchor="rt", color=th.grade_color(grade_str))
        th.text(draw, (W - 20, 48), score_str, th.TextLevel.ACCENT, anchor="rm", color=th.ACCENT_SILVER)

    y = 86
    # 评分模板
    th.text(draw, (20, y), "评分模板", th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)
    th.text(draw, (86, y), data.template_name, th.TextLevel.MICRO, anchor="lm", color=th.TEXT_MAIN)

    draw.line([(20, y + 16), (W - 20, y + 16)], fill=th.DIVIDER, width=1)

    # 标题行
    y += 36
    th.text(draw, (20, y), "基础属性", th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)
    th.text(draw, (W // 2 + 10, y), "伤害词条", th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)

    y += 26
    start_y = y

    # 左列：基础属性
    for i, prop in enumerate(data.base_props):
        c = data.base_colors[i] if i < len(data.base_colors) and data.base_colors[i] else th.TEXT_MAIN
        th.text(draw, (20, start_y + i * 28), prop.name, th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)
        th.text(draw, (W // 2 - 10, start_y + i * 28), prop.value, th.TextLevel.MICRO, anchor="rm", color=c)

    # 右列：伤害词条
    for i, prop in enumerate(data.dmg_props):
        c = data.dmg_colors[i] if i < len(data.dmg_colors) and data.dmg_colors[i] else th.TEXT_MAIN
        th.text(draw, (W // 2 + 10, start_y + i * 28), prop.name, th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)
        th.text(draw, (W - 20, start_y + i * 28), prop.value, th.TextLevel.MICRO, anchor="rm", color=c)

    return layer, H
