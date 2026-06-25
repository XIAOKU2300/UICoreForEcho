"""right_echo_card — single echo card block (main prop + sub grid)."""
from __future__ import annotations

from PIL import ImageDraw
from typing import Any


def render(data: Any, th: Any):
    """Render one echo card.

    Parameters
    ----------
    data : EchoCardData
        Fields: name, level, score, grade, cost, icon_image,
        main_prop (Prop | None), sub_props (list[Prop]),
        main_color (RGBA | None), sub_colors (list[RGBA | None]).
    th : Theme
        Theme helper providing drawing primitives.

    Returns
    -------
    (layer, height) : (Image.Image, int)
    """
    W = th.RIGHT_TRACK[1]  # 350
    H = 190  # 增高避免文字被底部截断

    layer, draw = th.new_layer(W, H)

    # ── holo panel background ──────────────────────────────────
    th.holo_panel(draw, (0, 0, W, H))

    # ── empty echo guard ───────────────────────────────────────
    if data.name == "---" and data.main_prop is None:
        th.text(
            draw,
            (W // 2, H // 2),
            "\u672a\u88c5\u5907",
            th.TextLevel.LABEL,
            color=th.TEXT_SUB,
            anchor="mm",
        )
        return layer, H

    # ── top row (y=12) ────────────────────────────────────────
    # icon placeholder 28x28 at (16, 12)
    if getattr(data, "icon_image", None) is not None:
        icon = data.icon_image.resize((28, 28))
        layer.paste(icon, (16, 12), icon)
    else:
        draw.rectangle((16, 12, 44, 40), fill=(60, 60, 60, 120))

    # name
    th.text(draw, (52, 26), data.name, th.TextLevel.LABEL, color=th.TEXT_MAIN)

    # right-aligned: "Lv.{level} {score}分"
    score_part = ""
    if data.score is not None:
        score_part = f" {data.score:.1f}\u5206"
    level_text = f"Lv.{data.level}{score_part}"
    th.text(
        draw,
        (W - 16, 26),
        level_text,
        th.TextLevel.ACCENT,
        anchor="rm",
    )

    # ── main prop row (y=56) ──────────────────────────────────
    if data.main_prop is not None:
        name_color = data.main_color if data.main_color is not None else th.TEXT_SUB
        val_color = data.main_color if data.main_color is not None else th.TEXT_MAIN

        th.text(
            draw,
            (16, 56),
            data.main_prop.name,
            th.TextLevel.VALUE,
            color=name_color,
        )
        th.text(
            draw,
            (W - 16, 56),
            data.main_prop.value,
            th.TextLevel.VALUE,
            color=val_color,
            anchor="rm",
        )

    # ── sub-props grid (y0=88, row_h=22) ─────────────────────
    y0 = 96
    row_h = 26
    sub_list = data.sub_props or []
    sub_colors = getattr(data, "sub_colors", []) or []

    for i, prop in enumerate(sub_list):
        if i >= 5:
            break

        # column layout: left 3, right 2
        if i < 3:
            col_name_x = 16
            col_val_x = 160
            row = i
        else:
            col_name_x = 180
            col_val_x = W - 16  # ~334
            row = i - 3

        y = y0 + row * row_h

        color_i = sub_colors[i] if i < len(sub_colors) else None
        name_color = color_i if color_i is not None else th.TEXT_SUB
        val_color = color_i if color_i is not None else th.TEXT_MAIN

        th.text(draw, (col_name_x, y), prop.name, th.TextLevel.MICRO, color=name_color)
        th.text(
            draw,
            (col_val_x, y),
            prop.value,
            th.TextLevel.MICRO,
            color=val_color,
            anchor="rm",
        )

    return layer, H
