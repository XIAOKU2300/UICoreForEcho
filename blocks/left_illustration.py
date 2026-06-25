# -*- coding: utf-8 -*-
"""左轨立绘区块: 无边框,四周渐变柔化融入背景(毛玻璃质感过渡)。"""
from PIL import Image as _PILImage, ImageDraw as _ID, ImageFilter


def render(data, th):
    W = th.LEFT_TRACK[1]  # 380
    H = 720
    layer, draw = th.new_layer(W, H)

    # 背景水印: 超大角色名横铺,极低透明度
    cname = getattr(data, "char_name", "") or ""
    if cname:
        wm = th.font("youshe", 96)
        draw.text((W // 2, H // 2), cname, font=wm, fill=(235, 240, 250, 20), anchor="mm")

    if data.pile_image is not None:
        img = data.pile_image.convert("RGBA")
        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), resample=3)  # LANCZOS

        # 居中贴到图层(底部对齐)
        paste_y = H - new_h
        layer.alpha_composite(img, dest=(0, paste_y))

        # 四周渐变遮罩: 底部最重,左右和顶部柔化边缘
        # 底部渐变(从下往上,高 260px)
        r, g, b = th.BG_MAIN[:3]
        fade_bottom = 260
        for i in range(fade_bottom):
            alpha = int(255 * (1 - i / fade_bottom) ** 1.5)
            y = H - fade_bottom + i
            if 0 <= y < H:
                draw.line([(0, y), (W, y)], fill=(r, g, b, alpha))

        # 顶部渐变(从上往下,高 120px)
        fade_top = 120
        for i in range(fade_top):
            alpha = int(180 * (1 - i / fade_top))
            y = i
            draw.line([(0, y), (W, y)], fill=(r, g, b, alpha))

        # 左侧渐变(从左往右,宽 60px)
        fade_left = 60
        for i in range(fade_left):
            alpha = int(160 * (1 - i / fade_left))
            draw.line([(i, 0), (i, H)], fill=(r, g, b, alpha))

        # 右侧渐变(从右往左,宽 40px)
        fade_right = 40
        for i in range(fade_right):
            alpha = int(120 * (1 - i / fade_right))
            x = W - fade_right + i
            draw.line([(x, 0), (x, H)], fill=(r, g, b, alpha))

    else:
        # 占位: 淡圆角矩形 + "立绘"提示
        pad = 40
        x0, y0, x1, y1 = pad, 80, W - pad, H - 80
        try:
            draw.rounded_rectangle(
                (x0, y0, x1, y1), radius=th.RADIUS,
                outline=th.DIVIDER, width=1,
            )
        except AttributeError:
            draw.rectangle((x0, y0, x1, y1), outline=th.DIVIDER, width=1)
        th.text(draw, (W // 2, (y0 + y1) // 2), "立绘", th.TextLevel.LABEL, anchor="mm")

    return layer, H
