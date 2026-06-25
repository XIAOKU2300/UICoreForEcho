# -*- coding: utf-8 -*-
"""EchoMatrix v2 角色面板适配层。

把插件真实数据(account_info / role_detail)转成 echomatrix_ui.schema.CardData,
再调 render_card 出图。接到 bot 的 draw_char_detail_img_v2 入口。

复用老函数的数据获取(base_info_cache / get_role_need / calc_phantom_score / get_valid_color)。
"""
from __future__ import annotations
from typing import Optional

from . import schema
from . import render_card


def _prop(name, value):
    return schema.Prop(str(name or ""), str(value if value is not None else ""))


def _safe(obj, *path, default=None):
    """安全取链式属性。"""
    cur = obj
    for p in path:
        if cur is None:
            return default
        cur = getattr(cur, p, None)
    return cur if cur is not None else default


def build_card_data(account_info, role_detail, avatar_img=None, calc_temp=None,
                    total_score=None, total_grade=None, get_valid_color=None):
    """把真实数据组装成 CardData。

    参数:
      account_info: AccountBaseInfo(有 name/id/level/worldLevel)
      role_detail:  RoleDetailData(有 role/phantomData/weaponData/skillList/chainList)
      avatar_img:   头像 PIL.Image 或 None
      calc_temp:    评分模板(给 get_valid_color 用)
      total_score/total_grade: 综合评分
      get_valid_color: 函数(name,value,calc_temp)->(name_color,value_color),用于好词条高亮
    """
    d = schema.CardData()
    role = getattr(role_detail, "role", None)

    # ── 顶栏 ──
    d.top_bar = schema.TopBarData(
        player_name=str(getattr(account_info, "name", None) or "---"),
        uid=str(getattr(account_info, "id", None) or "--------"),
        union_level=getattr(account_info, "level", None),
        world_level=getattr(account_info, "worldLevel", None),
    )

    char_name = str(getattr(role, "roleName", None) or "---")

    # ── 左轨立绘 ──
    d.illustration = schema.IllustrationData(
        pile_image=None,  # 立绘图由 render 时另传,这里占位(适配层不持有大图)
        element_cn=getattr(role, "attributeName", None),
        char_name=char_name,
    )

    # ── 命座 ──
    chain_list = getattr(role_detail, "chainList", None) or []
    unlocked = []
    for i in range(6):
        if i < len(chain_list):
            unlocked.append(bool(getattr(chain_list[i], "unlocked", False)))
        else:
            unlocked.append(False)
    d.chains = schema.ChainsData(unlocked=unlocked)

    # ── 名牌 ──
    d.nameplate = schema.NameplateData(
        char_name=char_name,
        char_level=getattr(role, "level", None),
        total_score=total_score,
        total_grade=total_grade,
    )

    # ── 中轨属性(从 equipPhantomAddPropList 取面板总属性) ──
    attr_props = []
    add_list = getattr(role_detail, "equipPhantomAddPropList", None) or []
    for p in add_list:
        nm = getattr(p, "attributeName", None)
        vl = getattr(p, "attributeValue", None)
        if nm:
            attr_props.append(_prop(nm, vl))
    d.attributes = schema.AttributesData(props=attr_props)

    # ── 武器 ──
    wd = getattr(role_detail, "weaponData", None)
    wpn = getattr(wd, "weapon", None)
    d.weapon = schema.WeaponData(
        name=str(getattr(wpn, "weaponName", None) or "---"),
        level=getattr(wd, "level", None),
        refine=getattr(wd, "resonLevel", None),
        icon_image=None,
        main_stat=None,
        sub_stat=None,
    )

    # ── 技能 ──
    skills = []
    for sk in (getattr(role_detail, "skillList", None) or []):
        sk_obj = getattr(sk, "skill", None)
        skills.append(schema.SkillData(
            type_name=str(getattr(sk_obj, "type", None) or getattr(sk_obj, "name", None) or ""),
            level=getattr(sk, "level", None),
            icon_image=None,
        ))
    d.skills = schema.SkillsData(skills=skills)

    # 声骸 + 汇总 在第二部分填充
    _fill_echoes(d, role_detail, calc_temp, total_score, total_grade, get_valid_color)
    return d


def _to_num(value):
    """'72.3%' -> 72.3,失败 None。"""
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except Exception:
        return None


def _fill_echoes(d, role_detail, calc_temp, total_score, total_grade, get_valid_color):
    """填充 5 张声骸卡(主副词条 + 好词条高亮色) + 运算终端汇总。"""
    pd = getattr(role_detail, "phantomData", None)
    equip_list = getattr(pd, "equipPhantomList", None) or []
    role_id = _safe(role_detail, "role", "roleId")

    # 延迟 import 评分函数(避免循环依赖,失败则不算分)
    calc_phantom_score = None
    try:
        from ..calculate import calc_phantom_score as _cps
        calc_phantom_score = _cps
    except Exception:
        calc_phantom_score = None

    echoes = []
    for ph in equip_list:
        if ph is None or getattr(ph, "phantomProp", None) is None:
            echoes.append(schema.EchoCardData())  # 空卡 -> "未装备"
            continue
        prop_obj = ph.phantomProp
        try:
            props = ph.get_props()
        except Exception:
            props = []

        score = None
        grade = None
        if calc_phantom_score and role_id is not None:
            try:
                score, grade = calc_phantom_score(role_id, props, ph.cost, calc_temp)
            except Exception:
                score = grade = None

        # 前2个主词条,其余副词条
        main_prop = _prop(props[0].attributeName, props[0].attributeValue) if len(props) >= 1 else None
        sub_list = []
        sub_colors = []
        for idx, p in enumerate(props[1:] if len(props) > 1 else []):
            sub_list.append(_prop(p.attributeName, p.attributeValue))
            col = None
            if get_valid_color:
                try:
                    _, vcol = get_valid_color(p.attributeName, p.attributeValue, calc_temp)
                    # 只有好词条(非默认白)才高亮
                    if vcol and tuple(vcol[:3]) != (255, 255, 255):
                        col = tuple(vcol[:3]) + (255,) if len(vcol) == 3 else tuple(vcol)
                except Exception:
                    col = None
            sub_colors.append(col)

        # 主词条高亮色
        main_color = None
        if get_valid_color and main_prop:
            try:
                _, mvcol = get_valid_color(main_prop.name, main_prop.value, calc_temp)
                if mvcol and tuple(mvcol[:3]) != (255, 255, 255):
                    main_color = tuple(mvcol[:3]) + (255,) if len(mvcol) == 3 else tuple(mvcol)
            except Exception:
                main_color = None

        name = str(getattr(prop_obj, "name", None) or "---").replace("·", " ")
        echoes.append(schema.EchoCardData(
            name=name,
            level=getattr(ph, "level", None),
            score=round(score, 1) if score is not None else None,
            grade=grade,
            cost=getattr(ph, "cost", None),
            icon_image=None,
            main_prop=main_prop,
            sub_props=sub_list[:5],
            main_color=main_color,
            sub_colors=sub_colors[:5],
        ))
    d.echoes = echoes

    # ── 运算终端汇总: 总评分 + 双爆比(从面板属性取暴击/暴击伤害) ──
    crit_rate = crit_dmg = None
    for p in (getattr(role_detail, "equipPhantomAddPropList", None) or []):
        nm = str(getattr(p, "attributeName", None) or "")
        if nm == "暴击伤害":
            crit_dmg = _to_num(getattr(p, "attributeValue", None))
        elif nm == "暴击":
            crit_rate = _to_num(getattr(p, "attributeValue", None))
    d.summary = schema.SummaryData(
        total_score=total_score,
        total_grade=total_grade,
        crit_rate=crit_rate,
        crit_dmg=crit_dmg,
    )
