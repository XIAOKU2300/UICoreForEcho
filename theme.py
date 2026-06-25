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
# 声骸套装色调 (方案D - 声骸卡片重设计)
# 用于卡片左侧色条 + 套装名 pill + 顶部高光线
# 主色为饱和明亮的鸣潮渲染感配色
# ──────────────────────────────────────────────────────────
SONATA_COLORS = {
    # 冰系
    "凝夜白霜": (130, 220, 255, 255),     # 冰蓝
    # 火系
    "熔山裂谷": (255, 130, 70, 255),      # 熔橙
    # 雷/紫
    "彻空冥雷": (190, 130, 255, 255),     # 雷紫
    "行幽墨翟": (150, 90, 220, 255),      # 深紫
    # 风/青
    "啸谷长风": (110, 230, 195, 255),     # 青翠
    "翎羽迷踪": (110, 230, 195, 255),     # 同风系
    # 衍射/玫
    "漪澜浮录": (255, 110, 170, 255),     # 玫粉
    # 湮灭/金
    "浮星祛暗": (255, 210, 90, 255),      # 暖金
    "不绝余音": (255, 200, 60, 255),      # 强金
    # 沉日/暗
    "沉日劫明": (200, 100, 120, 255),     # 暗玫
    # 治疗 / 嫩绿
    "隐世回光": (170, 240, 130, 255),     # 嫩绿
    # 辅助 / 浅紫
    "轻云出月": (200, 180, 255, 255),     # 浅紫
    # 攻击共鸣 / 红
    "凌冽决断之心": (255, 140, 120, 255),
    # 防御 / 暖白
    "永夜星辰": (220, 230, 255, 255),
}
SONATA_FALLBACK = (180, 200, 230, 255)    # 未知套装兜底（中性银蓝）

# 词条层级色 (方案D - 词条评级显式化)
# 主词条/副词条按 adapter 传入的 sub_colors 反推 tier：
#   ACCENT_VIOLET → TIER_GOD     (神级)
#   SUCCESS       → TIER_GOOD    (优秀)
#   None          → TIER_NORMAL  (普通)
#   ERROR         → TIER_BAD     (劣)
TIER_GOD  = (200, 150, 255, 255)         # 紫光（最高级）
TIER_GOOD = (90, 230, 170, 255)          # 翠绿（优）
TIER_NORMAL = (240, 245, 252, 255)       # 偏白（普）
TIER_BAD  = (150, 160, 175, 255)         # 暗灰（劣 — 收弱不删除）
TIER_DOT_R = 4                            # 副词条行首小色点半径

# ──────────────────────────────────────────────────────────
# 着重词条高亮色 (EMPHASIS / Spotlight Highlight) — 方案D 后期加重 hook
# 用途: 对「双爆」「元素伤害」等关键词条做加重高亮显示。
# 设计原则:
#   - 高彩度 (OKLch chroma ≥ 0.18) + 中亮度 (L 65~78),
#     在毛玻璃深底 (PANEL_FILL) 上对比度 ≥ 7:1, 醒目但不刺眼。
#   - 与 TIER 色阶解耦: TIER 表「这条词条好不好」, EMPHASIS 表「这类词条该被注意」。
#     优先级 EMPHASIS > TIER (一条 暴击+神级 → 取 CRIT_HL)。
#
# 切换方式: right_echo_card 副词条循环里调 emphasis_for(prop.name);
#         返回 None 时维持 tier 色, 默认不破坏现有视觉。
# ──────────────────────────────────────────────────────────
CRIT_HL   = (255, 215, 95, 255)          # 暴击 / 暴击伤害 — 琥珀金 (鸣潮暴击官方色系)
DMG_HL    = (255, 130, 220, 255)         # 元素伤害加成 — 霓虹玫粉 (跳出蓝绿主调不撞套装色)
ENERGY_HL = (120, 255, 220, 255)         # 共鸣效率 — 冰荧青 (能量感视觉锚)
ATK_HL    = (255, 160, 100, 255)         # 攻击% / 生命% / 防御% — 熔橙 (攻击系恒色)
HEAL_HL   = (180, 255, 130, 255)         # 治疗效果加成 — 嫩绿 (生命系)

# 名称 → 高亮色 (按 in 包含匹配, 命中即返回; 顺序即优先级)
# 设计师可在此增删调序; 默认全部启用, 若需关闭某类只需注释对应行
EMPHASIS_MAP = [
    ("暴击伤害",   CRIT_HL),
    ("暴击",       CRIT_HL),
    ("双爆",       CRIT_HL),
    ("共鸣效率",   ENERGY_HL),
    ("治疗效果",   HEAL_HL),
    ("伤害加成",   DMG_HL),    # 冷凝/熔燃/衍射... 等元素伤
    ("攻击",       ATK_HL),    # 攻击 / 攻击百分比 都命中
    ("生命",       ATK_HL),
    ("防御",       ATK_HL),
]

# 是否启用 EMPHASIS 着重 (设计师后期可改 False 一键回到纯 tier 色)
EMPHASIS_ON = False

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


# ──────────────────────────────────────────────────────────
# 方案D 工具函数: 套装色 + 词条 tier
# ──────────────────────────────────────────────────────────
def sonata_color(name: Optional[str]) -> Tuple[int, int, int, int]:
    """套装名 → 主色。未知或 None → SONATA_FALLBACK。"""
    if not name:
        return SONATA_FALLBACK
    # 去掉常见后缀和空白后查表
    key = str(name).strip().split("·")[0].strip()
    return SONATA_COLORS.get(key, SONATA_FALLBACK)


def classify_tier(color: Optional[Tuple[int, int, int, int]]) -> str:
    """根据 adapter 传入的颜色反推词条 tier。
    返回 'god'/'good'/'normal'/'bad' 字符串。"""
    if color is None:
        return "normal"
    rgb = tuple(color[:3])
    if rgb == ACCENT_VIOLET[:3]:
        return "god"
    if rgb == SUCCESS[:3]:
        return "good"
    if rgb == ERROR[:3]:
        return "bad"
    return "normal"


def tier_color(tier: str) -> Tuple[int, int, int, int]:
    """tier 字符串 → 显示色。"""
    return {
        "god": TIER_GOD,
        "good": TIER_GOOD,
        "normal": TIER_NORMAL,
        "bad": TIER_BAD,
    }.get(tier, TIER_NORMAL)


def sonata_panel(draw: ImageDraw.ImageDraw, bbox, sonata_rgba,
                 highlight: bool = False) -> None:
    """方案D 专用毛玻璃面板: 在 holo_panel 基础上把顶部高光线和左侧色条染成套装色。
    bbox = (x0, y0, x1, y1) 局部坐标。"""
    x0, y0, x1, y1 = bbox
    fill = PANEL_FILL_HI if highlight else PANEL_FILL

    # 毛玻璃底
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=RADIUS, fill=fill)
    except AttributeError:
        draw.rectangle((x0, y0, x1, y1), fill=fill)

    # 顶部亮带渐隐(毛玻璃顶部光照感)
    glow_h = 14
    for i in range(glow_h):
        a = int(28 * (1 - i / glow_h))
        draw.line([(x0 + RADIUS, y0 + 1 + i), (x1 - RADIUS, y0 + 1 + i)],
                  fill=(255, 255, 255, a))

    # 顶边发光线 (套装色, 2px)
    draw.line([(x0 + RADIUS, y0 + 1), (x1 - RADIUS, y0 + 1)],
              fill=sonata_rgba, width=2)

    # 左侧套装色条 (从顶到底, 渐隐的渐变)
    bar_w = 6
    bar_x = x0 + 2
    bar_top = y0 + RADIUS - 2
    bar_bot = y1 - RADIUS + 2
    bar_h = max(1, bar_bot - bar_top)
    for j in range(bar_h):
        t = j / bar_h
        # 上端饱和 → 下端略淡 (透明度从 220 → 120)
        a = int(220 - 100 * t)
        c = (sonata_rgba[0], sonata_rgba[1], sonata_rgba[2], a)
        draw.line([(bar_x, bar_top + j), (bar_x + bar_w - 1, bar_top + j)],
                  fill=c)

    # 极细玻璃折射边
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=RADIUS,
                               outline=(200, 220, 255, 35), width=1)
    except (AttributeError, TypeError):
        draw.rectangle((x0, y0, x1, y1), outline=(200, 220, 255, 35), width=1)

    # 底部 1px 弱反光 (套装色)
    bottom_glow = (sonata_rgba[0], sonata_rgba[1], sonata_rgba[2], 50)
    draw.line([(x0 + RADIUS, y1 - 1), (x1 - RADIUS, y1 - 1)],
              fill=bottom_glow, width=1)

    # 角卡扣折线: 用套装色 + 较细
    corner_brackets(draw, (x0, y0, x1, y1), length=9,
                    color=sonata_rgba, width=1)


def sonata_pill(draw: ImageDraw.ImageDraw, xy, text_str: str,
                sonata_rgba, anchor: str = "rt") -> None:
    """套装名小药丸. xy 为锚点位置, anchor 通常 'rt' (右上)。"""
    # 测宽
    f = font("misans", 13)
    try:
        text_w = int(f.getlength(text_str))
    except Exception:
        text_w = len(text_str) * 13
    pad_x = 8
    pad_y = 3
    w = text_w + pad_x * 2
    h = 18

    x, y = xy
    if anchor == "rt":
        x0 = x - w
        y0 = y
    elif anchor == "lt":
        x0 = x
        y0 = y
    else:
        x0 = x - w // 2
        y0 = y - h // 2

    x1 = x0 + w
    y1 = y0 + h

    # 半透明套装色底
    bg_rgba = (sonata_rgba[0], sonata_rgba[1], sonata_rgba[2], 55)
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=9, fill=bg_rgba)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=9,
                               outline=sonata_rgba, width=1)
    except (AttributeError, TypeError):
        draw.rectangle((x0, y0, x1, y1), fill=bg_rgba, outline=sonata_rgba)

    # 文字
    draw.text((x0 + pad_x, y0 + h // 2), text_str,
              font=f, fill=sonata_rgba, anchor="lm")


def score_bar(draw: ImageDraw.ImageDraw, bbox, value: float, vmax: float,
              fill_rgba) -> None:
    """评分进度条. bbox = (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = bbox
    # 槽底
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=2,
                               fill=(255, 255, 255, 25))
    except (AttributeError, TypeError):
        draw.rectangle((x0, y0, x1, y1), fill=(255, 255, 255, 25))
    # 填充
    t = max(0.0, min(1.0, (value or 0.0) / max(0.001, vmax)))
    fw = int((x1 - x0) * t)
    if fw > 0:
        try:
            draw.rounded_rectangle((x0, y0, x0 + fw, y1), radius=2,
                                   fill=fill_rgba)
        except (AttributeError, TypeError):
            draw.rectangle((x0, y0, x0 + fw, y1), fill=fill_rgba)


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


# ──────────────────────────────────────────────────────────
# 着重词条 hook (后期加重用)
# ──────────────────────────────────────────────────────────
def emphasis_for(prop_name: Optional[str]) -> Optional[Tuple[int, int, int, int]]:
    """词条名 → 着重高亮色; 命中返回 RGBA, 未命中或 EMPHASIS_ON=False 返回 None。

    用法 (right_echo_card 副词条循环):
        hl = th.emphasis_for(prop.name)
        val_color = hl if hl is not None else tier_c

    扩展时只改 EMPHASIS_MAP / EMPHASIS_ON 即可, 不需要动业务代码。
    """
    if not EMPHASIS_ON or not prop_name:
        return None
    name = str(prop_name)
    for keyword, color in EMPHASIS_MAP:
        if keyword in name:
            return color
    return None



# ──────────────────────────────────────────────────────────
# 方案D - cost pip 阵 + grade chip (echo_card / mid_echo_summary 用)
# ──────────────────────────────────────────────────────────
def cost_pips(draw: ImageDraw.ImageDraw, x: int, y: int, cost: Optional[int],
              accent: Optional[Tuple[int, int, int, int]] = None,
              max_cost: int = 4) -> int:
    """Cost 菱形 pip 阵: cost 个发光菱形 + 暗色占位补到 max_cost。
    返回最右端 x。 (x, y) 为左上锚点。"""
    if cost is None or cost < 0:
        cost = 0
    pip_w = 9
    gap = 4
    color = accent or (180, 200, 230, 255)
    for i in range(max_cost):
        cx = x + i * (pip_w + gap) + pip_w // 2
        diamond = [
            (cx, y),
            (cx + pip_w // 2, y + pip_w // 2),
            (cx, y + pip_w),
            (cx - pip_w // 2, y + pip_w // 2),
        ]
        if i < cost:
            draw.polygon(diamond, fill=color)
            draw.point((cx, y + pip_w // 2), fill=(255, 255, 255, 255))
        else:
            draw.polygon(diamond, outline=(120, 130, 160, 140))
    return x + max_cost * (pip_w + gap)


def grade_chip(draw: ImageDraw.ImageDraw, x: int, y: int,
               grade: Optional[str], anchor: str = "rm") -> None:
    """评级胶囊: 圆角小标签, 文字反白底主题色 (用 GRADE_COLORS)。"""
    if not grade:
        return
    g = str(grade).upper()
    bg = grade_color(g)
    fnt = font("tektur", 18)
    try:
        tw = int(fnt.getlength(g))
    except Exception:
        tw = len(g) * 10
    pad_x = 9
    w = tw + pad_x * 2
    h = 22
    if anchor == "rm":
        x0 = x - w
        y0 = y - h // 2
    elif anchor == "lm":
        x0 = x
        y0 = y - h // 2
    else:  # mm
        x0 = x - w // 2
        y0 = y - h // 2
    x1 = x0 + w
    y1 = y0 + h
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=11, fill=bg)
    except AttributeError:
        draw.rectangle((x0, y0, x1, y1), fill=bg)
    # 文字 — 深色, 与亮底色形成反差
    draw.text((x0 + w // 2, y0 + h // 2 - 1), g, font=fnt,
              fill=(20, 24, 36, 255), anchor="mm")


# ──────────────────────────────────────────────────────────
# 方案D - cost pip + 评级 chip (right_echo_card / mid_echo_summary 用)
# ──────────────────────────────────────────────────────────
def cost_pips(draw: ImageDraw.ImageDraw, x: int, y: int, cost: Optional[int],
              accent=None, max_cost: int = 4) -> int:
    """绘制 cost 菱形 pip 阵: 当前 cost 实心 + 套装色, 剩余位置空心暗色描边。
    返回最右端 x。 (x, y) 为左上锚点。"""
    if cost is None or cost <= 0:
        cost = 0
    pip_w = 9
    gap = 4
    color = accent or (180, 200, 230, 255)
    for i in range(max_cost):
        cx = x + i * (pip_w + gap) + pip_w // 2
        diamond = [(cx, y), (cx + pip_w // 2, y + pip_w // 2),
                   (cx, y + pip_w), (cx - pip_w // 2, y + pip_w // 2)]
        if i < cost:
            draw.polygon(diamond, fill=color)
            draw.point((cx, y + pip_w // 2), fill=(255, 255, 255, 255))
        else:
            draw.polygon(diamond, outline=(120, 130, 160, 140))
    return x + max_cost * (pip_w + gap)


def grade_chip(draw: ImageDraw.ImageDraw, x: int, y: int, grade: Optional[str],
               anchor: str = "rm") -> None:
    """评级胶囊: 圆角小标签, grade 文字反白底主题色。"""
    if not grade:
        return
    g = grade.upper()
    bg = grade_color(g)
    fnt = font("tektur", 18)
    try:
        tw = int(fnt.getlength(g))
    except Exception:
        tw = len(g) * 10
    pad_x = 9
    w = tw + pad_x * 2
    h = 22
    if anchor == "rm":
        x0 = x - w
        y0 = y - h // 2
    elif anchor == "lm":
        x0 = x
        y0 = y - h // 2
    else:
        x0 = x - w // 2
        y0 = y - h // 2
    x1 = x0 + w
    y1 = y0 + h
    try:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=11, fill=bg)
    except AttributeError:
        draw.rectangle((x0, y0, x1, y1), fill=bg)
    draw.text((x0 + w // 2, y0 + h // 2 - 1), g, font=fnt,
              fill=(20, 24, 36, 255), anchor="mm")
