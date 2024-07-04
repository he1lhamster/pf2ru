from enum import Enum
from typing import List, Union, Optional, Any

from pydantic import BaseModel


class ItemRead(BaseModel):
    id: int
    name: str
    type_level: str
    traits_output: str
    text_output: str
    actions: str | None = None
    url: str
    status: int

#
# class BaseItem:
#     views: int
#     additional_side_info: Optional[str] = None
#
# class Ability(BaseModel):
#     name: str
#     short: str
#
# class Proficiency(BaseModel):
#     name: str
#     bonus: int
#
# class Alignment(Enum):
#     LG = 'Lawful Good'
#     NG = 'Neutral Good'
#     CG = 'Chaotic Good'
#     LN = 'Lawful Neutral'
#     N = 'Neutral'
#     CN = 'Chaotic Neutral'
#     LE = 'Lawful Evil'
#     NE = 'Neutral Evil'
#     CE = 'Chaotic Evil'
#
# class Trait(BaseModel):
#     name: str
#     value: Optional[str] = None
#
# class Language(BaseModel):
#     name: str
#
# class Size(BaseModel):
#     name: str
#
# class Action(BaseModel):
#     name: str
#     actions: int
#     icon: str
#
# class Skill(BaseModel):
#     name: str
#     actions_untrained: List[Action]
#     actions_trained: List[Action]
#
# class Source(BaseModel):
#     id: int
#     name: str
#
# class AttackProficiency(BaseModel):
#     unarmed: Proficiency
#     simple: Proficiency
#     martial: Proficiency
#     advanced: Proficiency
#     other: str
#
# class DefenseProficiency(BaseModel):
#     unarmored: Proficiency
#     light: Proficiency
#     medium: Proficiency
#     heavy: Proficiency
#     other: str
#
# class SavingThrowProficiency(BaseModel):
#     fortitude: Proficiency
#     reflex: Proficiency
#     will: Proficiency
#
# class SkillProficiency(BaseModel):
#     additional: int
#     skills: List[Skill]
#
# class Special(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     action: List[Action]
#     effect: str
#     trigger: str
#     frequency: str
#     requirements: str
#     description: str
#     source: Source
#     type: str
#     level: str
#     gained_from: Union[str]
#
# class ItemHeader(BaseItem):
#     name: str
#     description: str
#
# class Feat(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     actions: Optional[Action] = None
#     category: str
#     level: int
#     grant_specials: Optional[List[Any]]
#     prerequisites: List[Any]
#     requirements: str
#     additional_headers: List[str]
#     description: str
#
# class AncestryFeature(BaseModel):
#     id: int
#     name: str
#     description: str
#     traits: List[Trait]
#     source: Source
#     prerequisites: str
#     specials: Optional[List[Special]]
#     grant_specials: Optional[List[Any]] = None
#
# class Ancestry(BaseModel):
#     id: int
#     name: str
#     img: str = None
#     traits: List[Trait]
#     description: str
#     boosts: List[List[Ability]]
#     flaws: List[List[Ability]]
#     hp: int
#     languages: List[Language]
#     additional_languages: List[Language]
#     reach: int = 5
#     size: Size
#     source: Source
#     speed: int
#     vision: str
#     features: List[AncestryFeature]
#
# class Heritage(BaseModel):
#     id: int
#     name: str
#     img: str
#     ancestry: Ancestry
#     traits: List[Trait]
#     description: str
#     source: Source
#     is_versatile: bool
#
# class Archetype(BaseModel):
#     id: int
#     name: str
#     img: str
#     traits: List[Trait]
#     source: List[Source]
#     description: str
#     dedication_level: int
#     feats: List[Feat]
#
# class ClassFeature(BaseModel):
#     id: int
#     name: str
#     description: str
#     traits: List[Trait]
#     source: Source
#     level: List[int]
#     specials: Optional[List[Special]]
#     grant_specials: Optional[List[Any]]
#
# class ClassPC(BaseModel):
#     id: int
#     name: str
#     img: str
#     traits: List[Trait]
#     source: Source
#     key_ability: Ability
#     hp: int
#     perception: Proficiency
#     classDC: Proficiency
#     attacks: AttackProficiency
#     defenses: DefenseProficiency
#     saving_throws: SavingThrowProficiency
#     trained_skills: SkillProficiency
#     additional_skills: int
#     ancestry_feat_level: List[int]
#     class_feat_level: List[int]
#     general_feat_level: List[int]
#     skill_feat_level: List[int]
#     skill_increase_level: List[int]
#     features: List[ClassFeature]
#
# class Condition(BaseModel):
#     id: int
#     name: str
#     source: Source
#     description: str
#
# class Background(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     boosts: List[List[Ability]]
#     flaws: List[List[Ability]]
#     description: str
#     feat: Feat
#     trained_skills: Optional[List[Skill]]
#     grant_specials: List[Any]
#
# class ActionActivity (BaseModel):
#     id: int
#     name: int
#     traits: List[Trait]
#     source: Source
#     actions: Optional[Action | str]
#     headers: Optional[List[str]]
#     description: str
#
# class SpellComponent:
#     somatic: bool
#     verbal: bool
#     material: bool
#
# class MagicTradition(Enum):
#     arcana = "Arcana"
#     occult = "Occult"
#     divine = "Divine"
#     primal = "Primal"
#
# class Spell(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     level: int
#     components: SpellComponent
#     materials: str
#     cost: str
#     duration: str
#     area: str
#     target: str
#     range: str
#     traditions: List[MagicTradition]
#     additional_headers: List[str]
#     heightening: List[str]
#     description: str
#     actions: Union[List[Action] | str]
#
# class Ritual(Spell):
#     primary_check: str
#     secondary_casters: int
#     secondary_checks: str
#
# class Material:
#     type: str
#     grade: str
#
# class Weapon(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     base_item: str
#     category: str
#     equipped_bulk: str
#     damage_type: str
#     damage: str
#     group: str
#     hardness: int
#     hp: int
#     level: int
#     price: str
#     range: str
#     reload: str
#     usage: str
#     bulk: str
#     material: Material
#     description: str
#
# class Armor(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     base_items: str
#     category: str
#     ac_bonus: int
#     check_penalty: int
#     dex_cap: int
#     equipped_bulk: str
#     group: str
#     hardness: int
#     hp: int
#     level: int
#     material: Material
#     price: str
#     strength: int
#     usage: str
#     bulk: str
#     description: str
#
# class Shield(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     base_items: str
#     category: str
#     ac_bonus: int
#     check_penalty: int
#     dex_cap: int
#     equipped_bulk: str
#     group: str
#     hardness: int
#     hp: int
#     level: int
#     material: Material
#     price: str
#     strength: int
#     usage: str
#     bulk: str
#     description: str
#
# class ClassKit(BaseModel):
#     id: int
#     name: str
#     price: str
#     price_leftover: str
#     bulk: str
#     weapons: List[Weapon]
#     armors: List[Armor]
#     gear: List[Any]
#     options: str
#
# class Consumable(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     img: str
#     base_item: str
#     consumable_type: str
#     container_id: int
#     hardness: int
#     hp: int
#     level: int
#     price: str
#     usage: str
#     description: str
#
# class Equipment(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     container_id: int
#     base_item: str
#     hardness: int
#     hp: int
#     level: int
#     material: Material
#     price: str
#     usage: str
#     bulk: str
#     damage: str
#     damage_type: str
#     range: str
#     reload: str
#     additional_headers: str
#
# class ClassSpecialization(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     actions: Action
#     type: str # tenet, order, muse etc
#     related_class: ClassPC.name
#     description: str
#     features: List[Special]
#     grant_specials: List[Any]
# #
# # class Domain(BaseModel):
# #     id: int
# #     name: str
# #     traits: List[Trait]
# #     source: Source
# #     deities: List[Deity]
# #     domain_spell: Spell
# #     advanced_domain_spell: Spell
# #     description: str
# #     apocryphal_domain_spell: Spell
# #     advanced_apocryphal_domain_spell: Spell
# #
# # class Deity(BaseModel):
# #     id: int
# #     name: str
# #     img: str
# #     traits: List[Trait]
# #     source: Source
# #     alignment: Alignment
# #     followers_alignment: List[Alignment]
# #     category: str
# #     ability: List[Ability]
# #     domains: List[Domain]
# #     alternate_domains: List[Domain]
# #     skill: Skill
# #     font: str
# #     favored_weapons: List[Weapon]
# #     spells: List[Spell]
#
# class FamiliarAbility(BaseModel):
#     id: int
#     name: str
#     traits: List[Trait]
#     source: Source
#     description: str
#
# class Hazard(BaseModel):
#     pass
#
#
# class Compendium(BaseModel):
#     ancestries: List[Ancestry]
#     classes: List[ClassPC]
#     Feats: List[Feat]
