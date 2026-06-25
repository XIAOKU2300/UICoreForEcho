# -*- coding: utf-8 -*-
"""全局主题(冻结·只读)。

封装所有配色、字体实例、间距、轨道坐标,并提供"绘制工厂方法":
区块只调用 theme.holo_panel / theme.text / theme.guide_dots,
不自己写底板/边框/字体逻辑 —— 视觉一致性被强制收归主题层。

EchoMatrix 银白冷调科技风。
"""
from __future__ import annotations
import os
from enum import Enum
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# ──────────────────────────────────────────────────────────
# 配色 (RGBA) — 鸣潮·声骸活力风:
# 整体提亮，面板走毛玻璃路线(高透明+亮底)
# ──────────────────────────────────────────────────────────
BG_MAIN = (20, 24, 36, 255)            # 深靛蓝底(提亮) #141824
BG_GRADIENT_TOP = (28, 34, 52, 255)    # 顶部渐变上缘(提亮)
PANEL_FILL = (40, 48, 72, 160)         # 毛玻璃面板: 半透明蓝灰 @63%
PANEL_FILL_HI = (50, 60, 90, 180)     # 高亮毛玻璃面板
HOLO_EDGE = (100, 210, 255, 255)      # 主发光边: 明亮天蓝
ACCENT_SILVER = (235, 240, 250, 255)   # 星辉白(核心标题)
ACCENT_CYAN = (80, 220, 255, 255)      # 数据荧青
ACCENT_GOLD = (255, 200, 60, 255)      # 金色强调
ACCENT_VIOLET = (180, 120, 255, 255)   # 紫光
ACCENT_TEAL = (0, 230, 180, 255)       # 翡翠绿
TEXT_MAIN = (250, 252, 255, 255)       # 主文字(纯白)
TEXT_SUB = (170, 185, 210, 255)        # 次文字(提亮)
DIVIDER = (80, 95, 130, 200)           # 分隔线(提亮可见)
DOT_GUIDE = (140, 170, 220, 100)       # 点阵引导线

# 状态色 — 鲜活饱和
SUCCESS = (0, 220, 160, 255)           # 翠绿
WARNING = (255, 180, 40, 255)          # 琥珀金
ERROR = (255, 80, 90, 255)             # 珊瑚红

# 评级色 C→SSS — 彩虹色阶,体现「五彩缤纷」
GRADE_COLORS = {
    "c": (120, 135, 160, 255),         # 灰蓝
    "b": (60, 180, 255, 255),          # 天蓝
    "a": (160, 100, 255, 255),         # 电紫
    "s": (255, 70, 120, 255),          # 玫红
    "ss": (255, 200, 60, 255),         # 金
    "sss": (255, 240, 200, 255),       # 暖白金(微金光)
}

# ──────────────────────────────────────────────────────────
# 布局常量
# ──────────────────────────────────────────────────────────
CARD_W = 1200
MARGIN = 40
GAP = 20                                # 区块间距(16→20,给面板呼吸)
COL_GAP = 16
RADIUS = 14                             # 圆角略大,更现代

# 三轨 x 基准 (起点, 宽度)
LEFT_TRACK = (40, 380)                  # 左轨 x40-420
MID_TRACK = (440, 350)                  # 中轨 x440-790
RIGHT_TRACK = (810, 350)                # 右轨 x810-1160
TRACK_TOP = 150                         # 三轨内容起始 y(顶栏130+间距)

# ──────────────────────────────────────────────────────────
# 字体
# ──────────────────────────────────────────────────────────
_FONT_FILES = {
    "misans": "小米MiSans-Medium.ttf",
    "iosevka": "Iosevka-Regular.ttc",
    "tektur": "Tektur-SemiCondensed-Regular.ttf",
    "youshe": "优设标题黑.ttf",
}
_font_cache = {}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    """获取字体实例。kind: misans/iosevka/tektur/youshe。"""
    key = (kind, size)
    if key not in _font_cache:
        path = os.path.join(_FONT_DIR, _FONT_FILES.get(kind, _FONT_FILES["misans"]))
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


class TextLevel(Enum):
    """文本层级 → 自动映射 字体/字号/颜色。"""
    TITLE = "title"        # 区块标题
    LABEL = "label"        # 属性标签(次要)
    VALUE = "value"        # 数值(主)
    ACCENT = "accent"      # 强调(等级/荧青)
    NAME_BIG = "name_big"  # 巨型角色名
    SCORE_BIG = "score_big"  # 总评分超大数字
    MICRO = "micro"        # 免责声明等极小字


_LEVEL_MAP = {
    TextLevel.TITLE: ("misans", 26, ACCENT_SILVER),       # 标题略大(24→26)
    TextLevel.LABEL: ("misans", 18, TEXT_SUB),            # 标签缩小(20→18)拉开对比
    TextLevel.VALUE: ("iosevka", 28, TEXT_MAIN),          # 数值更突出(26→28)
    TextLevel.ACCENT: ("iosevka", 22, ACCENT_CYAN),
    TextLevel.NAME_BIG: ("youshe", 60, ACCENT_SILVER),   # 角色名更大(56→60)
    TextLevel.SCORE_BIG: ("tektur", 68, ACCENT_SILVER),  # 评分更突出(64→68)
    TextLevel.MICRO: ("misans", 13, TEXT_SUB),            # 微型略缩(14→13)
}


# ──────────────────────────────────────────────────────────
# 绘制工厂方法 —— 区块只调这些, 保证视觉统一
# ──────────────────────────────────────────────────────────
def new_layer(w: int, h: int) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    """创建一张透明局部图层 + 其 draw。区块在此图层内用局部坐标(0,0)起绘。"""
    layer = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def holo_panel(draw: ImageDraw.ImageDraw, bbox, highlight: bool = False,
               accent_color=None, layer: Optional[Image.Image] = None) -> None:
    """绘制毛玻璃科幻底板: 多层半透叠加模拟 frosted glass + 发光顶边。
    bbox = (x0, y0, x1, y1) 局部坐标。highlight=True 用更亮的底。
    accent_color 可覆盖顶边颜色。layer 传入可做额外像素操作。"""
    x0, y0, x1, y1 = bbox
    fill = PANEL_FILL_HI if highlight else PANEL_FILL
    edge_color = accent_color or HOLO_EDGE

    # 毛玻璃底层: 主色圆角矩形
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=RADIUS, fill=fill)
    except AttributeError:
        draw.rectangle((x0, y0, x1, y1), fill=fill)

    # 毛玻璃第二层: 顶部亮带(模拟光线穿透磨砂玻璃的顶部高光)
    glow_h = 12
    for i in range(glow_h):
        alpha = int(30 * (1 - i / glow_h))
        glow_color = (255, 255, 255, alpha)
        draw.line([(x0 + RADIUS, y0 + 1 + i), (x1 - RADIUS, y0 + 1 + i)], fill=glow_color)

    # 顶部发光高亮线(2px)
    draw.line([(x0 + RADIUS, y0 + 1), (x1 - RADIUS, y0 + 1)], fill=edge_color, width=2)

    # 底边微光(1px,模拟玻璃底部反射)
    bottom_glow = (edge_color[0], edge_color[1], edge_color[2], 40)
    draw.line([(x0 + RADIUS, y1 - 1), (x1 - RADIUS, y1 - 1)], fill=bottom_glow, width=1)

    # 边框: 极细的亮边(模拟玻璃折射边缘)
    border_color = (200, 220, 255, 35)
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=RADIUS, outline=border_color, width=1)
    except (AttributeError, TypeError):
        draw.rectangle((x0, y0, x1, y1), outline=border_color, width=1)

    # 四角卡扣折线(缩小尺寸,更精致)
    bracket_color = edge_color if highlight else DIVIDER
    corner_brackets(draw, (x0, y0, x1, y1), length=10, color=bracket_color, width=2 if highlight else 1)


def corner_brackets(draw: ImageDraw.ImageDraw, bbox, length: int = 14,
                    color=None, width: int = 1) -> None:
    """在矩形四角画短促的直角折线(机甲卡扣修饰),不画全包围边框。"""
    x0, y0, x1, y1 = bbox
    c = color or DIVIDER
    L = length
    # 左上
    draw.line([(x0, y0 + L), (x0, y0), (x0 + L, y0)], fill=c, width=width)
    # 右上
    draw.line([(x1 - L, y0), (x1, y0), (x1, y0 + L)], fill=c, width=width)
    # 左下
    draw.line([(x0, y1 - L), (x0, y1), (x0 + L, y1)], fill=c, width=width)
    # 右下
    draw.line([(x1 - L, y1), (x1, y1), (x1, y1 - L)], fill=c, width=width)


def aim_frame(draw: ImageDraw.ImageDraw, bbox, color=None, width: int = 2) -> None:
    """瞄准框: 四角更长的折线 + 角点小方块(用于总评/运算终端的高潮区)。默认金色。"""
    x0, y0, x1, y1 = bbox
    c = color or ACCENT_GOLD
    L = 22
    for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        draw.line([(cx, cy + dy * L), (cx, cy), (cx + dx * L, cy)], fill=c, width=width)
        draw.rectangle((cx - 2, cy - 2, cx + 2, cy + 2), fill=c)


def title(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    """区块标题 + 双色渐变点缀短线(标题左下)。锚点 lm。"""
    f, size, color = _LEVEL_MAP[TextLevel.TITLE]
    draw.text((x, y), text, font=font(f, size), fill=color, anchor="lm")
    # 双色渐变短线: 从 cyan 到 violet
    line_y = y + 16
    line_len = 32
    for i in range(line_len):
        t = i / line_len
        r = int(ACCENT_CYAN[0] * (1 - t) + ACCENT_VIOLET[0] * t)
        g = int(ACCENT_CYAN[1] * (1 - t) + ACCENT_VIOLET[1] * t)
        b = int(ACCENT_CYAN[2] * (1 - t) + ACCENT_VIOLET[2] * t)
        draw.point((x + i, line_y), fill=(r, g, b, 255))
        draw.point((x + i, line_y + 1), fill=(r, g, b, 255))


def text(draw: ImageDraw.ImageDraw, xy, content: str, level: TextLevel,
         anchor: str = "lm", color: Optional[Tuple[int, int, int, int]] = None) -> None:
    """按层级绘制文本。color 可覆盖层级默认色(用于好词条高亮)。"""
    f, size, default_color = _LEVEL_MAP[level]
    draw.text(xy, content, font=font(f, size), fill=color or default_color, anchor=anchor)


def text_w(content: str, level: TextLevel) -> int:
    """测量某层级文本宽度(用于右对齐计算)。"""
    f, size, _ = _LEVEL_MAP[level]
    fnt = font(f, size)
    try:
        return int(fnt.getlength(content))
    except Exception:
        return len(content) * size // 2


def guide_dots(draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int,
               step: int = 8, r: int = 1) -> None:
    """科技点阵引导线: 从 x0 到 x1 在 y 高度画一排小点(连接标签与数值, 消灭空白河流)。"""
    x = x0
    while x <= x1:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=DOT_GUIDE)
        x += step


def grade_color(grade: Optional[str]) -> Tuple[int, int, int, int]:
    """评级 → 颜色。"""
    if not grade:
        return TEXT_SUB
    return GRADE_COLORS.get(str(grade).lower(), ACCENT_SILVER)


def paste_layer(base: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    """把局部图层粘到主画布。"""
    base.alpha_composite(layer, dest=(x, y))


def bg_gradient(img: Image.Image) -> None:
    """在主画布上绘制微妙的顶部→底部渐变,打破纯色死板感。
    从 BG_GRADIENT_TOP 渐变到 BG_MAIN。"""
    draw = ImageDraw.Draw(img)
    h = img.height
    fade_h = min(400, h // 3)
    for i in range(fade_h):
        t = i / fade_h
        r = int(BG_GRADIENT_TOP[0] * (1 - t) + BG_MAIN[0] * t)
        g = int(BG_GRADIENT_TOP[1] * (1 - t) + BG_MAIN[1] * t)
        b = int(BG_GRADIENT_TOP[2] * (1 - t) + BG_MAIN[2] * t)
        draw.line([(0, i), (img.width, i)], fill=(r, g, b, 255))


def glow_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int,
                color: Tuple[int, int, int, int], rings: int = 4) -> None:
    """在指定位置画一圈辐射光晕(用于品质节点/选中态)。"""
    for i in range(rings):
        expand = r + i * 3
        alpha = int(color[3] * (1 - i / rings) * 0.4)
        glow = (color[0], color[1], color[2], alpha)
        draw.ellipse((cx - expand, cy - expand, cx + expand, cy + expand),
                     outline=glow, width=1)
