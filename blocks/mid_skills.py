"""技能阵列面板 — mid_skills block."""


def render(data, th):
    """Render the skills array panel.

    Parameters
    ----------
    data : SkillsData
        .skills – list[SkillData], each with .type_name, .level, .icon_image
    th : theme object
        Provides new_layer, holo_panel, title, text, TextLevel, MID_TRACK, ACCENT_CYAN.

    Returns
    -------
    (PIL.Image.Image, int)  –  (layer, height)
    """
    skills = data.skills or []
    W = th.MID_TRACK[1]  # 350
    h = 56 + len(skills) * 44 + 16

    layer, draw = th.new_layer(W, h)

    # 背景面板 + 标题
    th.holo_panel(draw, (0, 0, W, h))
    th.title(draw, 16, 28, "技能")

    # 技能行  (y 起点 56, 行距 44)
    for i, skill in enumerate(skills):
        y = 56 + i * 44

        # 左侧图标占位  40×40
        icon_rect = (16, y - 16, 56, y + 16)
        if skill.icon_image:
            draw.bitmap((16, y - 16), skill.icon_image, mask=None)
        else:
            draw.rectangle(icon_rect, fill=(30, 30, 40))

        # 技能名
        th.text(draw, (68, y), skill.type_name, th.TextLevel.LABEL, anchor="lm")

        # 等级  右对齐  青色
        lv = f"Lv.{skill.level}" if skill.level is not None else "Lv.--"
        th.text(draw, (W - 16, y), lv, th.TextLevel.ACCENT, anchor="rm")

    return layer, h
