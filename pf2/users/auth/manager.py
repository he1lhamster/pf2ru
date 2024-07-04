from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union

import aiosmtplib
from aiosmtplib.email import formataddr
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions, InvalidPasswordException
from sqlalchemy import select

from database import async_session_maker
from users.models import *
from users.accessor import get_user_db

from config import settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET
    verification_token_lifetime_seconds = 86400
    reset_password_token_lifetime_seconds = 86400
    SECRET = settings.JWT_SECRET
    user_db_model = User

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        if not user.is_verified:
            await self.request_verify(user)

        async with async_session_maker() as session:
            archive = Archive(user_id=user.id)
            session.add(archive)
            await session.commit()
            await session.refresh(archive)

            name = "Общее"
            description = "Общая группа для любых заметок"
            title = "Приветственное письмо"
            text = 'Приветствую на pf2.ru! В данном разделе "Библиотека" можно добавлять записи / заметки по ' \
                   'различным объектам, аналогично "закладкам" или "избранному". На странице конкретных объектов ' \
                   'есть иконка пера возле названия, нажав на которую можно добавить заметку по данному объекту. ' \
                   'Заметки можно объединять в группы - "книжные полки", например, можно добавить черты и ' \
                   'заклинания, которые вы планируете выбрать для вашего персонажа в конкретной Тропе Приключений. '
            # else:
            #     name = "General"
            #     description = "General group for your notes"
            #     title = "Greeting letter"
            #     text = 'Welcome to pf2.ru! In this "Library" section, you can add entries/notes about various objects, similar to "bookmarks" or "favorites." On the page of specific objects, there is a feather-pen icon next to the name, which you can click to add a note about that object. Notes can be grouped into "bookshelves" – for example, you can add feats and spells that you plan to choose for your character in a specific Adventure Path.'

            theme = ArchiveTheme(archive_id=archive.id, name=name, description=description)
            session.add(theme)
            await session.commit()
            await session.refresh(theme)

            note = ArchiveNote(archive_theme_id=theme.id, text=text, title=title)
            session.add(note)
            await session.commit()
        return

    async def validate_password(
        self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) <= 3:
            raise InvalidPasswordException(password)
        return

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        reset_link = f"https://pf2.ru/users/reset?token={token}"
        message = MIMEMultipart()
        message['Subject'] = "PF2.RU Восстановление пароля"
        message['From'] = formataddr(('Animal Messenger', settings.EMAIL_USER))
        message['To'] = user.email
        # message['Reply-To'] = email
        message.attach(MIMEText(
            f"Для восстановления пароля, пожалуйста, пройдите по ссылке: {reset_link}"))
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                start_tls=True,
                username=settings.EMAIL_USER,
                password=settings.EMAIL_PASSWORD,
            )
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def on_after_reset_password(
            self, user: User, request: Optional[Request] = None
    ):
        body_json = await request.json()
        password = body_json['password']
        return {'username': user.email, 'password': password}

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        verif_link = f"https://pf2.ru/users/verify?token={token}"
        message = MIMEMultipart()
        message['Subject'] = "PF2.RU Подтверждение регистрации"
        message['From'] = formataddr(('Animal Messenger', settings.EMAIL_USER))
        message['To'] = user.email
        # message['Reply-To'] = email
        message.attach(MIMEText(f"Добро пожаловать на pf2.ru, {user.username}!. Для завершения регистрации, пожалуйста, пройдите по ссылке: {verif_link}"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                start_tls=True,
                username=settings.EMAIL_USER,
                password=settings.EMAIL_PASSWORD,
            )
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        is_valid_username = await self.is_valid_username(user_create.username)
        if not is_valid_username:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["username"] = user_create.username

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def is_valid_username(self, username: str) -> bool:
        if len(username) < 3:
            return False
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).filter_by(username=username)
            )
            username_exist = result.scalars().first()

            if username_exist:
                return False

            return True

    async def is_valid_email(self, user_email: str) -> bool:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).filter_by(email=user_email)
            )
            email_exist = result.scalars().first()
            if email_exist:
                return False

            return True

    # async def authenticate(self, username: str, password: str):
    #
    #     # user_db = await self.user_db.get_by_username(username)
    #     try:
    #         user = await self.user_db.get_by_username(username)
    #
    #     except exceptions.UserNotExists:
    #         self.password_helper.hash(password)
    #         return None
    #
    #     verified, updated_password_hash = self.password_helper.verify_and_update(
    #         password, user.hashed_password
    #     )
    #     if not verified:
    #         return None
    #     # Update password hash to a more robust one if needed
    #     if updated_password_hash is not None:
    #         await self.user_db.update(user, {"hashed_password": updated_password_hash})
    #
    #     return user
    #
    # async def oauth_callback(
    #     self: "BaseUserManager[models.UOAP, models.ID]",
    #     oauth_name: str,
    #     access_token: str,
    #     account_id: str,
    #     account_email: str,
    #     expires_at: Optional[int] = None,
    #     refresh_token: Optional[str] = None,
    #     request: Optional[Request] = None,
    #     *,
    #     associate_by_email: bool = False,
    #     is_verified_by_default: bool = False,
    # ) -> models.UOAP:
    #
    #     oauth_account_dict = {
    #         "oauth_name": oauth_name,
    #         "access_token": access_token,
    #         "account_id": account_id,
    #         "account_email": account_email,
    #         "expires_at": expires_at,
    #         "refresh_token": refresh_token,
    #     }
    #
    #     try:
    #         user = await self.get_by_oauth_account(oauth_name, account_id)
    #     except exceptions.UserNotExists:
    #         try:
    #             # Associate account
    #             user = await self.get_by_email(account_email)
    #             if not associate_by_email:
    #                 raise exceptions.UserAlreadyExists()
    #             user = await self.user_db.add_oauth_account(user, oauth_account_dict)
    #         except exceptions.UserNotExists:
    #             # Create account
    #             password = self.password_helper.generate()
    #             user_dict = {
    #                 "email": account_email,
    #                 "hashed_password": self.password_helper.hash(password),
    #                 "is_verified": is_verified_by_default,
    #                 "username": account_email,  # add username
    #             }
    #             user = await self.user_db.create(user_dict)
    #             user = await self.user_db.add_oauth_account(user, oauth_account_dict)
    #             await self.on_after_register(user, request)
    #     else:
    #         # Update oauth
    #         for existing_oauth_account in user.oauth_accounts:
    #             if (
    #                 existing_oauth_account.account_id == account_id
    #                 and existing_oauth_account.oauth_name == oauth_name
    #             ):
    #                 user = await self.user_db.update_oauth_account(
    #                     user, existing_oauth_account, oauth_account_dict
    #                 )
    #
    #     return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


