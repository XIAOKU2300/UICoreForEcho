# -*- coding: utf-8 -*-
"""区块契约规范(所有 block 必须遵守)。

═══════════════════════════════════════════════════════════
每个区块 = blocks/ 下一个独立 .py 文件 = 一个渲染函数。
函数统一签名:

    def render(data, theme) -> (layer, height)

- 参数 data: 该区块对应的数据切片(见 schema.py 的某个 *Data 类)
- 参数 theme: 全局主题模块(import theme),用它的工厂方法绘制
- 返回 layer: PIL.Image (RGBA 透明局部图层),宽度=所在轨道宽度
- 返回 height: int,该图层的实际内容高度(组装器据此堆叠)

铁律:
1. 只用局部坐标 (0,0) 起绘,不要管自己在主画布的哪个位置。
2. 图层宽度 = 轨道宽度(theme.LEFT/MID/RIGHT_TRACK[1])。
3. 只读 data 切片里的字段,不假设其他数据。
4. 只调 theme 的工厂方法画底板/文字/点阵,不自己定义颜色字体。
5. 不修改 theme.py / schema.py (它们已冻结)。
6. 数值右对齐用 theme.text(..., anchor="rm") 或 theme.text_w 测宽计算。

示例骨架:
    import theme
    def render(data, th):
        W = th.MID_TRACK[1]
        layer, draw = th.new_layer(W, 200)
        th.holo_panel(draw, (0, 0, W, 200))
        th.title(draw, 16, 28, "标题")
        ... 画内容 ...
        return layer, 200
═══════════════════════════════════════════════════════════
"""
