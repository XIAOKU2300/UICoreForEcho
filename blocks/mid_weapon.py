# blocks/mid_weapon.py  -- 武器终端面板 (frozen)
"""Mid-block: 武器终端面板 — icon + name + level/refine + two stat rows with guide dots."""


def render(data, th):
    """Render the weapon holographic panel.

    Parameters
    ----------
    data : WeaponData
        .name        — str
        .level       — int | None
        .refine      — int | None
        .icon_image  — PIL.Image.Image | None
        .main_stat   — Prop | None  (has .name, .value)
        .sub_stat    — Prop | None  (has .name, .value)
    th : theme object
        Provides new_layer, holo_panel, title, text, guide_dots, text_w,
        TextLevel (TITLE / LABEL / VALUE / ACCENT), MID_TRACK, DIVIDER.

    Returns
    -------
    (PIL.Image.Image, int)  — (layer, height)
    """
    W = th.MID_TRACK[1]  # 350
    H = 180

    layer, draw = th.new_layer(W, H)

    # ── background panel + title ──
    th.holo_panel(draw, (0, 0, W, H))
    th.title(draw, 16, 28, "武器")

    # ── weapon icon (80×80 at top-left) ──
    icon_x, icon_y = 16, 50
    icon_sz = 80
    if getattr(data, "icon_image", None) is not None:
        icon = data.icon_image.resize((icon_sz, icon_sz))
        layer.paste(icon, (icon_x, icon_y), icon if icon.mode == "RGBA" else None)
    else:
        # placeholder: dark square + outline
        draw.rectangle(
            (icon_x, icon_y, icon_x + icon_sz, icon_y + icon_sz),
            fill=(30, 30, 40, 180),
            outline=(80, 100, 120, 160),
            width=1,
        )

    # ── weapon name + level/refine ──
    name = data.name or "--"
    th.text(draw, (92, 68), name, th.TextLevel.TITLE, anchor="lm")

    lv = data.level if data.level is not None else "--"
    rf = data.refine if data.refine is not None else "--"
    th.text(draw, (92, 96), f"Lv.{lv} 精{rf}", th.TextLevel.ACCENT, anchor="lm")

    # ── stat rows (y=130, spacing 30) ──
    stats = [
        ("攻击力", data.main_stat),
        ("副属性", data.sub_stat),
    ]
    for i, (fallback_name, prop) in enumerate(stats):
        y = 130 + i * 30

        label = prop.name if prop is not None else fallback_name
        value = prop.value if prop is not None else "--"

        # label (left)
        th.text(draw, (16, y), label, th.TextLevel.LABEL, anchor="lm")
        label_w = th.text_w(label, th.TextLevel.LABEL)

        # value (right)
        th.text(draw, (W - 16, y), value, th.TextLevel.VALUE, anchor="rm")
        val_w = th.text_w(value, th.TextLevel.VALUE)

        # guide dots between label and value
        dot_x1 = 16 + label_w + 8
        dot_x2 = W - 16 - val_w - 8
        if dot_x2 > dot_x1:
            th.guide_dots(draw, dot_x1, dot_x2, y)

    return layer, H
