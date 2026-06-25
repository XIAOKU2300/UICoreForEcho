# -*- coding: utf-8 -*-
"""数据契约(冻结·只读)。

所有区块只能读取分配给自己的"数据切片",不得假设这里没有的字段。
组装器负责把完整数据拆成切片投喂给各 block。

设计原则(来自架构方案):最小知识 / 按需投喂 / 不可变基石。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ──────────────────────────────────────────────────────────
# 基础值对象
# ──────────────────────────────────────────────────────────
@dataclass
class Prop:
    """一条词条: 名称 + 显示值字符串(可能带%)。"""
    name: str
    value: str


# ──────────────────────────────────────────────────────────
# 各区块的数据切片(每个 block 只收到自己这片)
# ──────────────────────────────────────────────────────────
@dataclass
class TopBarData:
    """顶栏: 身份识别。"""
    player_name: str = "---"
    uid: str = "--------"
    union_level: Optional[int] = None      # 联觉等级
    world_level: Optional[int] = None      # 索拉等阶


@dataclass
class IllustrationData:
    """左轨立绘。pile_image 为 PIL.Image 或 None(占位)。"""
    pile_image: object = None
    element_cn: Optional[str] = None       # 元素中文名(用于色调)
    char_name: str = ""                    # 角色名(背景水印大字用)


@dataclass
class ChainsData:
    """共鸣链(命座): 6 个节点的解锁状态。"""
    unlocked: List[bool] = field(default_factory=lambda: [False] * 6)


@dataclass
class NameplateData:
    """左轨名牌 + 综合评分。"""
    char_name: str = "---"
    char_level: Optional[int] = None
    total_score: Optional[float] = None
    total_grade: Optional[str] = None      # C/B/A/S/SS/SSS


@dataclass
class AttributesData:
    """中轨基础属性面板: 约 10 项 (名称, 值)。"""
    props: List[Prop] = field(default_factory=list)


@dataclass
class WeaponData:
    """中轨武器。"""
    name: str = "---"
    level: Optional[int] = None
    refine: Optional[int] = None           # 精炼阶 (R/精)
    icon_image: object = None
    main_stat: Optional[Prop] = None       # 攻击力
    sub_stat: Optional[Prop] = None        # 副属性


@dataclass
class SkillData:
    """单个技能。"""
    type_name: str = ""                    # 常态攻击/共鸣技能/...
    level: Optional[int] = None
    icon_image: object = None


@dataclass
class SkillsData:
    """中轨技能阵列。"""
    skills: List[SkillData] = field(default_factory=list)


@dataclass
class EchoCardData:
    """右轨单张声骸卡。"""
    name: str = "---"
    level: Optional[int] = None
    score: Optional[float] = None
    grade: Optional[str] = None
    cost: Optional[int] = None
    icon_image: object = None
    main_prop: Optional[Prop] = None
    sub_props: List[Prop] = field(default_factory=list)
    # 好词条高亮: 与 main/sub 同序的颜色标记(由组装器算好, block 只用)
    # 每项是 RGBA 元组或 None(None=默认色)
    main_color: Optional[Tuple[int, int, int, int]] = None
    sub_colors: List[Optional[Tuple[int, int, int, int]]] = field(default_factory=list)
    # 方案D 新增: 套装名(用于卡片色条/pill高亮)
    # TODO[后端对接]: 后端在 phantomProp 上提供 sonataName / setName 字段后填充
    sonata: Optional[str] = None


@dataclass
class SummaryData:
    """右轨终极运算终端: 评分 + 双爆比(准确系数, 不含虚假伤害绝对值)。"""
    total_score: Optional[float] = None
    total_grade: Optional[str] = None
    crit_rate: Optional[float] = None      # 暴击率% (数值, 如 72.3)
    crit_dmg: Optional[float] = None       # 暴击伤害% (数值, 如 258.6)
    # 可选扩展字段(预留给 right_summary 后续启用,如伤害排名等):
    damage_type: Optional[str] = None
    crit_damage_expect: Optional[str] = None
    avg_damage_expect: Optional[str] = None
    score_rank: Optional[str] = None
    damage_rank: Optional[str] = None


@dataclass
class EchoSummaryData:
    """中轨声骸加成汇总(可选区块,如洛瑟菈需要)。"""
    grade: Optional[str] = None
    score: Optional[float] = None
    template_name: str = ""
    base_props: List[Prop] = field(default_factory=list)
    dmg_props: List[Prop] = field(default_factory=list)
    base_colors: List[Optional[Tuple[int, int, int, int]]] = field(default_factory=list)
    dmg_colors: List[Optional[Tuple[int, int, int, int]]] = field(default_factory=list)


@dataclass
class CardData:
    """完整卡片数据(组装器持有, 拆片投喂各 block)。"""
    top_bar: TopBarData = field(default_factory=TopBarData)
    illustration: IllustrationData = field(default_factory=IllustrationData)
    chains: ChainsData = field(default_factory=ChainsData)
    nameplate: NameplateData = field(default_factory=NameplateData)
    attributes: AttributesData = field(default_factory=AttributesData)
    weapon: WeaponData = field(default_factory=WeaponData)
    skills: SkillsData = field(default_factory=SkillsData)
    echoes: List[EchoCardData] = field(default_factory=list)   # 最多5
    summary: SummaryData = field(default_factory=SummaryData)
    echo_summary: Optional["EchoSummaryData"] = None           # 可选: 中轨声骸加成汇总
