import json

from sqlalchemy import select
from database import async_session_maker
from config import settings


class Compendium:
    # dict looks like {"type": { id: {"eng": eng_name, "rus": rus_name, "src": source}, }, }
    def __init__(self):
        self.all_types = [
            "action",
            "alchemistresearchfield",
            "ancestry",
            "animaladvancedoption",
            "animalcompanion",
            "animalspecialization",
            "archetype",
            "armor",
            "armorgroup",
            "background",
            "barbarianinstinct",
            "bardmuse",
            "championcause",
            "championtenet",
            "class_",
            "clericdoctrine",
            "condition",
            "curse",
            "deity",
            "disease",
            "domain",
            "druidicorder",
            "equipment",
            "familiarability",
            "familiarspecific",
            "feat",
            "generalskillaction",
            "gunslingerway",
            "hazard",
            "hellknightorder",
            "heritage",
            "inventorinnovation",
            "investigatormethodology",
            "kineticistelement",
            "kingdomevent",
            "kingdomstructure",
            "kingmakercampsitemeal",
            "kingmakerwarfarearmy",
            "kingmakerwarfaretactic",
            "language",
            "magushybridstudy",
            "monster",
            "monsterability",
            "monsterfamily",
            "npc",
            "oraclemystery",
            "plane",
            "psychicconsciousmind",
            "psychicsubconsciousmind",
            "rangerhuntersedge",
            "relic",
            "ritual",
            "rogueracket",
            "setrelic",
            "shield",
            "siegeweapon",
            "skill",
            "sorcererbloodline",
            "source",
            "spell",
            "summonereidolon",
            "swashbucklerstyle",
            "thaumaturgeimplement",
            "trait",
            "uniqueanimalcompanion",
            "vehicle",
            "weapon",
            "weapongroup",
            "weatherhazard",
            "witchlesson",
            "witchpatron",
            "wizardarcaneschool",
            "wizardarcanethesis",
        ]
        self.compendium = {}
        self.allowed_links = {}
        self.allowed_types = []

    async def init(self):
        from routers.converters import d_type

        async with async_session_maker() as session:
            for item_type in self.all_types:

                if item_type not in d_type:
                    continue

                current_model = d_type[item_type][1]
                current_router = d_type[item_type][0]

                temp_d = {}
                allowed_temp_d = {}  # { "type": {id: name, }, }

                all_items = await session.execute(select(current_model)
                                                  .order_by(current_model.id)
                                                  )
                items = [x.__dict__ for x in all_items.scalars().all()]

                for item in items:
                    if item["rus_name"] and item["source"] in settings.allowed_sources \
                            and item_type in settings.allowed_links:
                        allowed_temp_d[int(item['id'])] = item["name"].lower()

                    if not item["rus_name"]: item["rus_name"] = ""

                    temp_d[int(item['id'])] = {
                                   "eng": item['name'].lower(),
                                   "rus": item['rus_name'].lower(),
                                   "src": item['source'],
                                   }

                if item_type in settings.allowed_links:
                    self.allowed_types.append(item_type)
                    self.allowed_links[current_router] = allowed_temp_d
                self.compendium[item_type] = temp_d

        with open('compendium.json', 'w', encoding='utf-8') as w_compendium:
            json.dump(self.compendium, w_compendium)

    def name_to_id(self, item_type: str, item_name: str) -> list | None:
        """
        get item_type and item_name, find and return its id (or ids) from compendium
        else return None
        """
        found_items = []

        if item_type not in self.compendium:
            return None
        for k, v in self.compendium[item_type].items(): # id: {"eng": "", "rus": "", "src": "", }
            if v["eng"] == item_name.lower():
                found_items.append(int(k))
        if not found_items:
            return None

        return found_items if len(found_items) > 1 else found_items[0]

    def id_to_name(self, item_type: str, item_id: int) -> str | None:
        """
        get item_type and item_id, find and return its name from compendium
        name doesn't lower
        else return None
        """
        if item_type not in self.compendium or \
           item_id not in self.compendium[item_type]:
            return None

        return self.compendium[item_type][item_id]["eng"]

    async def update_compendium(self, item_types: str | None):
        from routers.converters import d_type
        async with async_session_maker() as session:
            if not item_types:
                return
            for item_type in item_types:
                current_model = d_type[item_type][1]

                all_items = await session.execute(select(current_model.id, current_model.name,
                                                         current_model.source, current_model.rus_name)
                                                  )
                items = [x.__dict__ for x in all_items.scalars().all()]
                for item in items:

                    self.compendium[item_type][int(item['id'])] = {
                        "eng": item['name'].lower(),
                        "rus": item['rus_name'].lower(),
                        "src": item['source'],
                    }

    def is_allowed(self, item_type: str, item_id: int) -> bool:
        from routers.converters import d_type
        item_link_type = d_type[item_type][0]

        if item_link_type in self.allowed_links and item_id in self.allowed_links[item_link_type]:
            return True
        return False


compendium = Compendium()
