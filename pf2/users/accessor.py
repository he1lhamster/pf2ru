from typing import List

from fastapi import Depends
from fastapi_users import exceptions
from fastapi_users.models import UP
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from typing_extensions import Optional

from users.models import User, OAuthAccount, ArchiveTheme, Archive, ArchiveNote
from database import get_async_session, async_session_maker
from users.schemas import ArchiveThemeCreate, ArchiveThemeUpdate, ArchiveNoteCreate, ArchiveNoteUpdate


class SQLAlchemyUserDatabaseExtend(SQLAlchemyUserDatabase):
    async def get_by_username(self, username: str) -> Optional[UP]:
        async with async_session_maker() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()
        return user


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabaseExtend(session, User, OAuthAccount)


class UserManagerExtend:

    def __init__(self, session: Session = Depends(get_async_session)):
        self.session = session

    @staticmethod
    async def get_user_by_id(user_id):
        async with async_session_maker() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise exceptions.UserNotExists()
            return user

    # ------------ ARCHIVE THEMES -----------------
    async def get_archive_by_user_id(self, user_id: int) -> Archive:
        archive = await self.session.execute(
            select(Archive).options(selectinload(Archive.themes)).where(Archive.user_id == user_id))
        return archive.scalar_one()

    async def get_themes_by_user_id(self, user_id: int) -> ArchiveTheme:
        user_archive = await self.get_archive_by_user_id(user_id)
        return await self.session.execute(select(ArchiveTheme).where(ArchiveTheme.archive_id == user_archive.id))

    async def get_theme_by_id(self, theme_id: int) -> ArchiveTheme:
        return await self.session.get(ArchiveTheme, theme_id)

    async def create_archive_theme(self, theme: ArchiveThemeCreate) -> ArchiveTheme:
        db_theme = ArchiveTheme(
            archive_id=theme.archive_id,
            name=theme.name,
            description=theme.description,
        )
        self.session.add(db_theme)
        await self.session.commit()
        await self.session.refresh(db_theme)

        return db_theme

    async def update_archive_theme(self, theme: ArchiveThemeUpdate) -> ArchiveTheme:
        db_theme = await self.get_theme_by_id(theme.id)
        if theme.name:
            db_theme.name = theme.name
        if theme.description:
            db_theme.description = theme.description
        await self.session.commit()
        return db_theme

    async def delete_archive_theme(self, db_theme: ArchiveTheme):
        await self.session.delete(db_theme)
        await self.session.commit()
        return

    # ------------ ARCHIVE NOTES -----------------

    async def get_note_by_id(self, note_id: int) -> ArchiveNote:
        return await self.session.get(ArchiveNote, note_id)

    async def get_notes_by_theme_id(self, theme_id: int) -> ArchiveNote:
        return await self.session.execute(select(ArchiveNote).where(ArchiveNote.archive_theme_id == theme_id))

    async def create_archive_note(self, note: ArchiveNoteCreate) -> ArchiveNote:
        db_note = ArchiveNote(
            archive_theme_id=note.archive_theme_id,
            title=note.title,
            text=note.text,
            item_type=note.item_type,
            item_id=note.item_id
        )
        self.session.add(db_note)
        await self.session.commit()
        await self.session.refresh(db_note)

        return db_note

    async def update_archive_note(self, note: ArchiveNoteUpdate) -> ArchiveNote:
        db_note = await self.get_note_by_id(note.id)
        if note.title:
            db_note.title = note.title
        if note.text:
            db_note.text = note.text
        if note.archive_theme_id:
            db_note.archive_theme_id = note.archive_theme_id
        await self.session.commit()
        return db_note

    async def delete_archive_note(self, db_note: ArchiveNote):
        await self.session.delete(db_note)
        await self.session.commit()
        return


user_manager_extend = UserManagerExtend()
