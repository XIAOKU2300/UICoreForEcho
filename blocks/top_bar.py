# -*- coding: utf-8 -*-
"""顶栏区块: 身份识别(头像/昵称/UID/等级/品牌标)。全幅。
这是骨架自带的样板 block,演示契约用法。
"""


def render(data, th):
    W = th.CARD_W
    H = 120
    layer, draw = th.new_layer(W, H)

    # 头像占位圆 (圆心 80,80 半径36)
    cx, cy, r = 80, 80, 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 44, 54, 255),
                 outline=th.ACCENT_SILVER, width=2)

    # 昵称 + UID
    th.text(draw, (134, 64), data.player_name or "---", th.TextLevel.TITLE, anchor="lm")
    th.text(draw, (134, 92), "UID " + (data.uid or "--------"), th.TextLevel.ACCENT, anchor="lm")

    # 等级数据区 (中部)
    th.text(draw, (440, 60), "联觉等级", th.TextLevel.LABEL, anchor="mm")
    th.text(draw, (440, 88), ("Lv." + str(data.union_level)) if data.union_level is not None else "Lv.--",
            th.TextLevel.VALUE, anchor="mm", color=th.ACCENT_SILVER)
    th.text(draw, (600, 60), "索拉等阶", th.TextLevel.LABEL, anchor="mm")
    th.text(draw, (600, 88), str(data.world_level) if data.world_level is not None else "--",
            th.TextLevel.ACCENT, anchor="mm")

    # 品牌标(绝对右对齐)
    th.text(draw, (W - 40, 70), "EchoMatrix", th.TextLevel.TITLE, anchor="rm", color=th.ACCENT_SILVER)

    return layer, H
