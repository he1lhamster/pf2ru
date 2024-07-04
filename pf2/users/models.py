from typing import List
from datetime import datetime

from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, ForeignKey

from content.models import *
from database import Base
from fastapi_users.db import SQLAlchemyBaseOAuthAccountTable, SQLAlchemyBaseUserTable


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    __tablename__ = "oauth_account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    oauth_name: Mapped[str] = mapped_column(
        String(length=100), index=True, nullable=False
    )
    access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(length=1024), nullable=True
    )
    account_id: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_pf2.id"), nullable=False)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user_pf2'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password = mapped_column(String, nullable=False)
    is_active = mapped_column(Boolean, default=True, nullable=False)
    is_superuser = mapped_column(Boolean, default=False, nullable=False)
    is_verified = mapped_column(Boolean, default=False, nullable=False)
    registration_date = mapped_column(DateTime, default=datetime.now(), nullable=False)
    archive = relationship("Archive", back_populates="user", uselist=False, cascade="all, delete-orphan")
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )


class Archive(Base):
    __tablename__ = 'archive'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: int = Column(ForeignKey('user_pf2.id'))
    user = relationship("User", back_populates="archive")
    themes = relationship("ArchiveTheme", back_populates="archive", cascade="all, delete-orphan")


class ArchiveTheme(Base):
    __tablename__ = 'archive_theme'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    archive_id: int = Column(ForeignKey('archive.id'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    create_date = mapped_column(DateTime, default=datetime.now(), nullable=False)
    archive = relationship("Archive", back_populates="themes")
    notes = relationship("ArchiveNote", back_populates="theme", cascade="all, delete-orphan")


class ArchiveNote(Base):
    __tablename__ = 'archive_note'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    archive_theme_id: int = Column(ForeignKey('archive_theme.id'))
    text: Mapped[str] = mapped_column(String)
    create_date = mapped_column(DateTime, default=datetime.now(), nullable=False)
    title: Mapped[str] = mapped_column(String)
    item_type: Mapped[str | None] = mapped_column(String, nullable=True)
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    theme = relationship("ArchiveTheme", back_populates="notes")
