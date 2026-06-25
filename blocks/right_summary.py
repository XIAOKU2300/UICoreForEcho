"""right_summary — terminal block (highlight panel + total score + crit ratio)."""
from __future__ import annotations

from PIL import ImageDraw
from typing import Any


def render(data: Any, th: Any):
    """Render the summary / terminal block.

    Parameters
    ----------
    data : SummaryData
        Fields: total_score (float | None), total_grade (str | None),
        crit_rate (float | None), crit_dmg (float | None).
    th : Theme
        Theme helper providing drawing primitives.

    Returns
    -------
    (layer, height) : (Image.Image, int)
    """
    W = th.RIGHT_TRACK[1]  # 350
    H = 200

    layer, draw = th.new_layer(W, H)

    # ── highlighted holo panel background ──────────────────────
    th.holo_panel(draw, (0, 0, W, H), highlight=True, accent_color=th.ACCENT_GOLD)
    th.aim_frame(draw, (0, 0, W, H))

    # ── title ─────────────────────────────────────────────────
    th.title(draw, 16, 28, "\u8fd0\u7b97\u7ec8\u7aef")

    # ── total score area (y=56) ───────────────────────────────
    # grade letter — left
    grade_text = (data.total_grade or "").upper()
    if grade_text:
        th.text(
            draw,
            (16, 80),
            grade_text,
            th.TextLevel.SCORE_BIG,
            color=th.grade_color(grade_text),
        )

    # score value — right-aligned
    if data.total_score is not None:
        score_str = f"{data.total_score:.1f}"
    else:
        score_str = "--"
    th.text(
        draw,
        (W - 16, 80),
        score_str,
        th.TextLevel.SCORE_BIG,
        color=th.ACCENT_SILVER,
        anchor="rm",
    )

    # label below
    th.text(draw, (16, 108), "\u7efc\u5408\u8bc4\u5206", th.TextLevel.LABEL, color=th.TEXT_SUB)

    # ── crit ratio area (y=130+) ──────────────────────────────
    y_label = 130
    line_h = 24

    # ratio value
    if (
        data.crit_rate is not None
        and data.crit_dmg is not None
        and data.crit_rate != 0
    ):
        ratio = data.crit_dmg / data.crit_rate
        ratio_str = f"1 : {ratio:.1f}"
    else:
        ratio = None
        ratio_str = "--"

    # row 1 — crit ratio
    th.text(draw, (16, y_label), "\u53cc\u7206\u6bd4", th.TextLevel.LABEL, color=th.TEXT_SUB)
    th.text(
        draw,
        (W - 16, y_label),
        ratio_str,
        th.TextLevel.VALUE,
        anchor="rm",
    )

    # row 2 — ideal ratio
    th.text(
        draw,
        (16, y_label + line_h),
        "\u7406\u60f3\u53cc\u7206",
        th.TextLevel.MICRO,
        color=th.TEXT_SUB,
    )
    th.text(
        draw,
        (W - 16, y_label + line_h),
        "1 : 2",
        th.TextLevel.MICRO,
        color=th.TEXT_SUB,
        anchor="rm",
    )

    # row 3 — verdict
    th.text(
        draw,
        (16, y_label + line_h * 2),
        "\u8bc4\u4ef7",
        th.TextLevel.LABEL,
        color=th.TEXT_SUB,
    )
    if ratio is not None:
        if abs(ratio - 2.0) <= 0.3:
            verdict = "\u5747\u8861"
            verdict_color = th.ACCENT_CYAN
        elif ratio > 2.3:
            verdict = "\u66b4\u4f24\u504f\u9ad8"
            verdict_color = th.WARNING
        else:  # ratio < 1.7
            verdict = "\u66b4\u51fb\u504f\u9ad8"
            verdict_color = th.WARNING
    else:
        verdict = "--"
        verdict_color = th.TEXT_SUB

    th.text(
        draw,
        (W - 16, y_label + line_h * 2),
        verdict,
        th.TextLevel.LABEL,
        color=verdict_color,
        anchor="rm",
    )

    return layer, H
