# -*- coding: utf-8 -*-
"""中轨声骸汇总区块 (方案D 改造版).

在原"基础属性 / 伤害词条"双栏汇总之上, 加 3 个声骸级摘要:
  1. 套装组合带 — 5 个色块对应 5 张声骸的套装色, 一眼看出 X/5 件套
  2. Cost 总览  — Σcost / 12 槽位指示, 超装/欠装可视化
  3. 主套装色  — 把汇总面板的强调色换成"出现次数最多的套装"色

依赖: theme.sonata_color / theme.cost_pips
"""
from __future__ import annotations
from collections import Counter

from PIL import ImageDraw


def _dominant_sonata(echoes, th):
    """从 echo 列表里挑出现次数最多的套装名 + 其颜色 + 件数。"""
    if not echoes:
        return None, th.SONATA_FALLBACK, 0
    names = [getattr(e, "sonata", None) for e in echoes if getattr(e, "sonata", None)]
    if not names:
        return None, th.SONATA_FALLBACK, 0
    most_name, count = Counter(names).most_common(1)[0]
    return most_name, th.sonata_color(most_name), count


def render(data, th, echoes=None):
    """渲染中区声骸汇总。

    新参数 echoes: 可选, 用于绘制套装组合带 / Cost 总览。
    旧调用签名仍兼容 (echoes 缺省时跳过新摘要)。
    """
    if data is None:
        return None

    W = th.MID_TRACK[1]

    # 是否带新摘要 (套装条 + cost 条) — 为 echoes 留 56px
    has_new_summary = bool(echoes)
    summary_h = 64 if has_new_summary else 0

    max_rows = max(len(data.base_props), len(data.dmg_props))
    H = 80 + summary_h + 40 + (max_rows * 28) + 24

    layer, draw = th.new_layer(W, H)

    # 主套装色 — 用于面板强调色
    dom_name, dom_color, dom_count = _dominant_sonata(echoes or [], th)
    accent = dom_color if dom_count >= 2 else th.ACCENT_VIOLET

    th.holo_panel(draw, (0, 0, W, H), highlight=True, accent_color=accent)

    # 标题 + 主套装提示
    th.title(draw, 20, 30, "声骸加成汇总")
    if dom_name and dom_count >= 2:
        # 标题后跟一行小字: "凝夜白霜 ×3"
        suffix = f"{dom_name} ×{dom_count}"
        th.text(draw, (20 + th.text_w("声骸加成汇总", th.TextLevel.TITLE) + 14, 32),
                suffix, th.TextLevel.MICRO, color=accent)

    # 评级和评分在右上角
    grade_str = (data.grade or "--").upper()
    score_str = f"{data.score:.2f}分" if data.score else "--"

    if grade_str:
        th.grade_chip(draw, W - 20, 22, grade_str, anchor="rm")
        th.text(draw, (W - 20, 50), score_str, th.TextLevel.ACCENT,
                anchor="rm", color=accent)

    # ── 方案D 新摘要: 套装组合带 + Cost 总览 ─────────────
    if has_new_summary:
        sum_y = 64
        # 套装组合带 — 5 个 color slot
        slot_w = (W - 40 - 4 * 6) // 5
        slot_h = 18
        for i in range(5):
            x0 = 20 + i * (slot_w + 6)
            x1 = x0 + slot_w
            if i < len(echoes) and echoes[i] is not None:
                e = echoes[i]
                e_name = getattr(e, "sonata", None)
                e_col = th.sonata_color(e_name) if e_name else th.SONATA_FALLBACK
                # 主套装高亮, 其他套装弱化
                if dom_name and e_name == dom_name:
                    fill = e_col
                else:
                    fill = (e_col[0], e_col[1], e_col[2], 140)
            else:
                fill = (60, 70, 90, 140)
            try:
                draw.rounded_rectangle((x0, sum_y, x1, sum_y + slot_h),
                                       radius=4, fill=fill)
            except (AttributeError, TypeError):
                draw.rectangle((x0, sum_y, x1, sum_y + slot_h), fill=fill)

        # Cost 总览 — Σcost / 12
        total_cost = sum(int(getattr(e, "cost", 0) or 0) for e in echoes)
        cost_y = sum_y + slot_h + 6
        # 12 cost slot 横排
        cost_slot_w = (W - 40) // 12 - 2
        for i in range(12):
            x0 = 20 + i * (cost_slot_w + 2)
            x1 = x0 + cost_slot_w
            if i < total_cost:
                # 已用槽位 - 主套装色
                fill = accent
            else:
                fill = (60, 70, 90, 120)
            draw.rectangle((x0, cost_y, x1, cost_y + 4), fill=fill)
        # cost 文字
        th.text(draw, (W - 20, cost_y + 2), f"COST {total_cost}/12",
                th.TextLevel.MICRO, color=accent if total_cost <= 12 else th.ERROR,
                anchor="rm")

    # 评分模板
    y = 86 + summary_h
    th.text(draw, (20, y), "评分模板", th.TextLevel.MICRO, anchor="lm",
            color=th.TEXT_SUB)
    th.text(draw, (86, y), data.template_name, th.TextLevel.MICRO, anchor="lm",
            color=th.TEXT_MAIN)

    draw.line([(20, y + 16), (W - 20, y + 16)], fill=th.DIVIDER, width=1)

    # 标题行
    y += 36
    th.text(draw, (20, y), "基础属性", th.TextLevel.MICRO, anchor="lm",
            color=th.TEXT_SUB)
    th.text(draw, (W // 2 + 10, y), "伤害词条", th.TextLevel.MICRO, anchor="lm",
            color=th.TEXT_SUB)

    y += 26
    start_y = y

    # 左列：基础属性
    for i, prop in enumerate(data.base_props):
        c = data.base_colors[i] if i < len(data.base_colors) and data.base_colors[i] else th.TEXT_MAIN
        th.text(draw, (20, start_y + i * 28), prop.name, th.TextLevel.MICRO,
                anchor="lm", color=th.TEXT_SUB)
        th.text(draw, (W // 2 - 10, start_y + i * 28), prop.value,
                th.TextLevel.MICRO, anchor="rm", color=c)

    # 右列：伤害词条
    for i, prop in enumerate(data.dmg_props):
        c = data.dmg_colors[i] if i < len(data.dmg_colors) and data.dmg_colors[i] else th.TEXT_MAIN
        th.text(draw, (W // 2 + 10, start_y + i * 28), prop.name,
                th.TextLevel.MICRO, anchor="lm", color=th.TEXT_SUB)
        th.text(draw, (W - 20, start_y + i * 28), prop.value,
                th.TextLevel.MICRO, anchor="rm", color=c)

    return layer, H
