import enum
from typing import Optional
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Text, Index, ForeignKey, Column, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from database import Base


class Proficiency(enum.Enum):
    T = 'Trained'
    E = 'Expert'
    M = 'Master'
    L = 'Legendary'


class Rarity(enum.Enum):
    Common = 'Common'
    Uncommon = 'Uncommon'
    Rare = 'Rare'
    Unique = 'Unique'


class Tradition(enum.Enum):
    arcane = 'Arcane'
    divine = 'Divine'
    occult = 'Occult'
    primal = 'Primal'


# class ItemType(Base):
#     __tablename__ = 'itemtype'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]


class BaseModel:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def generate_index_name(cls):
        return f"ix_{cls.__tablename__}_name"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(index=True)
    rarity: Mapped[str | None]
    type: Mapped[str | None]
    type_level: Mapped[str | None]
    trait: Mapped[str | None]
    traits_output: Mapped[str | None]
    text_output: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None]
    views: Mapped[Optional[int]] = mapped_column(default=0)
    is_legacy: Mapped[bool]
    rus_name: Mapped[str | None]
    rus_type_level: Mapped[str | None]
    rus_traits_output: Mapped[str | None]
    rus_text_output: Mapped[str | None]
    legacy_name: Mapped[str | None]
    remaster_name: Mapped[str | None]

    # item_type_id: Mapped[int] = Column(ForeignKey('itemtype.id'))

    __table_args__ = (

        Index('ix_my_table_text_output_tsv', text("to_tsvector('english', to_plain_text(text_output))"), postgresql_using='gin'),
        Index('ix_my_table_rus_text_output_tsv', text("to_tsvector('russian', to_plain_text(rus_text_output))"), postgresql_using='gin'),

        Index('ix_my_table_traits_output_tsv', text("to_tsvector('english', extract_link_name(traits_output))"), postgresql_using = 'gin'),
        Index('ix_my_table_rus_traits_output_tsv', text("to_tsvector('russian', extract_link_name(rus_traits_output))"),
              postgresql_using='gin'),
    )


class Action(Base, BaseModel):
    __tablename__ = "action"
    requirement: Mapped[str | None]
    frequency: Mapped[str | None]
    trigger: Mapped[str | None]
    element: Mapped[str | None]
    school: Mapped[str | None]
    cost: Mapped[str | None]
    actions: Mapped[str | None]
#     new
    subcategory: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="action")

    __table_args__ = (
        Index('ix_action_name', 'name'),
    )

class GeneralSkillAction(Base, BaseModel):
    __tablename__ = "generalskillaction"
    requirement: Mapped[str | None]
    frequency: Mapped[str | None]
    trigger: Mapped[str | None]
    cost: Mapped[str | None]
    actions: Mapped[str | None]


class Ancestry(Base, BaseModel):
    __tablename__ = "ancestry"
    hp: Mapped[int | None]
    speed: Mapped[str | None]
    ability_flaw: Mapped[str | None]
    language: Mapped[str | None]
    land_speed: Mapped[str | None]
    max_speed: Mapped[str | None]
    ability_boost: Mapped[str | None]
    size: Mapped[str | None]
    vision: Mapped[str | None]
    ability: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="ancestry")

    __table_args__ = (
        Index('ix_ancestry_name', 'name'),
    )


class Heritage(Base, BaseModel):
    __tablename__ = "heritage"
    ancestry_id: Mapped[str | None]
    is_versatile: Mapped[bool] = False

    # item_type: Mapped[int] = relationship(ItemType, backref="heritage")

    __table_args__ = (
        Index('ix_heritage_name', 'name'),
    )


class Class_(Base, BaseModel):
    __tablename__ = "class_"
    hp: Mapped[int]
    ability_boost: Mapped[str | None]
    skill_proficiency: Mapped[str | None]
    perception_proficiency: Mapped[str | None]
    ability: Mapped[str | None]
    attack_proficiency: Mapped[str | None]
    defense_proficiency: Mapped[str | None]
    tradition: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="class_")

    __table_args__ = (
        Index('ix_class__name', 'name'),
    )


class Background(Base, BaseModel):
    __tablename__ = 'background'
    ability_boost: Mapped[str | None]
    skill: Mapped[str | None]
    prerequisite: Mapped[str | None]
    feat: Mapped[str | None]
    ability: Mapped[str | None]
    subcategory: Mapped[str | None]
    adventure: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="background")

    __table_args__ = (
        Index('ix_background_name', 'name'),
    )


class Feat(Base, BaseModel):
    __tablename__ = 'feat'
    actions: Mapped[str | None]
    requirement: Mapped[str | None]
    frequency: Mapped[str | None]
    cost: Mapped[str | None]
    leads_to: Mapped[str | None]
    prerequisite: Mapped[str | None]
    feat: Mapped[str | None]
    trigger: Mapped[str | None]
    school: Mapped[str | None]
    element: Mapped[str | None]
    level: Mapped[str | None]
    heighten_level: Mapped[str | None]
    subcategory: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="feat")

    __table_args__ = (
        Index('ix_feat_name', 'name'),
    )


class Archetype(Base, BaseModel):
    __tablename__ = 'archetype'
    prerequisite: Mapped[str | None]
    level: Mapped[str | None]
    is_multiclass: Mapped[int | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="archetype")

    __table_args__ = (
        Index('ix_archetype_name', 'name'),
    )


class Spell(Base, BaseModel):
    __tablename__ = 'spell'
    mystery: Mapped[str | None]
    area: Mapped[str | None]
    heighten: Mapped[str | None]
    school: Mapped[str | None]
    target: Mapped[str | None]
    domain: Mapped[str | None]
    trigger: Mapped[str | None]
    deity: Mapped[str | None]
    requirement: Mapped[str | None]
    element: Mapped[str | None]
    range: Mapped[str | None]
    tradition: Mapped[str | None]
    patron_theme: Mapped[str | None]
    actions: Mapped[str | None]
    component: Mapped[str | None]
    duration: Mapped[str | None]
    cost: Mapped[str | None]
    bloodline: Mapped[str | None]
    saving_throw: Mapped[str | None]
    lesson: Mapped[str | None]
    level: Mapped[str | None]
    heighten_level: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="spell")

    __table_args__ = (
        Index('ix_spell_name', 'name'),
    )


class Ritual(Base, BaseModel):
    __tablename__ = 'ritual'
    secondary_check: Mapped[str | None]
    target: Mapped[str | None]
    requirement: Mapped[str | None]
    secondary_casters: Mapped[str | None]
    area: Mapped[str | None]
    duration: Mapped[str | None]
    element: Mapped[str | None]
    cost: Mapped[str | None]
    level: Mapped[str | None]
    heighten: Mapped[str | None]
    school: Mapped[str | None]
    range: Mapped[str | None]
    primary_check: Mapped[str | None]
    heighten_level: Mapped[str | None]

    # item_type: Mapped[int] = relationship(ItemType, backref="ritual")

    __table_args__ = (
        Index('ix_ritual_name', 'name'),
    )


class AlchemistResearchField(Base, BaseModel):
    __tablename__ = 'alchemistresearchfield'

    # item_type: Mapped[int] = relationship(ItemType, backref="alchemistresearchfield")
    __table_args__ = (
        Index('ix_alchemistresearchfield_name', 'name'),
    )


class BardMuse(Base, BaseModel):
    __tablename__ = 'bardmuse'
    # item_type: Mapped[int] = relationship(ItemType, backref="bardmuse")
    __table_args__ = (
        Index('ix_bardmuse_name', 'name'),
    )


class BarbarianInstinct(Base, BaseModel):
    __tablename__ = 'barbarianinstinct'
    # item_type: Mapped[int] = relationship(ItemType, backref="barbarianinstinct")
    __table_args__ = (
        Index('ix_barbarianinstinct_name', 'name'),
    )


class ChampionCause(Base, BaseModel):
    alignment: Mapped[str | None]
    __tablename__ = 'championcause'
    # item_type: Mapped[int] = relationship(ItemType, backref="championcause")
    __table_args__ = (
        Index('ix_championcause_name', 'name'),
    )


class ChampionTenet(Base, BaseModel):
    __tablename__ = 'championtenet'
    # item_type: Mapped[int] = relationship(ItemType, backref="championtenet")
    __table_args__ = (
        Index('ix_championtenet_name', 'name'),
    )


class ClericDoctrine(Base, BaseModel):
    __tablename__ = 'clericdoctrine'
    # item_type: Mapped[int] = relationship(ItemType, backref="clericdoctrine")
    __table_args__ = (
        Index('ix_clericdoctrine_name', 'name'),
    )


class DruidicOrder(Base, BaseModel):
    __tablename__ = 'druidicorder'
    # item_type: Mapped[int] = relationship(ItemType, backref="druidicorder")
    __table_args__ = (
        Index('ix_druidicorder_name', 'name'),
    )


class RogueRacket(Base, BaseModel):
    __tablename__ = 'rogueracket'
    # item_type: Mapped[int] = relationship(ItemType, backref="rogueracket")
    __table_args__ = (
        Index('ix_rogueracket_name', 'name'),
    )


class RangerHuntersEdge(Base, BaseModel):
    __tablename__ = 'rangerhuntersedge'
    # item_type: Mapped[int] = relationship(ItemType, backref="rangerhuntersedge")
    __table_args__ = (
        Index('ix_rangerhuntersedge_name', 'name'),
    )


class SorcererBloodline(Base, BaseModel):
    spell: Mapped[str | None]
    __tablename__ = 'sorcererbloodline'
    # item_type: Mapped[int] = relationship(ItemType, backref="sorcererbloodline")
    __table_args__ = (
        Index('ix_sorcererbloodline_name', 'name'),
    )


class WizardArcaneSchool(Base, BaseModel):
    __tablename__ = 'wizardarcaneschool'
    # item_type: Mapped[int] = relationship(ItemType, backref="wizardarcaneschool")
    __table_args__ = (
        Index('ix_wizardarcaneschool_name', 'name'),
    )


class WizardArcaneThesis(Base, BaseModel):
    __tablename__ = 'wizardarcanethesis'
    # item_type: Mapped[int] = relationship(ItemType, backref="wizardarcanethesis")
    __table_args__ = (
        Index('ix_wizardarcanethesis_name', 'name'),
    )


class InvestigatorMethodology(Base, BaseModel):
    __tablename__ = 'investigatormethodology'
    # item_type: Mapped[int] = relationship(ItemType, backref="investigatormethodology")
    __table_args__ = (
        Index('ix_investigatormethodology_name', 'name'),
    )


class OracleMystery(Base, BaseModel):
    __tablename__ = 'oraclemystery'
    # item_type: Mapped[int] = relationship(ItemType, backref="oraclemystery")
    __table_args__ = (
        Index('ix_oraclemystery_name', 'name'),
    )


class SwashbucklerStyle(Base, BaseModel):
    __tablename__ = 'swashbucklerstyle'
    # item_type: Mapped[int] = relationship(ItemType, backref="swashbucklerstyle")
    __table_args__ = (
        Index('ix_swashbucklerstyle_name', 'name'),
    )


class WitchPatron(Base, BaseModel):
    __tablename__ = 'witchpatron'
    skill: Mapped[str | None]
    tradition: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="witchpatron")
    __table_args__ = (
        Index('ix_witchpatron_name', 'name'),
    )


class WitchLesson(Base, BaseModel):
    __tablename__ = 'witchlesson'
    # item_type: Mapped[int] = relationship(ItemType, backref="witchlesson")
    __table_args__ = (
        Index('ix_witchlesson_name', 'name'),
    )


class Domain(Base, BaseModel):
    __tablename__ = 'domain'
    deity: Mapped[str | None]
    advanced_domain_spell: Mapped[str | None]
    domain: Mapped[str | None]
    domain_spell: Mapped[str | None]
    advanced_apocryphal_spell: Mapped[str | None]
    apocryphal_spell: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="domain")

    __table_args__ = (
        Index('ix_domain_name', 'name'),
    )


class AnimalCompanion(Base, BaseModel):
    __tablename__ = 'animalcompanion'
    charisma: Mapped[str | None]
    strength_req: Mapped[str | None]
    constitution: Mapped[str | None]
    burrow_speed: Mapped[str | None]
    climb_speed: Mapped[str | None]
    dexterity: Mapped[str | None]
    swim_speed: Mapped[str | None]
    fly_speed: Mapped[str | None]
    sense: Mapped[str | None]
    intelligence: Mapped[str | None]
    size: Mapped[str | None]
    skill: Mapped[str | None]
    strength: Mapped[str | None]
    wisdom: Mapped[str | None]
    element: Mapped[str | None]
    speed: Mapped[str | None]
    land_speed: Mapped[str | None]
    max_speed: Mapped[str | None]
    hp: Mapped[int]
    # item_type: Mapped[int] = relationship(ItemType, backref="animalcompanion")

    __table_args__ = (
        Index('ix_animalcompanion_name', 'name'),
    )


class AnimalAdvancedOption(Base, BaseModel):
    __tablename__ = 'animaladvancedoption'
    # item_type: Mapped[int] = relationship(ItemType, backref="animaladvancedoption")

    __table_args__ = (
        Index('ix_animaladvancedoption_name', 'name'),
    )


class AnimalSpecialization(Base, BaseModel):
    __tablename__ = 'animalspecialization'
    # item_type: Mapped[int] = relationship(ItemType, backref="animalspecialization")

    __table_args__ = (
        Index('ix_animalspecialization_name', 'name'),
    )


class FamiliarSpecific(Base, BaseModel):
    __tablename__ = 'familiarspecific'
    # item_type: Mapped[int] = relationship(ItemType, backref="familiarspecific")

    __table_args__ = (
        Index('ix_familiarspecific_name', 'name'),
    )


class FamiliarAbility(Base, BaseModel):
    __tablename__ = 'familiarability'
    actions: Mapped[str | None]
    requirement: Mapped[str | None]
    ability_type: Mapped[str | None]
    frequency: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="familiarability")

    __table_args__ = (
        Index('ix_familiarability_name', 'name'),
    )


class Hazard(Base, BaseModel):
    __tablename__ = 'hazard'
    weakness: Mapped[str | None]
    hazard_type: Mapped[str | None]
    hp: Mapped[str | None]
    resistance: Mapped[str | None]
    all_resistance: Mapped[str | None]
    ac: Mapped[str | None]
    reflex: Mapped[str | None]
    complexity: Mapped[str | None]
    hardness: Mapped[str | None]
    immunity: Mapped[str | None]
    fortitude: Mapped[str | None]
    rarity: Mapped[str | None]
    school: Mapped[str | None]
    element: Mapped[str | None]
    level: Mapped[str | None]
    will: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="hazard")

    __table_args__ = (
        Index('ix_hazard_name', 'name'),
    )


class Deity(Base, BaseModel):
    __tablename__ = 'deity'
    divine_font: Mapped[str | None]
    deity: Mapped[str | None]
    follower_alignment: Mapped[str | None]
    domain: Mapped[str | None]
    favored_weapon: Mapped[str | None]
    ability_boost: Mapped[str | None]
    skill: Mapped[str | None]
    ability: Mapped[str | None]
    alignment: Mapped[str | None]
    deity_category: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="deity")

    __table_args__ = (
        Index('ix_deity_name', 'name'),
    )


class Trait(Base, BaseModel):
    __tablename__ = 'trait'
    # item_type: Mapped[int] = relationship(ItemType, backref="trait")

    __table_args__ = (
        Index('ix_trait_name', 'name'),
    )


class Language(Base, BaseModel):
    __tablename__ = 'language'
    # item_type: Mapped[int] = relationship(ItemType, backref="language")

    __table_args__ = (
        Index('ix_language_name', 'name'),
    )


class Condition(Base, BaseModel):
    __tablename__ = 'condition'
    # item_type: Mapped[int] = relationship(ItemType, backref="condition")

    __table_args__ = (
        Index('ix_condition_name', 'name'),
    )


class Source(Base, BaseModel):
    __tablename__ = 'source'
    # item_type: Mapped[int] = relationship(ItemType, backref="source")

    __table_args__ = (
        Index('ix_source_name', 'name'),
    )


class EquipmentVariant(Base, BaseModel):
    __tablename__ = 'equipment_variant'
    onset: Mapped[str | None]
    stage: Mapped[str | None]
    school: Mapped[str | None]
    spell: Mapped[str | None]
    item_category: Mapped[str | None]
    hands: Mapped[str | None]
    subcategory: Mapped[str | None]
    frequency: Mapped[str | None]
    price: Mapped[str | None]
    trigger: Mapped[str | None]
    bulk: Mapped[str | None]
    usage: Mapped[str | None]
    requirement: Mapped[str | None]
    item_subcategory: Mapped[str | None]
    element: Mapped[str | None]
    actions: Mapped[str | None]
    base_item: Mapped[str | None]
    duration: Mapped[str | None]
    saving_throw: Mapped[str | None]
    alignment: Mapped[str | None]
    level: Mapped[str | None]

    parent_id: int = Column(ForeignKey('equipment.id'))
    equipment = relationship('Equipment', back_populates='variants',)
    # item_type: Mapped[int] = relationship(ItemType, backref="equipment_variant")

    __table_args__ = (
        Index('ix_equipment_variant_name', 'name'),
    )


class Equipment(Base, BaseModel):
    __tablename__ = 'equipment'
    onset: Mapped[str | None]
    stage: Mapped[str | None]
    school: Mapped[str | None]
    spell: Mapped[str | None]
    item_category: Mapped[str | None]
    hands: Mapped[str | None]
    subcategory: Mapped[str | None]
    frequency: Mapped[str | None]
    price: Mapped[str | None]
    trigger: Mapped[str | None]
    bulk: Mapped[str | None]
    usage: Mapped[str | None]
    requirement: Mapped[str | None]
    item_subcategory: Mapped[str | None]
    element: Mapped[str | None]
    actions: Mapped[str | None]
    base_item: Mapped[str | None]
    duration: Mapped[str | None]
    saving_throw: Mapped[str | None]
    alignment: Mapped[str | None]
    level: Mapped[str | None]

    variants = relationship('EquipmentVariant', order_by=func.cast(EquipmentVariant.level, Integer), back_populates='equipment')
    # item_type: Mapped[int] = relationship(ItemType, backref="equipment")

    __table_args__ = (
        Index('ix_equipment_name', 'name'),
    )


class ArmorGroup(Base, BaseModel):
    __tablename__ = 'armorgroup'
    # item_type: Mapped[int] = relationship(ItemType, backref="armorgroup")

    __table_args__ = (
        Index('ix_armorgroup_name', 'name'),
    )


class Armor(Base, BaseModel):
    __tablename__ = 'armor'
    armor_category: Mapped[str | None]
    strength_req: Mapped[str | None]
    ac: Mapped[str | None]
    speed_penalty: Mapped[str | None]
    item_subcategory: Mapped[str | None]
    armor_group: Mapped[str | None]
    strength: Mapped[str | None]
    price: Mapped[str | None]
    dex_cap: Mapped[str | None]
    item_category: Mapped[str | None]
    bulk: Mapped[str | None]
    level: Mapped[str | None]
    check_penalty: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="armor")

    __table_args__ = (
        Index('ix_armor_name', 'name'),
    )


class Shield(Base, BaseModel):
    __tablename__ = 'shield'
    hp: Mapped[str | None]
    ac: Mapped[str | None]
    speed_penalty: Mapped[str | None]
    item_subcategory: Mapped[str | None]
    hardness: Mapped[str | None]
    price: Mapped[str | None]
    item_category: Mapped[str | None]
    bulk: Mapped[str | None]
    level: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="shield")

    __table_args__ = (
        Index('ix_shield_name', 'name'),
    )


class WeaponGroup(Base, BaseModel):
    __tablename__ = 'weapongroup'
    # item_type: Mapped[int] = relationship(ItemType, backref="weapongroup")

    __table_args__ = (
        Index('ix_weapongroup_name', 'name'),
    )


class Weapon(Base, BaseModel):
    __tablename__ = 'weapon'
    deity: Mapped[str | None]
    favored_weapon: Mapped[str | None]
    weapon_group: Mapped[str | None]
    item_subcategory: Mapped[str | None]
    damage: Mapped[str | None]
    bulk: Mapped[str | None]
    price: Mapped[str | None]
    weapon_type: Mapped[str | None]
    rarity: Mapped[str | None]
    item_category: Mapped[str | None]
    weapon_category: Mapped[str | None]
    range: Mapped[str | None]
    level: Mapped[str | None]
    hands: Mapped[str | None]
    # item_type: Mapped[int] = relationship(ItemType, backref="weapon")

    __table_args__ = (
        Index('ix_weapon_name', 'name'),
    )
