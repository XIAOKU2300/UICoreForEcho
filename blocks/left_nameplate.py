# -*- coding: utf-8 -*-
"""左轨名牌区块: 巨型角色名 + 等级 + 免责声明。
(评分已移到右下"运算终端",此处不再重复评分槽。)"""


def render(data, th):
    """data: NameplateData(char_name, char_level, total_score, total_grade)。返回 (layer, height)。"""
    W = th.LEFT_TRACK[1]  # 380
    H = 130
    layer, draw = th.new_layer(W, H)

    # 巨型角色名
    th.text(draw, (0, 0), data.char_name or "---", th.TextLevel.NAME_BIG, anchor="lt", color=th.ACCENT_SILVER)

    # 等级 + 青色点缀线
    lv_str = f"Lv.{data.char_level}" if data.char_level is not None else "Lv.--"
    th.text(draw, (0, 62), lv_str, th.TextLevel.LABEL, anchor="lt", color=th.ACCENT_CYAN)
    draw.line([(0, 92), (60, 92)], fill=th.ACCENT_CYAN, width=2)

    # 免责声明两行(左对齐,低调)
    th.text(draw, (0, 104), "非官方 · 数据由玩家社区自行计算", th.TextLevel.MICRO, anchor="lt", color=th.TEXT_SUB)
    th.text(draw, (0, 120), "不代表任何官方观点 · 仅供参考", th.TextLevel.MICRO, anchor="lt", color=th.TEXT_SUB)

    return layer, H
