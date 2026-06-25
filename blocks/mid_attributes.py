# blocks/mid_attributes.py  -- 基础属性全息面板 (frozen)
"""Mid-block: 基础属性全息面板. 点阵虚线连接标签和数值,消灭空白河流."""


def render(data, th):
    """Render the attributes holographic panel.

    Args:
        data: AttributesData with .props (list of Prop, each has .name / .value).
        th:   Theme object providing new_layer / holo_panel / title / text /
              guide_dots / TextLevel / MID_TRACK / text_w.

    Returns:
        (layer, height)
    """
    W = th.MID_TRACK[1]  # 350
    props = data.props
    row_h = 36
    pad_top = 60
    pad_bottom = 20
    h = pad_top + len(props) * row_h + pad_bottom

    layer, draw = th.new_layer(W, h)

    # 背景全息面板
    th.holo_panel(draw, (0, 0, W, h))

    # 标题
    th.title(draw, 20, 30, "属性")

    # 属性行
    for i, prop in enumerate(props):
        y = pad_top + i * row_h + row_h // 2

        # 标签 (左对齐)
        name = prop.name
        th.text(draw, (20, y), name, th.TextLevel.LABEL, anchor="lm")
        label_w = th.text_w(name, th.TextLevel.LABEL)

        # 数值 (右对齐)
        value = prop.value
        th.text(draw, (W - 20, y), value, th.TextLevel.VALUE, anchor="rm")
        val_w = th.text_w(value, th.TextLevel.VALUE)

        # 点阵虚线连接标签与数值
        dot_x1 = 20 + label_w + 10
        dot_x2 = W - 20 - val_w - 10
        if dot_x2 > dot_x1:
            th.guide_dots(draw, dot_x1, dot_x2, y)

    return layer, h
