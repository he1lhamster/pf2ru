from fastapi import APIRouter, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from templatetags import NewTemplateResponse, route_to_rus
from content.accessor import ContentManager, item_types
from fastapi import HTTPException
from config import settings
from routers.converters import convert_links, convert_to_traits, d_route
from compendium import compendium

router = APIRouter(
    prefix="",
    tags=["Database", "DB", "db"],
)


@router.get("/database")
async def get_database_index(request: Request):
    return await NewTemplateResponse("database.html", {"request": request})


@router.get("/conditions")
async def get_conditions(request: Request, accessor: ContentManager = Depends()):
    conditions = await accessor.get_conditions()

    if not conditions:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/conditions.html", {
        "request": request,
        "conditions": conditions,
    })


@router.get("/actions")
async def get_actions(request: Request, accessor: ContentManager = Depends()):
    actions = await accessor.get_actions()

    if not actions:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/actions.html", {
        "request": request,
        "basic_actions": actions["basic_actions"],
        "exploration_actions": actions["exploration_actions"],
        "downtime_actions": actions["downtime_actions"],
        "general_skill_actions": actions["general_skill_actions"],
    })


@router.get("/ancestries")
async def get_ancestries(request: Request, accessor: ContentManager = Depends()):
    ancestries = await accessor.get_ancestries()
    vers_heritages = await accessor.get_versatile_heritages()

    if not ancestries:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/ancestries.html", {
        "request": request,
        "ancestries": ancestries,
        "vers_heritages": vers_heritages,
    }
                               )


@router.get("/versatile-heritages")
async def get_versatile_heritages(request: Request, accessor: ContentManager = Depends()):
    vers_heritages = await accessor.get_versatile_heritages()

    if not vers_heritages:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/versatile_heritages.html", {
        "request": request,
        "vers_heritages": vers_heritages,
    }
                               )


@router.get("/heritages/{heritage_id}")
async def get_versatile_heritage(request: Request,
                                 heritage_id: str,
                                 tab: str = None,
                                 accessor: ContentManager = Depends()):
    heritage = await accessor.get_item_by_id('heritages', heritage_id)

    if not heritage:
        raise HTTPException(status_code=404)

    heritage_feats = await accessor.get_heritage_feats(heritage['id'])

    if heritage['rus_name'] and request.state.lang == 'ru':
        placeholder = f"Родословная: {heritage['rus_name']}"
    else: # not have rus
        placeholder = f"Heritage: {heritage['name']}"

    return await NewTemplateResponse("content/versatile_heritage.html", {
        "request": request,
        "heritage": heritage,
        "feats": heritage_feats,
        "placeholder": placeholder,
    })


@router.get("/ancestries/{ancestry_id}")
async def get_ancestry(request: Request,
                       ancestry_id: str,
                       tab: str = None,
                       accessor: ContentManager = Depends()):
    ancestry = await accessor.get_item_by_id('ancestries', ancestry_id)

    if not ancestry:
        raise HTTPException(status_code=404)

    ancestry_feats = await accessor.get_ancestry_feats(ancestry['id'])
    heritages = await accessor.get_heritages(ancestry['id'])

    versatile_heritages = await accessor.get_versatile_heritages()

    if ancestry['rus_name'] and request.state.lang == 'ru':
        placeholder = f"Родословная: {ancestry['rus_name']}"
    else: # not have rus
        placeholder = f"Heritage: {ancestry['name']}"

    return await NewTemplateResponse("content/ancestry.html", {
        "request": request,
        "ancestry": ancestry,
        "feats": ancestry_feats,
        "heritages": heritages,
        "versatile_heritages": versatile_heritages,
        "placeholder": placeholder,
    })


@router.get("/classes/{class_id}")
async def get_class_(request: Request, class_id: str, tab: str = None, accessor: ContentManager = Depends()):
    if class_id == 'animal companions':
        animal_companions = await accessor.get_animal_companions()
        return await NewTemplateResponse("content/animal_companions.html", {
            "request": request,
            "tab": tab,
            'animal_companions': animal_companions['animal_companions'],
            'animal_advanced_options': animal_companions['animal_advanced_options'],
            'animal_specializations': animal_companions['animal_specializations']

        })
    elif class_id == 'familiars':
        familiars = await accessor.get_familiars()
        familiar_abilities = familiars["familiar_abilities"]
        familiar_specific = familiars["familiar_specific"]

        return await NewTemplateResponse("content/familiars.html", {
            "request": request,
            "tab": tab,
            "familiar_abilities": familiar_abilities,
            "familiar_specific": familiar_specific,
        })
    else:
        class_ = await accessor.get_item_by_id('classes', class_id)

        if not class_:
            raise HTTPException(status_code=404)

        if class_['rus_name'] and request.state.lang == 'ru':
            placeholder = f"Родословная: {class_['rus_name']}"
        else:  # not have rus
            placeholder = f"Heritage: {class_['name']}"

        class_d = {
            "request": request,
            "tab": tab,
            "class_": class_,
            'feats': await accessor.get_class_feats(class_['id']),
            'spells': await accessor.get_class_spells(class_['id']),
            "placeholder": placeholder,
        }

        if class_['id'] == 1:
            class_d['alchemistresearchfields'] = await accessor.get_class_features("alchemistresearchfields")
        elif class_['id'] == 2:
            class_d['barbarianinstincts'] = await accessor.get_class_features("barbarianinstincts")
        elif class_['id'] == 3:
            class_d['bardmuses'] = await accessor.get_class_features("bardmuses")
        elif class_['id'] == 4:
            class_d['championcauses'] = await accessor.get_class_features("championcauses")
            class_d['championtenets'] = await accessor.get_class_features("championtenets")
        elif class_['id'] == 5:
            class_d['clericdoctrines'] = await accessor.get_class_features("clericdoctrines")
        elif class_['id'] == 6:
            class_d['druidicorders'] = await accessor.get_class_features("druidicorders")
        elif class_['id'] == 9:
            class_d['rangerhuntersedges'] = await accessor.get_class_features("rangerhuntersedges")
        elif class_['id'] == 10:
            class_d['roguerackets'] = await accessor.get_class_features("roguerackets")
        elif class_['id'] == 11:
            class_d['sorcererbloodlines'] = await accessor.get_class_features("sorcererbloodlines")
        elif class_['id'] == 12:
            class_d['wizardarcaneschools'] = await accessor.get_class_features("wizardarcaneschools")
            class_d['wizardarcanethesises'] = await accessor.get_class_features("wizardarcanethesises")
        # --------- APG ---------------
        elif class_['id'] == 13:
            class_d['investigatormethodologies'] = await accessor.get_class_features("investigatormethodologies")
        elif class_['id'] == 14:
            class_d['oraclemysteries'] = await accessor.get_class_features("oraclemysteries")
        elif class_['id'] == 15:
            class_d['swashbucklerstyles'] = await accessor.get_class_features("swashbucklerstyles")
        elif class_['id'] == 16:
            class_d['witchpatrons'] = await accessor.get_class_features("witchpatrons")
            class_d['witchlessons'] = await accessor.get_class_features("witchlessons")

        # ----------------MISC----
        # elif class_d['id'] == 'miscellaneous':

        return await NewTemplateResponse("content/class_.html", context=class_d)


@router.get("/backgrounds")
async def get_backgrounds(request: Request,
                          accessor: ContentManager = Depends(),
                          tab: str = None

                          ):
    backgrounds = await accessor.get_backgrounds()

    if not backgrounds:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/backgrounds.html", {
        "request": request,
        "general_bg": backgrounds["general_bg"],
    })


@router.get("/feats")
async def get_feats(request: Request, accessor: ContentManager = Depends()):
    feats = await accessor.get_feats()

    return await NewTemplateResponse("content/feats.html", {
        "request": request,
        "feats": feats["feats"],
        "general_feats": feats["general_feats"],
    })


@router.get("/archetypes")
async def get_archetypes(request: Request, accessor: ContentManager = Depends()):
    archetypes = await accessor.get_archetypes(lang=request.state.lang)

    if not archetypes:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/archetypes.html", {
        "request": request,
        "other_archetypes": archetypes["other_archetypes"],
        "multiclass_archetypes": archetypes["multiclass_archetypes"],
    })


@router.get("/spells")
async def get_spells(request: Request, tab: str = None, accessor: ContentManager = Depends()):
    spells = await accessor.get_spells(tab)

    if not spells:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/spells.html", {
        "request": request,
        "spells": spells,
    })


@router.get("/rituals")
async def get_rituals(request: Request, accessor: ContentManager = Depends()):
    rituals = await accessor.get_rituals()

    if not rituals:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/rituals.html", {
        "request": request,
        "rituals": rituals,
    })


@router.get("/equipment")
async def get_equipment(request: Request, tab: str = None, accessor: ContentManager = Depends()):
    # items = await accessor.get_equipment()

    # if not items:
    #     raise HTTPException(status_code=404)

    return await NewTemplateResponse("content/equipment.html", {
        "request": request,
        # "items": items,
    })


@router.get("/setting")
async def get_setting(request: Request, tab: str = None, accessor: ContentManager = Depends()):
    domains = await accessor.get_domains()
    deities = await accessor.get_deities()

    return await NewTemplateResponse("content/setting.html", {
        "request": request,
        "domains": domains,
        "deities": deities,
    })


@router.get("/adventuring")
async def get_adventuring(request: Request, tab: str = None, accessor: ContentManager = Depends()):
    services = await accessor.get_services()
    hazards = await accessor.get_hazards()

    return await NewTemplateResponse("content/adventuring.html", {
        "request": request,
        "services": services,
        "hazards": hazards,
    })


@router.get("/search")
async def search_request(request: Request, q: str = None, accessor: ContentManager = Depends()):
    if not q:
        return await NewTemplateResponse("search.html", {"request": request, "results": None, 'query': q, })
    results = await accessor.search(q)
    return await NewTemplateResponse("search.html", {"request": request, "results": results, 'query': q, })


# ------------ BELOW - common handlers, add new above this line ----------------

limiter = Limiter(key_func=get_remote_address)


@router.get("/{item_type}/{item_id}")
@limiter.limit("30/minute")
async def get_item_page(
        request: Request,
        item_type: str,
        item_id: int | str,
        accessor: ContentManager = Depends()
):

    if item_type not in compendium.allowed_links:
        raise HTTPException(status_code=404)

    item = await accessor.get_item_by_id(item_type, item_id)

    if not item:
        raise HTTPException(status_code=404)

    if isinstance(item, list):
        return await NewTemplateResponse("content/multiple_found.html",
                                   {
                                       "request": request,
                                       "items": item,
                                       "item_type": item_type,
                                   })

    popup_link = True if item_type in settings.popup_links else False

    if item['rus_name'] and request.state.lang == 'ru':
        if item['rus_type_level']:
            placeholder = f"{item['rus_type_level']}: {item['rus_name']}"
        else:
            placeholder = f"{route_to_rus(item_type)}: {item['rus_name']}"
    else: # not have rus
        if item['type_level']:
            placeholder = f"{item['type_level']}: {item['name']}"
        else:
            placeholder = f"{d_route[item_type][0]}: {item['name']}"

    return await NewTemplateResponse("content/item_page.html",
                                       {
                                           "request": request,
                                           "item": item,
                                           "item_type": item_type,
                                           "need_viewbox": popup_link,
                                           "placeholder": placeholder,
                                       }
                                )


# for lists of item
@router.get("/{item_type}")
async def get_list_of_items(
        request: Request,
        item_type: str,
        accessor: ContentManager = Depends()
):
    if item_type not in compendium.allowed_links and item_type not in item_types:
        raise HTTPException(status_code=404)

    if item_type in item_types:
        items = await accessor.get_equipment_by_type(item_type)

        return await NewTemplateResponse(f"content/equipment_category.html", {
            "request": request,
            "items": items,
            "item_type": item_types[item_type],
        })

    items = await accessor.get_item_list(item_type, request.state.lang)
    if not items:
        raise HTTPException(status_code=404)

    return await NewTemplateResponse(f"content/{item_type}.html", {
        "request": request,
        "items": items,
    })


@router.get("/viewbox/{item_type}/{item_id}")
async def get_item_viewbox(
        request: Request,
        item_type: str,
        item_id: int | str,
        lang: str = None,
        accessor: ContentManager = Depends()
):
    if item_type not in compendium.allowed_links:
        raise HTTPException(status_code=404)
    # item_type = await route_to_model(item_type)
    if not lang or lang == 'null':
        lang = request.state.lang
    item = await accessor.get_item_viewbox_by_id(item_type, item_id, lang)

    if not item:
        raise HTTPException(status_code=404)

    from templatetags import viewbox_r
    item["traits_output"] = convert_to_traits(item["traits_output"]) if item["traits_output"] else ""
    item["text_output"] = convert_links(viewbox_r(item["text_output"])) if item["text_output"] else ""

    return await NewTemplateResponse("content/item.html", {"request": request, "item": item, "item_type": item_type, })

