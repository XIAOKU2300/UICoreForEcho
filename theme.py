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
# 配色 (RGBA)
# ──────────────────────────────────────────────────────────
BG_MAIN = (11, 13, 18, 255)            # 空天暗底 #0B0D12
PANEL_FILL = (21, 24, 33, 204)         # 全息底板 #151821 @80%
PANEL_FILL_HI = (28, 33, 46, 230)      # 高亮区块(运算终端) 更亮
HOLO_EDGE = (0, 229, 255, 255)         # 青色发光顶边 #00E5FF
ACCENT_SILVER = (226, 232, 240, 255)   # 星尘白(核心数字/标题) #E2E8F0
ACCENT_CYAN = (0, 229, 255, 255)       # 数据荧青(等级/引导)
TEXT_MAIN = (248, 250, 252, 255)       # 主文字 #F8FAFC
TEXT_SUB = (148, 163, 184, 255)        # 次文字/标签 #94A3B8
DIVIDER = (51, 65, 85, 255)            # 分隔/边框 #334155
DOT_GUIDE = (148, 163, 184, 120)       # 点阵引导线(半透灰蓝)

# 状态色
SUCCESS = (16, 185, 129, 255)
WARNING = (245, 158, 11, 255)
ERROR = (239, 68, 68, 255)

# 评级色 C→SSS
GRADE_COLORS = {
    "c": (100, 116, 139, 255),
    "b": (14, 165, 233, 255),
    "a": (139, 92, 246, 255),
    "s": (244, 63, 94, 255),
    "ss": (0, 229, 255, 255),
    "sss": (255, 255, 255, 255),
}

# ──────────────────────────────────────────────────────────
# 布局常量
# ──────────────────────────────────────────────────────────
CARD_W = 1200
MARGIN = 40
GAP = 16                                # 标准区块间距
COL_GAP = 16
RADIUS = 12

# 三轨 x 基准 (起点, 宽度)
LEFT_TRACK = (40, 380)                  # 左轨 x40-420
MID_TRACK = (440, 350)                  # 中轨 x440-790
RIGHT_TRACK = (810, 350)                # 右轨 x810-1160
TRACK_TOP = 140                         # 三轨内容起始 y(顶栏之下)

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
    TextLevel.TITLE: ("misans", 20, ACCENT_SILVER),
    TextLevel.LABEL: ("misans", 18, TEXT_SUB),
    TextLevel.VALUE: ("iosevka", 22, TEXT_MAIN),
    TextLevel.ACCENT: ("iosevka", 20, ACCENT_CYAN),
    TextLevel.NAME_BIG: ("youshe", 48, ACCENT_SILVER),
    TextLevel.SCORE_BIG: ("tektur", 52, ACCENT_SILVER),
    TextLevel.MICRO: ("misans", 14, TEXT_SUB),
}


# ──────────────────────────────────────────────────────────
# 绘制工厂方法 —— 区块只调这些, 保证视觉统一
# ──────────────────────────────────────────────────────────
def new_layer(w: int, h: int) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    """创建一张透明局部图层 + 其 draw。区块在此图层内用局部坐标(0,0)起绘。"""
    layer = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def holo_panel(draw: ImageDraw.ImageDraw, bbox, highlight: bool = False) -> None:
    """绘制全息科幻底板: 半透墨色底 + 青色发光顶边 + 圆角。
    bbox = (x0, y0, x1, y1) 局部坐标。highlight=True 用更亮的底(运算终端)。"""
    x0, y0, x1, y1 = bbox
    fill = PANEL_FILL_HI if highlight else PANEL_FILL
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=RADIUS, fill=fill, outline=DIVIDER, width=1)
    except AttributeError:
        draw.rectangle((x0, y0, x1, y1), fill=fill, outline=DIVIDER, width=1)
    # 青色发光顶边(顶部内缩圆角处一条亮线)
    draw.line([(x0 + RADIUS, y0 + 1), (x1 - RADIUS, y0 + 1)], fill=HOLO_EDGE, width=1)


def title(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    """区块标题 + 青色点缀短线(标题左下)。锚点 lm。"""
    f, size, color = _LEVEL_MAP[TextLevel.TITLE]
    draw.text((x, y), text, font=font(f, size), fill=color, anchor="lm")
    draw.line([(x, y + 14), (x + 28, y + 14)], fill=ACCENT_CYAN, width=2)


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
