# -*- coding: utf-8 -*-
"""预览渲染器: 注入洛瑟菈真实数据跑通渲染链."""
from __future__ import annotations
import schema
from render_card import render_card
import theme

def make_fake_data() -> schema.CardData:
    d = schema.CardData()
    # 1. 基础信息
    d.top_bar = schema.TopBarData(player_name="UrithanAGR", uid="108591248", union_level=80, world_level=8)
    d.illustration = schema.IllustrationData(pile_image=None, element_cn="冷凝", char_name="洛瑟菈")
    d.chains = schema.ChainsData(unlocked=[True, True, True, True, True, True]) # 假设满命
    d.nameplate = schema.NameplateData(char_name="洛瑟菈", char_level=90, total_score=93.34, total_grade="a")
    
    # 2. 角色面板属性
    d.attributes = schema.AttributesData(props=[
        schema.Prop("生命", "17117"), schema.Prop("攻击", "2396"),
        schema.Prop("防御", "1470"), schema.Prop("共鸣效率", "142.0%"),
        schema.Prop("偏置值累积效率", "0.0%"), schema.Prop("暴击", "64.4%"),
        schema.Prop("暴击伤害", "214.8%"), schema.Prop("冷凝伤害加成", "70.0%"),
        schema.Prop("普攻伤害加成", "25.8%"), schema.Prop("破甲/无视防御", "0")
    ])
    
    # 3. 武器与技能
    d.weapon = schema.WeaponData(name="漪澜浮录", level=90, refine=1,
                                 main_stat=schema.Prop("攻击", "500"),
                                 sub_stat=schema.Prop("攻击百分比", "54.0%"))
    d.skills = schema.SkillsData(skills=[
        schema.SkillData("常态攻击", 10), schema.SkillData("共鸣技能", 10),
        schema.SkillData("共鸣回路", 10), schema.SkillData("共鸣解放", 10),
        schema.SkillData("变奏技能", 6),
    ])
    
    # 4. 声骸总体汇总
    d.echo_summary = schema.EchoSummaryData(
        grade="B", score=147.96, template_name="洛瑟菈-通用",
        base_props=[
            schema.Prop("生命", "4880"), schema.Prop("攻击", "943"),
            schema.Prop("防御", "273"), schema.Prop("共鸣效率", "29.2%"),
            schema.Prop("暴击", "51.4%"), schema.Prop("暴击伤害", "64.8%"),
            schema.Prop("冷凝伤害加成", "70.0%"), schema.Prop("治疗效果加成", "0.0%")
        ],
        dmg_props=[
            schema.Prop("普攻伤害加成", "25.8%"), schema.Prop("重击伤害加成", "11.6%"),
            schema.Prop("共鸣技能伤害", "7.1%"), schema.Prop("共鸣解放伤害", "17.2%")
        ],
        base_colors=[None, None, None, theme.SUCCESS, None, None, None, None],
        dmg_colors=[theme.ACCENT_VIOLET, None, None, None]
    )
    
    # 5. 声骸个体明细
    # 1号
    d.echoes.append(schema.EchoCardData(
        name="格洛羽团", level=25, score=41.69, grade="S", cost=4,
        main_prop=schema.Prop("冷凝伤害加成", "30.0%"),
        sub_props=[schema.Prop("共鸣效率", "7.6%"), schema.Prop("攻击", "8.6%"), schema.Prop("普攻伤害加成", "8.6%"), schema.Prop("暴击伤害", "21.0%"), schema.Prop("暴击", "8.7%")],
        sub_colors=[theme.SUCCESS, None, theme.ACCENT_VIOLET, theme.ERROR, None]
    ))
    # 2号
    d.echoes.append(schema.EchoCardData(
        name="虚造神型", level=25, score=22.07, grade="B", cost=4,
        main_prop=schema.Prop("暴击", "22.0%"),
        sub_props=[schema.Prop("攻击", "40"), schema.Prop("共鸣技能伤害", "7.1%"), schema.Prop("暴击伤害", "15.0%"), schema.Prop("共鸣效率", "10.8%"), schema.Prop("共鸣解放伤害", "10.1%")],
        sub_colors=[None, None, None, theme.SUCCESS, None]
    ))
    # 3号
    d.echoes.append(schema.EchoCardData(
        name="重工铁骑", level=25, score=31.16, grade="A", cost=3,
        main_prop=schema.Prop("冷凝伤害加成", "30.0%"),
        sub_props=[schema.Prop("防御", "10.9%"), schema.Prop("暴击伤害", "13.8%"), schema.Prop("普攻伤害加成", "8.6%"), schema.Prop("暴击", "8.1%"), schema.Prop("共鸣效率", "10.8%")],
        sub_colors=[None, None, theme.ACCENT_VIOLET, None, theme.SUCCESS]
    ))
    # 4号
    d.echoes.append(schema.EchoCardData(
        name="影烁者", level=25, score=23.44, grade="B", cost=1,
        main_prop=schema.Prop("攻击", "18.0%"),
        sub_props=[schema.Prop("普攻伤害加成", "8.6%"), schema.Prop("暴击", "6.3%"), schema.Prop("攻击", "8.6%"), schema.Prop("共鸣解放伤害", "7.1%"), schema.Prop("重击伤害加成", "11.6%")],
        sub_colors=[theme.ACCENT_VIOLET, None, None, None, None]
    ))
    # 5号
    d.echoes.append(schema.EchoCardData(
        name="颤栗战士", level=25, score=29.6, grade="A", cost=1,
        main_prop=schema.Prop("攻击", "18.0%"),
        sub_props=[schema.Prop("攻击", "10.1%"), schema.Prop("防御", "11.9%"), schema.Prop("暴击伤害", "15.0%"), schema.Prop("暴击", "6.3%"), schema.Prop("生命", "320")],
        sub_colors=[None, None, None, None, None]
    ))
    
    # 6. 运算终端底部数据
    d.summary = schema.SummaryData(
        total_score=93.34, total_grade="A", crit_rate=64.4, crit_dmg=214.8,
        damage_type="本期深塔伤害", crit_damage_expect="21,726",
        avg_damage_expect="17,592", score_rank="103", damage_rank="67"
    )
    return d

if __name__ == "__main__":
    print("[preview] rendering EchoMatrix card...")
    try:
        from PIL import Image
        bg = Image.open("mqt8dys1-image.png") # 尝试使用用户提供的背景图作为立绘背景测试
    except Exception:
        bg = None
    
    img = render_card(make_fake_data(), bg_image=bg)
    out = "preview_luosela.png"
    img.convert("RGB").save(out)
    print(f"[preview] DONE: {out}  size={img.size}")
