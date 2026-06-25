# -*- coding: utf-8 -*-
"""总成组装器(流式调度中枢)。

职责:
1. 实例化主画布 + 背景。
2. 把 CardData 拆成切片,分发给各 block。
3. 维护左/中/右三个垂直流,把 block 返回的图层依次向下堆叠。
4. 截断多余高度,输出成品。

block 缺失时优雅跳过(骨架阶段可先跑通)。
"""
from __future__ import annotations
import importlib
from typing import Optional
from PIL import Image, ImageDraw
# 兼容两种使用方式: 包内(插件)用相对导入, 独立运行(UICoreForEcho)用顶层导入
try:
    from . import theme
    from . import schema
    _AS_PKG = True
except ImportError:
    import theme
    import schema
    _AS_PKG = False


# 轨道流式布局: 每条轨道是 (起点x, 宽度, 当前y游标)
class _TrackFlow:
    def __init__(self, x: int, w: int, top: int):
        self.x = x
        self.w = w
        self.y = top

    def place(self, base: Image.Image, layer, height: int):
        if layer is not None:
            theme.paste_layer(base, layer, self.x, self.y)
        self.y += height + theme.GAP


def _try_block(module_name: str, data, th):
    """动态调用 blocks/<module_name>.render(data, theme)。缺失/出错则返回 None。"""
    try:
        if _AS_PKG:
            mod = importlib.import_module(f".blocks.{module_name}", package=__package__)
        else:
            mod = importlib.import_module(f"blocks.{module_name}")
        return mod.render(data, th)
    except ModuleNotFoundError:
        return None
    except Exception as e:
        print(f"[render_card] block '{module_name}' error: {e}")
        return None


def render_card(data: schema.CardData, bg_image: Optional[Image.Image] = None) -> Image.Image:
    # ---- 主画布 + 背景 ----
    W = theme.CARD_W
    H0 = 1500  # 初始高度,末尾按内容截断
    img = Image.new("RGBA", (W, H0), theme.BG_MAIN)

    # 背景图支持: 如果提供了背景图,铺上去再叠一层半透暗色保证可读性
    if bg_image is not None:
        bg = bg_image.convert("RGBA")
        bg_ratio = W / bg.width
        bg_h = int(bg.height * bg_ratio)
        bg = bg.resize((W, bg_h), Image.LANCZOS)
        img.paste(bg, (0, 0))
        # 叠一层半透明暗色(确保文字可读)
        overlay = Image.new("RGBA", (W, H0), (20, 24, 36, 140))
        img.alpha_composite(overlay)
    else:
        theme.bg_gradient(img)

    draw = ImageDraw.Draw(img)

    # ---- 顶栏(全幅,固定在最上) ----
    top = _try_block("top_bar", data.top_bar, theme)
    if top is not None:
        layer, _h = top
        theme.paste_layer(img, layer, 0, 0)

    # ---- 三轨流 ----
    lx, lw = theme.LEFT_TRACK
    mx, mw = theme.MID_TRACK
    rx, rw = theme.RIGHT_TRACK
    # 轻度错落: 三轨起始高度错开,打破死板的齐平网格
    left = _TrackFlow(lx, lw, theme.TRACK_TOP)
    mid = _TrackFlow(mx, mw, theme.TRACK_TOP - 16)   # 中轨略高
    right = _TrackFlow(rx, rw, theme.TRACK_TOP + 20)  # 右轨略低

    # 左轨: 立绘 → 命座 → 名牌评分
    # (立绘/命座是叠在左轨视觉层,名牌在下方;此处按流式简化堆叠)
    for name, slice_data, flow in [
        ("left_illustration", data.illustration, left),
        ("left_chains", data.chains, left),
        ("left_nameplate", data.nameplate, left),
    ]:
        res = _try_block(name, slice_data, theme)
        if res:
            flow.place(img, res[0], res[1])

    # 中轨: 属性 → 武器 → 技能 → 声骸加成汇总(可选)
    for name, slice_data, flow in [
        ("mid_attributes", data.attributes, mid),
        ("mid_weapon", data.weapon, mid),
        ("mid_skills", data.skills, mid),
    ]:
        res = _try_block(name, slice_data, theme)
        if res:
            flow.place(img, res[0], res[1])
    # 中轨可选: 声骸加成汇总(只有 data.echo_summary 不为 None 才绘制)
    if getattr(data, "echo_summary", None) is not None:
        res = _try_block("mid_echo_summary", data.echo_summary, theme)
        if res:
            mid.place(img, res[0], res[1])

    # 右轨: 5张声骸卡 → 运算终端
    for echo in (data.echoes or []):
        res = _try_block("right_echo_card", echo, theme)
        if res:
            right.place(img, res[0], res[1])
    res = _try_block("right_summary", data.summary, theme)
    if res:
        right.place(img, res[0], res[1])

    # ---- 按三轨最大底部截断 ----
    content_bottom = max(left.y, mid.y, right.y) + theme.MARGIN
    content_bottom = max(content_bottom, theme.TRACK_TOP + 200)
    if content_bottom != H0:
        new_img = Image.new("RGBA", (W, content_bottom), theme.BG_MAIN)
        new_img.alpha_composite(img.crop((0, 0, W, min(content_bottom, H0))), dest=(0, 0))
        img = new_img

    return img
