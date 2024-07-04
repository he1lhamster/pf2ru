import re

from config import settings
from content.models import *
from compendium import compendium

d_route = {
    "actions": ("action", Action),
    "alchemistresearchfields": ("alchemistresearchfield", AlchemistResearchField),
    "ancestries": ("ancestry", Ancestry),
    "animaladvancedoptions": ("animaladvancedoption", AnimalAdvancedOption),
    "animalcompanions": ("animalcompanion", AnimalCompanion),
    "animalspecializations": ("animalspecialization", AnimalSpecialization),
    "archetypes": ("archetype", Archetype),
    "armor": ("armor", Armor),
    "armorgroups": ("armorgroup", ArmorGroup),
    "backgrounds": ("background", Background),
    "barbarianinstincts": ("barbarianinstinct", BarbarianInstinct),
    "bardmuses": ("bardmuse", BardMuse),
    "championcauses": ("championcause", ChampionCause),
    "championtenets": ("championtenet", ChampionTenet),
    "classes": ("class_", Class_),
    "clericdoctrines": ("clericdoctrine", ClericDoctrine),
    "conditions": ("condition", Condition),
    "deities": ("deity", Deity),
    "domains": ("domain", Domain),
    "druidicorders": ("druidicorder", DruidicOrder),
    "equipment": ("equipment", Equipment),
    "familiarabilities": ("familiarability", FamiliarAbility),
    "feats": ("feat", Feat),
    "generalskillactions": ("generalskillaction", GeneralSkillAction),
    "hazards": ("hazard", Hazard),
    "heritages": ("heritage", Heritage),
    "languages": ("language", Language),
    # "monsters": ("monster", Monster),
    "rangerhuntersedges": ("rangerhuntersedge", RangerHuntersEdge),
    "rituals": ("ritual", Ritual),
    "roguerackets": ("rogueracket", RogueRacket),
    "shields": ("shield", Shield),
    # "skills": ("skill", Skill),
    "sorcererbloodlines": ("sorcererbloodline", SorcererBloodline),
    "spells": ("spell", Spell),
    "sources": ("source", Source),
    "traits": ("trait", Trait),
    "weapons": ("weapon", Weapon),
    "weapongroups": ("weapongroup", WeaponGroup),
    "wizardarcaneschools": ("wizardarcaneschool", WizardArcaneSchool),
    "wizardarcanethesises": ("wizardarcanethesis", WizardArcaneThesis),
    #  --------------APG----------------
    "familiarspecific": ("familiarspecific", FamiliarSpecific),
    "investigatormethodologies": ("investigatormethodology", InvestigatorMethodology),
    "oraclemysteries": ("oraclemystery", OracleMystery),
    "swashbucklerstyles": ("swashbucklerstyle", SwashbucklerStyle),
    "witchpatrons": ("witchpatron", WitchPatron),
    "witchlessons": ("witchlesson", WitchLesson),
}
d_type = {
    "action": ("actions", Action, 'Action', 'Действие'),
    "alchemistresearchfield": ("alchemistresearchfields", AlchemistResearchField, 'Alchemist Research Field', 'Область Исследования Алхимика'),
    "ancestry": ("ancestries", Ancestry, 'Ancestry', 'Народ'),
    "animaladvancedoption": ("animaladvancedoptions", AnimalAdvancedOption, 'Animal Advanced Option', 'Продвинутые Опции Верного Зверя'),
    "animalcompanion": ("animalcompanions", AnimalCompanion, 'Animal Companion', 'Верный Зверь'),
    "animalspecialization": ("animalspecializations", AnimalSpecialization, 'Animal Specialization', 'Специализация Верного Зверя'),
    "archetype": ("archetypes", Archetype, 'Archetype', 'Архетип'),
    "armor": ("armor", Armor, 'Armor', 'Броня'),
    "armorgroup": ("armorgroups", ArmorGroup, 'Armor Group', 'Эффект Привычной Брони'),
    "background": ("backgrounds", Background, 'Background', 'Происхождение'),
    "barbarianinstinct": ("barbarianinstincts", BarbarianInstinct, 'BarbarianInstinct', 'Инстинкт Варвара'),
    "bardmuse": ("bardmuses", BardMuse, 'BardMuse', 'Муза Барда'),
    "championcause": ("championcauses", ChampionCause, 'ChampionCause', 'Призвание Поборника'),
    "championtenet": ("championtenets", ChampionTenet, 'ChampionTenet', 'Заповедь Поборника'),
    "class_": ("classes", Class_, 'Class', 'Класс'),
    "clericdoctrine": ("clericdoctrines", ClericDoctrine, 'Cleric Doctrine', 'Доктрина Клерика'),
    "condition": ("conditions", Condition, 'Condition', 'Состояние'),
    "deity": ("deities", Deity, 'Deity', 'Божество'),
    "domain": ("domains", Domain, 'Domain', 'Домен'),
    "druidicorder": ("druidicorders", DruidicOrder, 'Druidic Order', 'Друидический Орден'),
    "equipment": ("equipment", Equipment, 'Equipment', ''),
    "familiarability": ("familiarabilities", FamiliarAbility, 'Familiar Ability', 'Способность Фамильяра'),
    "feat": ("feats", Feat, 'Feat', 'Черта'),
    "generalskillaction": ("generalskillactions", GeneralSkillAction, 'GeneralSkillAction', 'Общее Действие Навыков'),
    "hazard": ("hazards", Hazard, 'Hazard', 'Опасность'),
    "heritage": ("heritages", Heritage, 'Heritage', 'Родословная'),
    "language": ("languages", Language, 'Language', 'Язык'),
    # "monster": ("monsters", Monster, '', '),
    "rangerhuntersedge": ("rangerhuntersedges", RangerHuntersEdge, 'Ranger Hunters Edge', 'Преимущества Охотника'),
    "ritual": ("rituals", Ritual, 'Ritual', 'Ритуал'),
    "rogueracket": ("roguerackets", RogueRacket, 'RogueRacket', 'Стиль Плута'),
    "shield": ("shields", Shield, 'Shield', 'Щит'),
    # "skill": ("skills", Skill, 'SorcererBloodline', '),
    "sorcererbloodline": ("sorcererbloodlines", SorcererBloodline, 'Sorcerer Bloodline', 'Наследие Колдуна'),
    "source": ("sources", Source, 'Source', 'Источник'),
    "spell": ("spells", Spell, 'Spell', 'Заклинание'),
    "trait": ("traits", Trait, 'Trait', 'Дескриптор'),
    "weapon": ("weapons", Weapon, 'Weapon', 'Оружие'),
    "weapongroup": ("weapongroups", WeaponGroup, 'Weapon Group', 'Критические Эффекты Оружия'),
    "wizardarcaneschool": ("wizardarcaneschools", WizardArcaneSchool, 'Wizard Arcane School', 'Школы Магии Волшебника'),
    "wizardarcanethesis": ("wizardarcanethesises", WizardArcaneThesis, 'Wizard Arcane Thesis', 'Магическая Диссертация Волшебника'),
    #     -----------APG--------------------
    "familiarspecific": ("familiarspecific", FamiliarSpecific, 'Familiar Specific', 'Особенный Фамильяр'),
    "investigatormethodology": ("investigatormethodologies", InvestigatorMethodology, 'Investigator Methodology', 'Методология Следователя'),
    "oraclemystery": ("oraclemysteries", OracleMystery, 'Oracle Mystery', 'Тайна Оракула'),
    "swashbucklerstyle": ("swashbucklerstyles", SwashbucklerStyle, 'Swashbuckler Style', 'Стиль Сорвиголовы'),
    "witchpatron": ("witchpatrons", WitchPatron, 'Witch Patron', 'Покровитель Ведьмы'),
    "witchlesson": ("witchlessons", WitchLesson, 'Witch Lesson', 'Урок Ведьмы'),
    "equipment_variant": ('equipment_variant', EquipmentVariant, '', '')
}


def convert_to_traits(text: str) -> str:
    '''
    function convert to traits_output
    '''
    if not text:
        return ""

    pattern = r'\[\[(\w+)/(\w+)\|([^\]]+)\]\]'
    matches = re.findall(pattern, text)

    for m in matches:
        link_type, link_id, link_label = m

        if compendium.is_allowed(link_type, int(link_id)):

            new_link = f'<a class="item-link item-link--traits-output" itemType="traits" itemId="{link_id}">{link_label}</a>'
        else:
            new_link = f'{link_label}'
        text = text.replace(f'[[{link_type}/{link_id}|{link_label}]]', new_link)
    return text


def convert_links(text: str) -> str:
    '''
    convert all md links in text to <a> tags, except mentioned in not_allowed_links
    :param text:
    :return: text with converted md links
    '''
    if not text:
        return ""

    pattern = r'\[\[(\w+)/(\w+)\|([^\]]+)\]\]'
    matches = re.findall(pattern, text)

    for m in matches:
        link_type, link_id, link_label = m
        try:
            link_name = compendium.id_to_name(link_type, int(link_id))
            if not compendium.is_allowed(link_type, int(link_id)):
                text = text.replace(f'[[{link_type}/{link_id}|{link_label}]]', f' <i>{link_label}</i>')
                continue

            if link_type in settings.popup_links:
                new_link = f'''
                            <span>
                            <span class="rhombus" itemID={link_id} itemType={d_type[link_type][0]} onclick="getItem(this)"></span>
                            <a class="item-link link--popup item-link--{link_type}" href="/{d_type[link_type][0]}/{link_name}">{link_label}</a>
                            </span>
                            '''
            else:
                new_link = f'''<a class="item-link item-link--{link_type}" href="/{d_type[link_type][0]}/{link_name}">{link_label}</a>'''

            text = text.replace(f'[[{link_type}/{link_id}|{link_label}]]', new_link)
        except KeyError:
            text = text.replace(f'[[{link_type}/{link_id}|{link_label}]]', f' <i>{link_label}</i>')

    return text


def links_to_text(text: str) -> str:
    if not text:
        return ""

    pattern = r'\[\[(\w+)/(\w+)\|([^\]]+)\]\]'
    matches = re.findall(pattern, text)

    for m in matches:
        link_type, link_id, link_label = m
        text = text.replace(f'[[{link_type}/{link_id}|{link_label}]]', link_label)

    return text
