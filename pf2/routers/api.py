from typing import Any

from fastapi import APIRouter, Request, Depends, HTTPException

from content.accessor import ContentManager
# from content.schemas import ItemRead
from routers.converters import convert_links, convert_to_traits
import json

from users.accessor import UserManagerExtend
from users.auth.auth import current_user
from users.models import ArchiveTheme, Archive, ArchiveNote
from users.schemas import ArchiveThemeCreate, ArchiveThemeUpdate, ArchiveNoteCreate, ArchiveNoteUpdate, \
    ArchiveThemeRead, ArchiveNoteRead

router = APIRouter(
    prefix="/api",
    tags=["api", ],
)


#
# @router.post("/{item_type}/{item_id}")
# async def api_post_item(
#         request: Request,
#         item: Any,
#         accessor: ContentManager = Depends()
# ):
#     pass
#
#
# # replace field(s) in item
# @router.patch("/{item_type}/{item_id}")
# async def api_patch_item(
#         request: Request,
#         item: Any,
#         accessor: ContentManager = Depends()
# ):
#     pass


# ------------Archive Theme CRUD------------------
@router.get("/archive/themes")
async def api_get_archive_themes(request: Request,
                                 user=Depends(current_user),
                                 user_manager_e: UserManagerExtend = Depends()
                                 ):
    archive_themes = await user_manager_e.get_themes_by_user_id(user.id)
    return archive_themes.scalars().all()


@router.get("/archive/themes/{theme_id}")
async def api_get_archive_themes(request: Request,
                                 theme_id: int,
                                 user=Depends(current_user),
                                 user_manager_e: UserManagerExtend = Depends()
                                 ):
    archive_theme = await user_manager_e.get_theme_by_id(theme_id)
    return archive_theme


@router.post("/archive/themes")
async def api_create_archive_theme(request: Request,
                                   theme: ArchiveThemeCreate,
                                   user=Depends(current_user),
                                   user_manager_e: UserManagerExtend = Depends()
                                   ):
    user_archive = await user_manager_e.get_archive_by_user_id(user.id)
    if not user_archive:
        raise HTTPException(status_code=404, detail="Archive for user not found")

    theme.archive_id = user_archive.id
    archive_theme = await user_manager_e.create_archive_theme(theme)
    return ArchiveThemeRead(id=archive_theme.id, name=archive_theme.name, description=archive_theme.description)


@router.patch("/archive/themes/{theme_id}")
async def api_update_archive_theme(request: Request,
                                   theme: ArchiveThemeUpdate,
                                   theme_id: int,
                                   user=Depends(current_user),
                                   user_manager_e: UserManagerExtend = Depends()
                                   ):
    theme.id = theme_id
    archive_theme = await user_manager_e.update_archive_theme(theme)
    return ArchiveThemeRead(id=archive_theme.id, name=archive_theme.name, description=archive_theme.description)


@router.delete("/archive/themes/{theme_id}")
async def api_delete_archive_theme(request: Request,
                                   theme_id: int,
                                   user=Depends(current_user),
                                   user_manager_e: UserManagerExtend = Depends()
                                   ):
    archive_theme = await user_manager_e.get_theme_by_id(theme_id)
    await user_manager_e.delete_archive_theme(archive_theme)
    return


# --------- ARCHIVE NOTES CRUD ----------------------
@router.get("/archive/themes/{theme_id}/notes")
async def api_get_archive_notes(request: Request,
                                theme_id: int,
                                user=Depends(current_user),
                                user_manager_e: UserManagerExtend = Depends()
                                ):
    archive_notes = await user_manager_e.get_notes_by_theme_id(theme_id)
    return archive_notes.scalars().all()


@router.post("/archive/themes/{theme_id}/notes")
async def api_create_archive_note(request: Request,
                                  theme_id: int,
                                  note: ArchiveNoteCreate,
                                  user=Depends(current_user),
                                  user_manager_e: UserManagerExtend = Depends()
                                  ):
    note.archive_theme_id = theme_id
    archive_note = await user_manager_e.create_archive_note(note)
    return ArchiveNoteRead(id=archive_note.id, archive_theme_id=note.archive_theme_id, title=archive_note.title, text=archive_note.text, item_type=archive_note.item_type, item_id=archive_note.item_id)


@router.patch("/archive/themes/{theme_id}/notes/{note_id}")
async def api_update_archive_note(request: Request,
                                  note: ArchiveNoteUpdate,
                                  theme_id: int,
                                  note_id: int,
                                  user=Depends(current_user),
                                  user_manager_e: UserManagerExtend = Depends()
                                  ):
    note.id = note_id
    archive_note = await user_manager_e.update_archive_note(note)
    return ArchiveNoteRead(id=archive_note.id, archive_theme_id=note.archive_theme_id, title=archive_note.title, text=archive_note.text, item_type=archive_note.item_type, item_id=archive_note.item_id)


@router.delete("/archive/themes/{theme_id}/notes/{note_id}")
async def api_delete_archive_note(request: Request,
                                  theme_id: int,
                                  note_id: int,
                                  user=Depends(current_user),
                                  user_manager_e: UserManagerExtend = Depends()
                                  ):
    archive_note = await user_manager_e.get_note_by_id(note_id)
    await user_manager_e.delete_archive_note(archive_note)
    return

# ----------------------------


@router.get("/{item_type}/{item_id}")
async def api_get_item(
        request: Request,
        item_type: str,
        item_id: int,
        lang: str | None = None,
        accessor: ContentManager = Depends()
):
    if not lang:
        lang = request.state.lang

    item = await accessor.get_item_viewbox_by_id(item_type, item_id, lang)

    if item:
        from templatetags import viewbox_r
        item["traits_output"] = convert_to_traits(item["traits_output"]) if item["traits_output"] else ""
        item["text_output"] = viewbox_r(item["text_output"]) if item["text_output"] else ""
        item["status"] = 200

        return json.dumps(item)
    else:
        return {"status": 404}

