from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from templatetags import NewTemplateResponse


router = APIRouter(
    prefix="/rules",
    tags=["Rules"],
)

templates = Jinja2Templates(directory="templates")


@router.get("")
async def get_rules_index(request: Request):
    lang = request.state.lang
    return await NewTemplateResponse("rules_index.html", {"request": request, "lang": lang})


@router.get("/core-rulebook/skills/{skill_name}")
async def core_rulebook_skill_page(request: Request, skill_name: str):
    lang = request.state.lang
    templ = f"core_rulebook/skills/{skill_name}-rus.html" if lang == 'ru' else f"core_rulebook/skills/{skill_name}.html"
    return await NewTemplateResponse(templ, {"request": request, "lang": lang})


@router.get("/core-rulebook")
async def core_rulebook_index(request: Request):
    templ = "core_rulebook/index.html"
    return await NewTemplateResponse(templ, {"request": request, })


@router.get("/core-rulebook/{chapter_name}")
async def core_rulebook_chapter(request: Request, chapter_name: str, ):
    if chapter_name not in [
        'introduction',
        'ancestries-and-backgrounds',
        'classes',
        'skills',
        'feats',
        'equipment',
        'spells',
        'the-age-of-lost-omens',
        'playing-the-game',
        'game-mastering',
        'crafting-and-treasure',
    ]:
        return await NewTemplateResponse('404error.html', {'status_code': 404, 'request': request, })

    lang = request.state.lang
    chapter_page = chapter_name.replace('-', '_')
    templ = f"core_rulebook/{chapter_page}-rus.html" if lang == 'ru' else f"core_rulebook/{chapter_page}.html"
    return await NewTemplateResponse(templ, {"request": request, "lang": lang})
