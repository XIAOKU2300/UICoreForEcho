# -*- coding: utf-8 -*-
"""顶栏区块: 身份识别(头像/昵称/UID/等级/品牌标)。全幅。
这是骨架自带的样板 block,演示契约用法。
"""


def render(data, th):
    W = th.CARD_W
    H = 130  # 增高,避免文字被截
    layer, draw = th.new_layer(W, H)

    # 底部分隔线
    draw.line([(40, H - 1), (W - 40, H - 1)], fill=th.DIVIDER, width=1)

    # 头像占位圆 — 用 cyan 描边
    cx, cy, r = 76, H // 2, 34
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 48, 72, 200),
                 outline=th.ACCENT_CYAN, width=2)

    # 昵称 + UID
    th.text(draw, (128, cy - 12), data.player_name or "---", th.TextLevel.TITLE, anchor="lm")
    th.text(draw, (128, cy + 16), "UID " + (data.uid or "--------"), th.TextLevel.ACCENT, anchor="lm")

    # 等级数据区 (中部) — 给足垂直空间
    mid_y1 = cy - 14
    mid_y2 = cy + 14
    th.text(draw, (460, mid_y1), "联觉等级", th.TextLevel.LABEL, anchor="mm")
    th.text(draw, (460, mid_y2), ("Lv." + str(data.union_level)) if data.union_level is not None else "Lv.--",
            th.TextLevel.VALUE, anchor="mm", color=th.ACCENT_SILVER)
    th.text(draw, (620, mid_y1), "索拉等阶", th.TextLevel.LABEL, anchor="mm")
    th.text(draw, (620, mid_y2), str(data.world_level) if data.world_level is not None else "--",
            th.TextLevel.ACCENT, anchor="mm")

    # 品牌标: logo 右对齐
    import os
    from PIL import Image as _Img
    _logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_white.png")
    try:
        _logo = _Img.open(_logo_path).convert("RGBA")
        _lh = 36
        _lw = int(_logo.width * _lh / _logo.height)
        _logo = _logo.resize((_lw, _lh), _Img.LANCZOS)
        layer.alpha_composite(_logo, dest=(W - 40 - _lw, cy - _lh // 2))
    except Exception:
        th.text(draw, (W - 40, cy), "EchoMatrix", th.TextLevel.TITLE, anchor="rm", color=th.ACCENT_SILVER)

    return layer, H
