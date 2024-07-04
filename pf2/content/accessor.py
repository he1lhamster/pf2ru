from fastapi import Depends
from sqlalchemy import select, func, Integer, case, or_, and_, cast, String, desc
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from typing import Any

from database import get_async_session
from compendium import compendium

from routers.converters import d_route, d_type
from config import settings
from content.models import *

viewbox_fields = [
    'id',
    'name',
    'traits_output',
    'text_output',
    'actions',
    'type_level',
]

rus_fields = {
    'id': 'id',
    'rus_name': 'name',
    'actions': 'actions',
    'rus_type_level': 'type_level',
    'rus_traits_output': 'traits_output',
    'rus_text_output': 'text_output',
}

item_types = {
    'adventuring-gear': 'Adventuring Gear',
    'held-items': 'Held Items',
    'materials': 'Materials',
    'snares': 'Snares',
    'staves': 'Staves',
    'structures': 'Structures',
    'services': 'Services',
    'worn-items': 'Worn Items',
    'alchemical-items': 'Alchemical Items',
    'consumables': 'Consumables',
    'armor': 'Armor',
    'shields': 'Shields',
    'weapons': 'Weapons',
    'runes': 'Runes',
    'wands': 'Wands',
}


def order_by_integer_part(column):
    if not column:
        return 0
    return func.cast(func.regexp_replace(column, '[^0-9]', '', 'g'), Integer)


class ContentManager:
    def __init__(self, session: Session = Depends(get_async_session)):
        self.session = session

    async def get_item_viewbox_by_id(self, item_type: str, item_id: int | str, lang: str | None = None):

        if item_type in d_route:
            item_type = d_route[item_type][0]

        if isinstance(item_id, str):
            item_id = int(item_id) if item_id.isdigit() else compendium.name_to_id(item_type, item_id)

        # FILTER - source in settings.allowed_sources
        item = await self.session.get(d_type[item_type][1], item_id)

        if not item or item.__dict__['source'] not in settings.allowed_sources:
            return None

        if lang == 'ru' and item.__dict__['rus_name']:
            item_dict = {rus_fields[k]: v for k, v in item.__dict__.items() if k in rus_fields}
        else:
            item_dict = {k: v for k, v in item.__dict__.items() if k in viewbox_fields}

        if not item.__dict__['type_level']:
            item_dict['type_level'] = d_type[item_type][3] if lang == 'ru' else d_type[item_type][2]

        item_dict['url'] = f"/{d_type[item_type][0]}/{item.__dict__['name'].lower()}"

        return item_dict

    async def get_item_by_id(self, item_type: str, item_id: int | str):

        if item_id.isdigit():
            item_id = int(item_id)
        else:
            item_id = compendium.name_to_id(d_route[item_type][0], item_id)

            if not item_id: return None

            # if return more than one item
            if isinstance(item_id, list):
                items = []
                for i in item_id:
                    item = await self.session.get(d_route[item_type][1], i)
                    items.append(item)
                return items

        item = await self.session.get(d_route[item_type][1], item_id)

        if not item or item.__dict__['source'] not in settings.allowed_sources:
            return None
        return {k: v for k, v in item.__dict__.items()}

    async def get_item_list(self, item_type: str, lang: str = None):

        # FILTER - source in settings.allowed_sources
        if item_type not in d_route:
            return None

        item_model = d_route[item_type][1]

        items = await self.session.execute(select(item_model)
                                           .where(item_model.source.in_(settings.allowed_sources))
                                           .order_by(item_model.rus_name)
                                           )
        if not items:
            return None
        return [x.__dict__ for x in items.scalars().all()]

    async def get_ancestries(self):
        # got only ancestries, not versatile heritages
        ancestries = await self.session.execute(select(Ancestry)
                                                .filter_by(type="Ancestry")
                                                .where(Ancestry.source.in_(settings.allowed_sources))
                                                .order_by(Ancestry.rarity, Ancestry.rus_name)
                                                )
        return [x.__dict__ for x in ancestries.scalars().all()]

    async def get_heritages(self, ancestry_id: int):
        ancestry_heritages = await self.session.execute(select(Heritage)
                                                        .filter_by(ancestry_id=str(ancestry_id))
                                                        .where(Heritage.source.in_(settings.allowed_sources))
                                                        .order_by(Heritage.rus_name)
                                                        )
        return [x.__dict__ for x in ancestry_heritages.scalars().all()]

    async def get_versatile_heritages(self):
        versatile_heritages = await self.session.execute(select(Heritage)
                                                         .filter_by(ancestry_id=None)
                                                         .where(Heritage.source.in_(settings.allowed_sources))
                                                         .order_by(Heritage.rus_name)
                                                         )
        return [x.__dict__ for x in versatile_heritages.scalars().all()]

    async def get_ancestry_feats(self, ancestry_id: int):
        ancestry_name = compendium.id_to_name('ancestry', ancestry_id)

        ancestry_feats = await self.session.execute(
            select(Feat)
            .filter(Feat.traits_output.ilike(f'%|{ancestry_name}]]%'))
            .where(Feat.source.in_(settings.allowed_sources))
            .order_by(func.cast(Feat.level, Integer), Feat.rus_name)
        )

        return [x.__dict__ for x in ancestry_feats.scalars().all()]

    async def get_heritage_feats(self, heritage_id: int):
        heritage_name = compendium.id_to_name('heritage', heritage_id)
        heritage_feats = await self.session.execute(
            select(Feat)
            .filter(Feat.traits_output.ilike(f'%|{heritage_name}]]%'))
            .where(Feat.source.in_(settings.allowed_sources))
            .order_by(func.cast(Feat.level, Integer), Feat.rus_name)
        )

        return [x.__dict__ for x in heritage_feats.scalars().all()]

    async def get_backgrounds(self):
        all_backgrounds = await self.session.execute(select(Background)
                                                     .where(Background.source.in_(settings.allowed_sources))
                                                     .order_by(Background.rus_name)
                                                     )
        general_bg = await self.session.execute(select(Background)
                                                .filter_by(subcategory='general')
                                                .where(Background.source.in_(settings.allowed_sources))
                                                .order_by(Background.rus_name)
                                                )

        return {
            "all_backgrounds": [x.__dict__ for x in all_backgrounds.scalars().all()],
            "general_bg": [x.__dict__ for x in general_bg.scalars().all()],
        }

    async def get_classes(self):
        classes = await self.session.execute(select(Class_)
                                             .where(Class_.source.in_(settings.allowed_sources))
                                             .order_by(Class_.source, Class_.rus_name)
                                             )
        return [x.__dict__ for x in classes.scalars().all()]

    async def get_class_feats(self, class_id):
        class_name = compendium.id_to_name('class_', class_id)
        class_feats = await self.session.execute(
            select(Feat)
            .filter(Feat.traits_output.ilike(f'%|{class_name}]]%'))
            .where(Feat.source.in_(settings.allowed_sources))
            .order_by(func.cast(Feat.level, Integer), Feat.rus_name)
        )
        return [x.__dict__ for x in class_feats.scalars().all()]

    async def get_class_spells(self, class_id):
        class_name = compendium.id_to_name('class_', class_id)
        class_spells = await self.session.execute(
            select(Spell)
            .filter(Spell.traits_output.ilike(f'%|{class_name}]]%'))
            .where(Spell.source.in_(settings.allowed_sources))
            .order_by(func.cast(Spell.level, Integer), Spell.rus_name)
        )
        return [x.__dict__ for x in class_spells.scalars().all()] if class_spells else None

    async def get_class_features(self, feature: str):
        if feature not in d_route:
            return None

        class_features = await self.session.execute(select(d_route[feature][1])
                                                    .where(d_route[feature][1].source.in_(settings.allowed_sources))
                                                    .order_by(d_route[feature][1].rus_name)
                                                    )
        return [x.__dict__ for x in class_features.scalars().all()]

    async def get_feats(self):
        feats = await self.session.execute(select(Feat)
                                           .where(or_(
            Feat.traits_output.ilike('%|General]]%'),
            Feat.traits_output.ilike('%|Skill]]%')
        )
        )
                                           .where(Feat.source.in_(settings.allowed_sources))
                                           .order_by(func.cast(Feat.level, Integer), Feat.rus_name)
                                           )
        general_feats = await self.session.execute(select(Feat)
                                                   .filter(Feat.traits_output.ilike('%|General]]%'))
                                                   .filter(Feat.traits_output.notlike('%|Skill]]%'))
                                                   .where(Feat.source.in_(settings.allowed_sources))
                                                   .order_by(func.cast(Feat.level, Integer), Feat.rus_name)
                                                   )
        # skill_feats = await self.session.execute(select(Feat)
        #                                          .filter(Feat.traits_output.ilike('%|Skill]]%'))
        #                                          .where(Feat.source.in_(settings.allowed_sources))
        #                                          .order_by(func.cast(Feat.level, Integer), Feat.name)
        #                                          )
        return {
            "feats": [x.__dict__ for x in feats.scalars().all()],
            "general_feats": [x.__dict__ for x in general_feats.scalars().all()],
            # "skill_feats": [x.__dict__ for x in skill_feats.scalars().all()],
        }

    async def get_archetypes(self, lang: str = 'en'):
        other_archetypes = await self.session.execute(select(Archetype, Feat.id.label('feat_id'))
                                                      .where(Archetype.is_multiclass.is_(None))
                                                      .where(Archetype.source.in_(settings.allowed_sources))
                                                      .join(Feat, Feat.name.ilike(Archetype.name + ' dedication'))
                                                      .order_by(Archetype.level, Archetype.rus_name)
                                                      )
        archetypes = []
        for row in other_archetypes:
            arch_data = row[0].__dict__
            arch_data.update({
                'dedication_feat': f'{{{{ viewbox (type="feat", id="{row[1]}", name="{arch_data["name"]}", lang="{lang}") }}}}'})
            archetypes.append(arch_data)
        other_archetypes = archetypes
        archetypes = []
        multiclass_archetypes = await self.session.execute(select(Archetype, Feat.id.label('feat_id'))
                                                           .filter_by(is_multiclass=1)
                                                           .where(Archetype.source.in_(settings.allowed_sources))
                                                           .join(Feat, Feat.name.ilike(Archetype.name + ' dedication'))
                                                           )
        for row in multiclass_archetypes:
            arch_data = row[0].__dict__
            arch_data.update({
                'dedication_feat': f'{{{{ viewbox (type="feat", id="{row[1]}", name="{arch_data["name"]}", lang="{lang}") }}}}'})
            archetypes.append(arch_data)
        multiclass_archetypes = archetypes

        return {
            "other_archetypes": other_archetypes,
            "multiclass_archetypes": multiclass_archetypes,
        }

    async def get_spells(self, spell_type: str = None):

        if spell_type.lower() == 'focus-spells':
            spells = await self.session.execute(select(Spell)
                                                .where(Spell.type_level.ilike('%focus%'))
                                                .where(Spell.source.in_(settings.allowed_sources))
                                                .order_by(func.cast(Spell.level, Integer), Spell.rus_name)
                                                )
        elif spell_type.lower() in ['arcane', 'occult', 'divine', 'primal']:
            spells = await self.session.execute(select(Spell)
            .filter(Spell.tradition.icontains(spell_type))
            .where(Spell.source.in_(settings.allowed_sources))
            .order_by(case(
                (Spell.type.ilike('cantrip'), 1),
                (Spell.type.ilike('spell'), 2),
            ),
                func.cast(Spell.level, Integer), Spell.name
            )
            )
        elif not spell_type or spell_type.lower() == 'spells':
            spells = await self.session.execute(select(Spell)
            .where(Spell.type_level.ilike('%spell%'))
            .where(Spell.source.in_(settings.allowed_sources))
            .order_by(
                case(
                    (Spell.type.ilike('cantrip'), 1),
                    (Spell.type.ilike('spell'), 2),
                )
                , func.cast(Spell.level, Integer), Spell.name)
            )
        else:
            return None

        return [x.__dict__ for x in spells.scalars().all()]

    async def get_rituals(self):
        rituals = await self.session.execute(select(Ritual)
                                             .where(Ritual.source.in_(settings.allowed_sources))
                                             .order_by(func.cast(Ritual.level, Integer), Ritual.rus_name)
                                             )
        return [x.__dict__ for x in rituals.scalars().all()]

    async def get_animal_companions(self):
        animal_companions = await self.session.execute(select(AnimalCompanion)
                                                       .where(AnimalCompanion.source.in_(settings.allowed_sources)))
        animal_advanced_options = await self.session.execute(select(AnimalAdvancedOption)
        .where(
            AnimalAdvancedOption.source.in_(settings.allowed_sources))
        )
        animal_specializations = await self.session.execute(select(AnimalSpecialization)
        .where(
            AnimalSpecialization.source.in_(settings.allowed_sources))
        )

        return {
            "animal_companions": [x.__dict__ for x in animal_companions.scalars().all()],
            "animal_advanced_options": [x.__dict__ for x in animal_advanced_options.scalars().all()],
            "animal_specializations": [x.__dict__ for x in animal_specializations.scalars().all()],
        }

    async def get_familiars(self):
        familiar_abilities = await self.session.execute(select(FamiliarAbility)
        .where(FamiliarAbility.source.in_(settings.allowed_sources))
        .where(FamiliarAbility.ability_type.in_(['Familiar', 'Master']))
        .order_by(
            case(
                (FamiliarAbility.ability_type.ilike('familiar'), 1),
                (FamiliarAbility.ability_type.ilike('master'), 2),
            ), FamiliarAbility.name)
        )

        familiar_specific = await self.session.execute(select(FamiliarSpecific)
                                                       .where(FamiliarSpecific.source.in_(settings.allowed_sources))
                                                       .order_by(FamiliarSpecific.name)
                                                       )

        return {
            "familiar_abilities": [x.__dict__ for x in familiar_abilities.scalars().all()],
            "familiar_specific": [x.__dict__ for x in familiar_specific.scalars().all()],
        }

    async def get_actions(self):

        basic_actions = await self.session.execute(select(Action)
                                                   .where(Action.source.in_(settings.allowed_sources))
                                                   .where(Action.subcategory.ilike('basic'))
                                                   .order_by(Action.rus_name.asc())
                                                   )
        exploration_actions = await self.session.execute(select(Action)
                                                         .where(Action.source.in_(settings.allowed_sources))
                                                         .where(Action.subcategory.ilike('exploration'))
                                                         .order_by(Action.rus_name.asc())
                                                         )
        downtime_actions = await self.session.execute(select(Action)
                                                      .where(Action.source.in_(settings.allowed_sources))
                                                      .where(Action.subcategory.ilike('downtime'))
                                                      .order_by(Action.rus_name.asc())
                                                      )

        general_skill_actions = await self.session.execute(select(GeneralSkillAction)
                                                           .where(
            GeneralSkillAction.source.in_(settings.allowed_sources))
                                                           .order_by(GeneralSkillAction.rus_name.asc())
                                                           )

        return {
            "basic_actions": [x.__dict__ for x in basic_actions.scalars().all()],
            "exploration_actions": [x.__dict__ for x in exploration_actions.scalars().all()],
            "downtime_actions": [x.__dict__ for x in downtime_actions.scalars().all()],
            "general_skill_actions": [x.__dict__ for x in general_skill_actions.scalars().all()],
        }

    async def get_equipment(self):
        items = await self.session.execute(select(Equipment)
                                           .where(Equipment.source.in_(settings.allowed_sources))
                                           .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
                                           )
        return [x.__dict__ for x in items.scalars().all()]

    async def get_equipment_by_type(self, item_type: str):
        items = {}

        if item_type in item_types:
            all_items = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                   .where(Equipment.item_category.ilike(item_types[item_type]))
                                                   .where(Equipment.source.in_(settings.allowed_sources))
                                                   .order_by(order_by_integer_part(Equipment.type_level),
                                                             Equipment.rus_name)
                                                   )
            items[item_type] = [x.__dict__ for x in all_items.scalars().all()]

            if item_type == 'alchemical-items':
                items.update(await self.get_alchemical_items())
            elif item_type == 'consumables':
                items.update(await self.get_consumables())
            elif item_type == 'armor':
                items.update(await self.get_armor())
            elif item_type == 'weapons':
                items.update(await self.get_weapons())
            elif item_type == 'shields':
                items.update(await self.get_shields())
            elif item_type == 'worn-items':
                items.update(await self.get_worn_items())
            elif item_type == 'runes':
                items.update(await self.get_runes())
            elif item_type == 'wands':
                items.update(await self.get_wands())

        return items

    async def get_alchemical_items(self):
        alchemical_bombs = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical bombs'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_elixirs = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical elixirs'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(func.cast(func.regexp_replace(Equipment.type_level, '[^0-9]', '', 'g'), Integer),
                      Equipment.rus_name))
        alchemical_poisons = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical poisons'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_tools = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical tools'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_ammunition = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical ammunition'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        drugs = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                           .where(Equipment.item_subcategory.ilike('drugs'))
                                           .where(Equipment.source.in_(settings.allowed_sources))
                                           .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_plants = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical plants'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_food = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                     .where(Equipment.item_subcategory.ilike('alchemical food'))
                                                     .where(Equipment.source.in_(settings.allowed_sources))
                                                     .order_by(order_by_integer_part(Equipment.type_level),
                                                               Equipment.rus_name)
                                                     )
        bottled_monstrosities = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Bottled Monstrosities'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))
        alchemical_other = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('alchemical other'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name))

        return {
            "alchemical_bombs": [x.__dict__ for x in alchemical_bombs.scalars().all()],
            "alchemical_elixirs": [x.__dict__ for x in alchemical_elixirs.scalars().all()],
            "alchemical_poisons": [x.__dict__ for x in alchemical_poisons.scalars().all()],
            "alchemical_tools": [x.__dict__ for x in alchemical_tools.scalars().all()],
            "alchemical_ammunition": [x.__dict__ for x in alchemical_ammunition.scalars().all()],
            "drugs": [x.__dict__ for x in drugs.scalars().all()],
            "alchemical_plants": [x.__dict__ for x in alchemical_plants.scalars().all()],
            "alchemical_food": [x.__dict__ for x in alchemical_food.scalars().all()],
            "bottled_monstrosities": [x.__dict__ for x in bottled_monstrosities.scalars().all()],
            "alchemical_other": [x.__dict__ for x in alchemical_other.scalars().all()],
        }

    async def get_consumables(self):
        magical_ammunition = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('magical ammunition'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        oils = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('oils'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        potions = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('potions'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        talismans = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('talismans'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        other_consumables = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('other consumables'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        bottled_breath = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                    .where(Equipment.item_subcategory.ilike('bottled breath'))
                                                    .where(Equipment.source.in_(settings.allowed_sources))
                                                    .order_by(order_by_integer_part(Equipment.type_level),
                                                              Equipment.rus_name)
                                                    )
        fulu = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                          .where(Equipment.item_subcategory.ilike('fulu'))
                                          .where(Equipment.source.in_(settings.allowed_sources))
                                          .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
                                          )
        gadgets = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                             .where(Equipment.item_subcategory.ilike('gadgets'))
                                             .where(Equipment.source.in_(settings.allowed_sources))
                                             .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
                                             )
        missive = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                             .where(Equipment.item_subcategory.ilike('missive'))
                                             .where(Equipment.source.in_(settings.allowed_sources))
                                             .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
                                             )
        scrolls = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                             .where(Equipment.item_subcategory.ilike('scrolls'))
                                             .where(Equipment.source.in_(settings.allowed_sources))
                                             .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
                                             )
        spell_catalysts = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                     .where(Equipment.item_subcategory.ilike('spell catalysts'))
                                                     .where(Equipment.source.in_(settings.allowed_sources))
                                                     .order_by(order_by_integer_part(Equipment.type_level),
                                                               Equipment.rus_name)
                                                     )

        return {
            "magical_ammunition": [x.__dict__ for x in magical_ammunition.scalars().all()],
            "oils": [x.__dict__ for x in oils.scalars().all()],
            "potions": [x.__dict__ for x in potions.scalars().all()],
            "talismans": [x.__dict__ for x in talismans.scalars().all()],
            "other_consumables": [x.__dict__ for x in other_consumables.scalars().all()],
            "bottled_breath": [x.__dict__ for x in bottled_breath.scalars().all()],
            "fulu": [x.__dict__ for x in fulu.scalars().all()],
            "gadgets": [x.__dict__ for x in gadgets.scalars().all()],
            "missive": [x.__dict__ for x in missive.scalars().all()],
            "scrolls": [x.__dict__ for x in scrolls.scalars().all()],
            "spell_catalysts": [x.__dict__ for x in spell_catalysts.scalars().all()],
        }

    async def get_worn_items(self):
        companion_items = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                     .where(Equipment.item_subcategory.ilike('companion items'))
                                                     .where(Equipment.source.in_(settings.allowed_sources))
                                                     .order_by(order_by_integer_part(Equipment.type_level),
                                                               Equipment.rus_name)
                                                     )
        eidolon_items = await self.session.execute(select(Equipment).options(selectinload(Equipment.variants))
                                                   .where(Equipment.item_subcategory.ilike('eidolon items'))
                                                   .where(Equipment.source.in_(settings.allowed_sources))
                                                   .order_by(order_by_integer_part(Equipment.type_level),
                                                             Equipment.rus_name)
                                                   )
        other_worn_items = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('other worn items'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        return {
            "companion_items": [x.__dict__ for x in companion_items.scalars().all()],
            "eidolon_items": [x.__dict__ for x in eidolon_items.scalars().all()],
            "other_worn_items": [x.__dict__ for x in other_worn_items.scalars().all()],
        }

    async def get_armor(self):
        all_armor = await self.session.execute(select(Armor)
                                               .where(Armor.source.in_(settings.allowed_sources))
                                               .order_by(Armor.level, Armor.rus_name)
                                               )
        armor_specializations = await self.session.execute(
            select(ArmorGroup)
            .where(ArmorGroup.source.in_(settings.allowed_sources))
        )
        precious_material_armor = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('precious material armor'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        specific_magic_armor = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('specific magic armor'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )
        basic_magic_armor = await self.session.execute(
            select(Equipment)
            .where(Equipment.item_subcategory.ilike('basic magic armor'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(Equipment.rus_name)
        )

        return {
            "armor": [x.__dict__ for x in all_armor.scalars().all()],
            "armor_specializations": [x.__dict__ for x in armor_specializations.scalars().all()],
            "precious_material_armor": [x.__dict__ for x in precious_material_armor.scalars().all()],
            "specific_magic_armor": [x.__dict__ for x in specific_magic_armor.scalars().all()],
            "basic_magic_armor": [x.__dict__ for x in basic_magic_armor.scalars().all()],
        }

    async def get_shields(self):
        shields = await self.session.execute(select(Shield)
                                             .where(Shield.source.in_(settings.allowed_sources))
                                             .order_by(Shield.level, Shield.rus_name)
                                             )
        precious_material_shields = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('precious material shields'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        specific_magic_shields = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('specific shields'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        return {
            "shields": [x.__dict__ for x in shields.scalars().all()],
            "precious_material_shields": [x.__dict__ for x in precious_material_shields.scalars().all()],
            "specific_magic_shields": [x.__dict__ for x in specific_magic_shields.scalars().all()],
        }

    async def get_weapons(self):
        weapons_melee = await self.session.execute(select(Weapon)
        .where(Weapon.source.in_(settings.allowed_sources))
        .where(Weapon.weapon_type.ilike('melee'))
        .order_by(case(
            (Weapon.weapon_category.ilike('unarmed'), 1),
            (Weapon.weapon_category.ilike('simple'), 2),
            (Weapon.weapon_category.ilike('martial'), 3),
            (Weapon.weapon_category.ilike('advanced'), 4),
            (Weapon.weapon_category.ilike('ammunition'), 5),
        ),
            Weapon.level, Weapon.rus_name)
        )
        weapons_ranged = await self.session.execute(select(Weapon)
        .where(Weapon.source.in_(settings.allowed_sources))
        .where(Weapon.weapon_type.ilike('ranged'))
        .order_by(case(
            (Weapon.weapon_category.ilike('unarmed'), 1),
            (Weapon.weapon_category.ilike('simple'), 2),
            (Weapon.weapon_category.ilike('martial'), 3),
            (Weapon.weapon_category.ilike('advanced'), 4),
            (Weapon.weapon_category.ilike('ammunition'), 5),
        ),
            Weapon.level, Weapon.rus_name)
        )
        weapon_group = await self.session.execute(select(WeaponGroup)
                                                  .where(WeaponGroup.source.in_(settings.allowed_sources))
                                                  )
        precious_material_weapons = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('precious material weapons'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        specific_magic_weapons = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('specific magic weapons'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        basic_magic_weapons = await self.session.execute(
            select(Equipment)
            .where(Equipment.item_subcategory.ilike('basic magic weapons'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        beast_guns = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('beast guns'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )

        return {
            "weapons_melee": [x.__dict__ for x in weapons_melee.scalars().all()],
            "weapons_ranged": [x.__dict__ for x in weapons_ranged.scalars().all()],
            "weapon_specializations": [x.__dict__ for x in weapon_group.scalars().all()],
            "precious_material_weapons": [x.__dict__ for x in precious_material_weapons.scalars().all()],
            "specific_magic_weapons": [x.__dict__ for x in specific_magic_weapons.scalars().all()],
            "basic_magic_weapons": [x.__dict__ for x in basic_magic_weapons.scalars().all()],
            "beast_guns": [x.__dict__ for x in beast_guns.scalars().all()],
        }

    async def get_runes(self):
        fundamental_armor_runes = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Fundamental Armor Runes'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        fundamental_weapon_runes = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Fundamental Weapon Runes'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        armor_property_runes = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Armor Property Runes'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        weapon_property_runes = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Weapon Property Runes'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)

        )
        accessory_runes = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Accessory Runes'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        return {
            "fundamental_armor_runes": [x.__dict__ for x in fundamental_armor_runes.scalars().all()],
            "fundamental_weapon_runes": [x.__dict__ for x in fundamental_weapon_runes.scalars().all()],
            "armor_property_runes": [x.__dict__ for x in armor_property_runes.scalars().all()],
            "weapon_property_runes": [x.__dict__ for x in weapon_property_runes.scalars().all()],
            "accessory_runes": [x.__dict__ for x in accessory_runes.scalars().all()],
        }

    async def get_wands(self):
        magic_wands = await self.session.execute(select(Equipment)
                                                 .where(Equipment.item_subcategory.ilike('magic wands'))
                                                 .where(Equipment.source.in_(settings.allowed_sources))
                                                 .order_by(order_by_integer_part(Equipment.type_level),
                                                           Equipment.rus_name)
                                                 )
        speciality_wands = await self.session.execute(
            select(Equipment).options(selectinload(Equipment.variants))
            .where(Equipment.item_subcategory.ilike('Specialty Wands'))
            .where(Equipment.source.in_(settings.allowed_sources))
            .order_by(order_by_integer_part(Equipment.type_level), Equipment.rus_name)
        )

        return {
            "magic_wands": [x.__dict__ for x in magic_wands.scalars().all()],
            "speciality_wands": [x.__dict__ for x in speciality_wands.scalars().all()],
        }

    async def get_deities(self):
        deities = await self.session.execute(select(Deity)
        .where(Deity.source.in_(settings.allowed_sources))
        .order_by(
            case(
                (Deity.deity_category.ilike('Gods of the Inner Sea'), 1),
                (Deity.deity_category.ilike('Faiths & Philosophies'), 2),
            ), Deity.rus_name)
        )
        return [x.__dict__ for x in deities.scalars().all()]

    async def get_domains(self):
        domains = await self.session.execute(select(Domain)
                                             .where(Domain.source.in_(settings.allowed_sources))
                                             .order_by(Domain.rus_name)
                                             )
        return [x.__dict__ for x in domains.scalars().all()]

    async def get_services(self):
        services = await self.session.execute(select(Equipment)
                                              .where(Equipment.item_category.ilike('services'))
                                              .where(Equipment.source.in_(settings.allowed_sources))
                                              .order_by(Equipment.rus_name)
                                              )
        return [x.__dict__ for x in services.scalars().all()]

    async def get_afflictions(self):
        return None

    async def get_conditions(self):
        conditions = await self.session.execute(select(Condition)
                                                .where(Condition.source.in_(settings.allowed_sources))
                                                .order_by(Condition.rus_name)
                                                )
        return [x.__dict__ for x in conditions.scalars().all()]

    async def get_traits(self):
        conditions = await self.session.execute(select(Trait)
                                                .where(Trait.source.in_(settings.allowed_sources))
                                                .order_by(Trait.rus_name)
                                                )
        return [x.__dict__ for x in conditions.scalars().all()]

    async def get_hazards(self):
        hazards = await self.session.execute(select(Hazard)
        .where(Hazard.source.in_(settings.allowed_sources))
        .order_by(
            case(
                (Hazard.complexity.ilike('simple'), 1),
                (Hazard.complexity.ilike('complex'), 2),
            ),
            func.cast(Hazard.level, Integer), Hazard.rus_name)
        )
        return [x.__dict__ for x in hazards.scalars().all()]

    async def search(self, query: str) -> Any | None:
        results = []
        ts_query = " & ".join([x for x in query.split()])

        search_query = cast(ts_query, String)

        for item_type in compendium.allowed_types:
            table = d_type[item_type][1]

            rus_rank_name = func.coalesce(
                func.ts_rank_cd(func.to_tsvector('russian', table.rus_name),
                                func.to_tsquery('russian', search_query)), 0)

            rus_rank_text = func.coalesce (
                 func.ts_rank(func.to_tsvector('russian', table.rus_traits_output),
                              func.plainto_tsquery('russian', search_query)) +
                 func.ts_rank(func.to_tsvector('russian', table.rus_text_output),
                              func.plainto_tsquery('russian', search_query))
                 , 0)

            eng_rank_name = func.coalesce(
                func.ts_rank_cd(func.to_tsvector('english', table.name),
                                func.to_tsquery('english', search_query), 32), 0)

            eng_rank_text = func.coalesce(
                 func.ts_rank(func.to_tsvector('english', table.traits_output),
                              func.plainto_tsquery('english', search_query)) +
                 func.ts_rank(func.to_tsvector('english', table.text_output),
                              func.plainto_tsquery('english', search_query))
                 , 0)

            result = await self.session.execute(
                select(table.id,
                       table.name,
                       table.rus_name,
                       table.source,
                       table.type_level,
                       table.rus_type_level,
                       table.traits_output,
                       table.rus_traits_output,
                       rus_rank_name.label('rus_rank_name'),
                       rus_rank_text.label('rus_rank_text'),
                       eng_rank_name.label('eng_rank_name'),
                       eng_rank_text.label('eng_rank_text'),
                       )
                .where(
                    and_(
                        table.source.in_(settings.allowed_sources),
                        or_(
                            table.name.icontains(f'%{query}%'),
                            func.to_tsvector('russian', table.rus_name).op('@@')(
                                func.plainto_tsquery('russian', search_query)),
                            func.to_tsvector('english', table.name).op('@@')(
                                func.plainto_tsquery('russian', search_query)),
                            func.to_tsvector('russian', table.rus_text_output).op('@@')(
                                func.to_tsquery('russian', search_query)),
                            func.to_tsvector('english', table.text_output).op('@@')(
                                func.to_tsquery('english', search_query)),
                            func.to_tsvector('russian', table.rus_traits_output).op('@@')(
                                func.to_tsquery('russian', search_query)),
                            func.to_tsvector('english', table.traits_output).op('@@')(
                                func.to_tsquery('english', search_query))
                        )
                    )
                )
            )

            # rows = [x.__dict__ for x in result.scalars().all()]
            rows = result.fetchall()

            if rows:
                for x in rows:
                    results.append({
                        'id': x.id,
                        'name': x.name,
                        'rus_name': x.rus_name,
                        'source': x.source,
                        'type_level': x.type_level,
                        'rus_type_level': x.rus_type_level,
                        'traits_output': x.traits_output,
                        'rus_traits_output': x.rus_traits_output,
                        'rus_rank_text': x.rus_rank_text,
                        'eng_rank_text': x.eng_rank_text,
                        'rus_rank_name': x.rus_rank_name,
                        'eng_rank_name': x.eng_rank_name,
                        'item_type': item_type
                    })

        # sort by rank desc
        results.sort(key=lambda x: [x['rus_rank_name'],
                                    x['eng_rank_name'],
                                    -len(x['rus_name']),
                                    -len(x['name']),
                                    x['rus_rank_text'],
                                    x['eng_rank_text']],
                     reverse=True)

        return results

    async def add_item(self, item_type: str, item: Any) -> Any:
        pass

    async def edit_item(self, item_type: str, item: Any):
        pass
