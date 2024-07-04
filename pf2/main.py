from fastapi import FastAPI, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from middlewares import language_middleware, AuthMiddleware
from templatetags import NewTemplateResponse
from content.scripts import insert_tables, truncate_tables
from compendium import compendium

from routers.rules import router as rules_router
from routers.content import router as content_router
from routers.api import router as api_router
from routers.appendix import router as appendix_router
from routers.users import router as users_router


app = FastAPI(
    title="Pathfinder2eRus",
    description="App for players in pathfinder 2e, contains rules and content.",
    version="0.0.1",
    docs_url="/docs",
)


@app.on_event('startup')
async def on_startup_app():
    # await truncate_tables(['equipment_variant'])
    # await truncate_tables(['action', 'alchemistresearchfield', 'ancestry', 'animaladvancedoption', 'animalcompanion', 'animalspecialization', 'archetype', 'armor', 'armorgroup', 'background', 'barbarianinstinct', 'bardmuse', 'championcause', 'championtenet', 'class_', 'clericdoctrine', 'condition', 'deity', 'domain', 'druidicorder', 'equipment', 'familiarability', 'feat', 'generalskillaction', 'hazard', 'heritage', 'language', 'rangerhuntersedge', 'ritual', 'rogueracket', 'shield', 'sorcererbloodline', 'spell', 'trait', 'weapon', 'weapongroup', 'wizardarcaneschool', 'wizardarcanethesis', 'familiarspecific', 'investigatormethodology', 'oraclemystery', 'swashbucklerstyle', 'witchpatron', 'witchlesson', ])
    # await insert_tables(['action', 'alchemistresearchfield', 'ancestry', 'animaladvancedoption', 'animalcompanion', 'animalspecialization', 'archetype', 'armor', 'armorgroup', 'background', 'barbarianinstinct', 'bardmuse', 'championcause', 'championtenet', 'class_', 'clericdoctrine', 'condition', 'deity', 'domain', 'druidicorder', 'equipment', 'familiarability', 'feat', 'generalskillaction', 'hazard', 'heritage', 'language', 'rangerhuntersedge', 'ritual', 'rogueracket', 'shield', 'sorcererbloodline', 'spell', 'trait', 'weapon', 'weapongroup', 'wizardarcaneschool', 'wizardarcanethesis', 'familiarspecific', 'investigatormethodology', 'oraclemystery', 'swashbucklerstyle', 'witchpatron', 'witchlesson', ])
    # await insert_tables(['equipment_variant'])

    await compendium.init()
    pass


tags_metadata = [
    {
        'name': 'users',
        'description': 'Authorization, Registration, Personal Area',
    },
    {
        'name': 'rules',
        'description': 'Books and Rules',
    },
    {
        'name': 'content',
        'description': 'Database with all content'
    },
    {
        'name': 'bestiary',
        'description': 'Bestiary'
    },
    {
        'name': 'appendix',
        'description': 'Additional information and pages'
    },
]

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root(request: Request):
    return await NewTemplateResponse('main.html', {"request": request,})


@app.post("/set_language/{lang}")
async def set_language(response: Response, lang: str):
    response.set_cookie(key='lang', value=lang)
    return {"status": "200"}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('static/icons/favicon.ico')


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(users_router)
app.include_router(rules_router)
app.include_router(appendix_router)
app.include_router(api_router)
app.include_router(content_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(language_middleware)
app.add_middleware(AuthMiddleware)


