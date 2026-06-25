# -*- coding: utf-8 -*-
"""预览渲染器: 用假数据跑通整条渲染链,输出 preview.png。
独立可跑: python preview.py
"""
from __future__ import annotations
import schema
from render_card import render_card


def make_fake_data() -> schema.CardData:
    d = schema.CardData()
    d.top_bar = schema.TopBarData(player_name="测试漂泊者", uid="101252736", union_level=80, world_level=8)
    d.illustration = schema.IllustrationData(pile_image=None, element_cn="热熔")
    d.chains = schema.ChainsData(unlocked=[True, True, True, False, False, False])
    d.nameplate = schema.NameplateData(char_name="爱弥斯", char_level=90, total_score=225.0, total_grade="sss")
    d.attributes = schema.AttributesData(props=[
        schema.Prop("生命", "18523"), schema.Prop("攻击", "2680"),
        schema.Prop("防御", "1245"), schema.Prop("共鸣效率", "100.0%"),
        schema.Prop("暴击", "72.3%"), schema.Prop("暴击伤害", "258.6%"),
        schema.Prop("热熔伤害加成", "38.0%"), schema.Prop("治疗效果加成", "0.0%"),
        schema.Prop("普攻伤害加成", "12.4%"), schema.Prop("共鸣解放伤害加成", "29.3%"),
    ])
    d.weapon = schema.WeaponData(name="千古洑流", level=90, refine=5,
                                 main_stat=schema.Prop("攻击力", "588"),
                                 sub_stat=schema.Prop("暴击伤害", "72.0%"))
    d.skills = schema.SkillsData(skills=[
        schema.SkillData("常态攻击", 10), schema.SkillData("共鸣技能", 10),
        schema.SkillData("共鸣回路", 1), schema.SkillData("共鸣解放", 10),
        schema.SkillData("变奏技能", 10),
    ])
    # 5 张声骸(主词条+副词条,好词条高亮色由组装器/真实环境算;这里给None=默认)
    import theme
    _hl = theme.ACCENT_SILVER  # 演示: 假装某些是好词条
    for i in range(5):
        d.echoes.append(schema.EchoCardData(
            name=["荣耀狮像", "巨布偶", "风鬃狼", "浮灵偶·莱特", "火鬃狼"][i],
            level=[10, 15, 15, 15, 15][i], score=[0.0, 2.17, 8.82, 0.48, 0.48][i],
            grade="a", cost=[4, 4, 3, 3, 1][i],
            main_prop=schema.Prop("攻击%", "33.0%") if i < 2 else schema.Prop("攻击", "150"),
            sub_props=[schema.Prop("暴击", "10.5%"), schema.Prop("暴击伤害", "21.0%"),
                       schema.Prop("攻击%", "11.6%"), schema.Prop("生命%", "8.2%"),
                       schema.Prop("共鸣效率", "6.4%")],
            main_color=None, sub_colors=[_hl, _hl, _hl, None, None],
        ))
    d.summary = schema.SummaryData(total_score=225.0, total_grade="sss", crit_rate=72.3, crit_dmg=258.6)
    return d


if __name__ == "__main__":
    print("[preview] rendering EchoMatrix card...")
    img = render_card(make_fake_data())
    out = "preview.png"
    img.convert("RGB").save(out)
    print(f"[preview] DONE: {out}  size={img.size}")
