import os
from typing import Union, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: str
    DB_HOST: Union[str | int]
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    JWT_SECRET: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="allow",
        # env_file=os.path.dirname(os.getcwd()) + "/.env",
        env_file='.env'
    )

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # make automated script - get from glossary / compendium
    @property
    def allowed_links(self):
        return [
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
            "deity",
            "domain",
            "druidicorder",
            "equipment",
            "familiarability",
            "feat",
            # "generalskillaction",
            "hazard",
            "heritage",
            # "language",
            "monster",
            # "npc",
            "rangerhuntersedge",
            "ritual",
            "rogueracket",
            "shield",
            "sorcererbloodline",
            "spell",
            "skill",
            "trait",
            "weapon",
            "weapongroup",
            "wizardarcaneschool",
            "wizardarcanethesis",
            #     -----------APG--------------------
            "familiarspecific",
            "investigatormethodology",
            "oraclemystery",
            "swashbucklerstyle",
            "witchpatron",
            "witchlesson",
        ]

    @property
    def allowed_sources(self):
        return ["[[source/1|Core Rulebook]]", "[[source/39|Advanced Player's Guide]]",
                # "[[source/2|Bestiary]]",
                ]

    @property
    def popup_links(self):
        return ['action',
                'background',
                'weapon',
                'equipment',
                'armor',
                'trait',
                'condition',
                'feat',
                'generalskillaction',
                'hazard',
                'ritual',
                'shield',
                'spell',
                'familiarability',

                ]


settings = Settings()
