# -*- coding: utf-8 -*-
"""right_echo_card — 方案D: 声骸卡片重设计 (统一模板, 所有角色通用)

视觉改进点:
1. 套装高亮: 卡片左侧贯穿色条 + 顶边发光线 + 套装名 pill 用套装色
2. 词条层级: 主词条强调放大; 副词条按 tier (god/good/normal/bad) 分级着色
                + 行首小色点提示层级, 同时弱化「劣」词条避免视觉污染
3. 评分槽: 右下角小进度条, 直接对比该件评分占满分百分比

依赖: theme.sonata_color / theme.sonata_panel / theme.sonata_pill /
      theme.classify_tier / theme.tier_color / theme.score_bar
所有角色都共用这一份渲染逻辑, 无需角色相关分支。
"""
from __future__ import annotations

from typing import Any


def render(data: Any, th: Any):
    W = th.RIGHT_TRACK[1]  # 350
    H = 230                # 比基线 +40 给词条/进度条更宽松呼吸

    layer, draw = th.new_layer(W, H)

    # ── 空件兜底 ─────────────────────────────────────────────
    if data.name == "---" and data.main_prop is None:
        # 用更冷静的空态: 灰阶毛玻璃 + 居中标签
        th.holo_panel(draw, (0, 0, W, H))
        th.text(
            draw,
            (W // 2, H // 2),
            "未装备",  # 未装备
            th.TextLevel.LABEL,
            color=th.TEXT_SUB,
            anchor="mm",
        )
        return layer, H

    # ── 套装色 + 染色毛玻璃面板 ──────────────────────────────
    sonata_name = getattr(data, "sonata", None)
    sonata_rgba = th.sonata_color(sonata_name)
    th.sonata_panel(draw, (0, 0, W, H), sonata_rgba)

    # ── 顶部区: 图标 + 名字 + Lv + 套装pill ─────────────────
    icon_x, icon_y, icon_s = 18, 14, 36
    if getattr(data, "icon_image", None) is not None:
        try:
            icon = data.icon_image.resize((icon_s, icon_s))
            layer.paste(icon, (icon_x, icon_y), icon)
        except Exception:
            draw.rectangle((icon_x, icon_y, icon_x + icon_s, icon_y + icon_s),
                           fill=(60, 70, 90, 140))
    else:
        # 占位: 套装色调暗
        ph = (sonata_rgba[0] // 3, sonata_rgba[1] // 3, sonata_rgba[2] // 3, 140)
        try:
            draw.rounded_rectangle(
                (icon_x, icon_y, icon_x + icon_s, icon_y + icon_s),
                radius=6, fill=ph,
            )
        except (AttributeError, TypeError):
            draw.rectangle(
                (icon_x, icon_y, icon_x + icon_s, icon_y + icon_s),
                fill=ph,
            )

    # 名字 (LABEL)
    name_x = icon_x + icon_s + 10
    th.text(draw, (name_x, icon_y + 6), data.name,
            th.TextLevel.LABEL, color=th.TEXT_MAIN)

    # 等级 + COST (ACCENT 小)
    cost_str = f"·{data.cost}C" if getattr(data, "cost", None) is not None else ""
    lv_str = f"Lv.{data.level}{cost_str}" if data.level is not None else cost_str.lstrip("·")
    if lv_str:
        th.text(draw, (name_x, icon_y + 26), lv_str,
                th.TextLevel.MICRO, color=th.TEXT_SUB)

    # 套装pill (右上角)
    if sonata_name:
        th.sonata_pill(draw, (W - 14, icon_y + 2), sonata_name,
                       sonata_rgba, anchor="rt")

    # ── 主词条强调区 (y≈64) ──────────────────────────────────
    # 单独一行加重强调: 字号加粗 + 套装色尾点
    y_main = 70
    if data.main_prop is not None:
        # 名字 (LABEL 灰白)
        th.text(draw, (18, y_main), data.main_prop.name,
                th.TextLevel.LABEL, color=th.TEXT_SUB)
        # 值 (SCORE_BIG 不合适, 用 VALUE 但加粗显著)
        # 主词条统一用套装色, 与套装色调呼应
        main_val_color = data.main_color if data.main_color is not None else sonata_rgba
        th.text(draw, (W - 18, y_main), data.main_prop.value,
                th.TextLevel.VALUE, color=main_val_color, anchor="rm")

    # 主词条下方分隔线 (套装色弱化)
    sep_y = y_main + 22
    sep_color = (sonata_rgba[0], sonata_rgba[1], sonata_rgba[2], 70)
    draw.line([(18, sep_y), (W - 18, sep_y)], fill=sep_color, width=1)

    # ── 副词条区 (y0=104) — 单列 5 行, 行首小色点 + 名/值 ─
    sub_list = data.sub_props or []
    sub_colors = getattr(data, "sub_colors", []) or []

    y0 = sep_y + 14
    row_h = 22
    for i, prop in enumerate(sub_list[:5]):
        y = y0 + i * row_h
        col_i = sub_colors[i] if i < len(sub_colors) else None
        tier = th.classify_tier(col_i)
        c = th.tier_color(tier)

        # 行首色点 (tier 视觉锚)
        dot_r = th.TIER_DOT_R
        dot_cx = 22
        dot_cy = y
        if tier == "bad":
            # 劣词条: 空心圈, 不抢戏
            draw.ellipse(
                (dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r),
                outline=c, width=1,
            )
        else:
            draw.ellipse(
                (dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r),
                fill=c,
            )

        # 名字 (劣词条: TIER_BAD; 普通: TEXT_SUB; 神/优: tier 色淡)
        if tier == "bad":
            name_color = th.TIER_BAD
        elif tier in ("god", "good"):
            # 名字用次色保持可读, 让值发光
            name_color = th.TEXT_SUB
        else:
            name_color = th.TEXT_SUB
        th.text(draw, (32, y), prop.name,
                th.TextLevel.MICRO, color=name_color)

        # 值 (tier 色, 右对齐)
        th.text(draw, (W - 18, y), prop.value,
                th.TextLevel.MICRO, color=c, anchor="rm")

    # ── 评分进度条 (右下角, y≈y0+5*row_h+8) ────────────────
    sc = data.score
    grade = (data.grade or "").upper()
    bar_y = y0 + 5 * row_h + 6
    bar_h = 4
    # 满分按 50 估算 (单件常见上限; 后端可调)
    # TODO[后端对接]: 提供单件评分的实际上限, 这里默认 50
    score_max = 50.0

    # 评分文字 (左侧, 套装色)
    if sc is not None:
        score_text = f"{sc:.1f}"
    else:
        score_text = "--"
    th.text(draw, (18, bar_y + 8), score_text,
            th.TextLevel.ACCENT, color=sonata_rgba)
    # 等级 (中间偏右)
    if grade:
        th.text(draw, (90, bar_y + 8), grade,
                th.TextLevel.LABEL, color=th.grade_color(grade))

    # 进度条 (右半)
    bar_x0, bar_x1 = 130, W - 18
    th.score_bar(
        draw, (bar_x0, bar_y + 4, bar_x1, bar_y + 4 + bar_h),
        sc if sc is not None else 0.0, score_max, sonata_rgba,
    )

    return layer, H
