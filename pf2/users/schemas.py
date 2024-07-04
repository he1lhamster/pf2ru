from fastapi_users import schemas
from pydantic import EmailStr, BaseModel
from typing_extensions import Optional


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    username: str


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr
    username: Optional[str] = None
    # password: Optional[str] = None


class ArchiveThemeRead(BaseModel):
    id: int
    name: str
    description: Optional[str]


class ArchiveThemeCreate(BaseModel):
    archive_id: Optional[int]
    name: str
    description: Optional[str]


class ArchiveThemeUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    description: Optional[str]


class ArchiveNoteRead(BaseModel):
    id: int
    archive_theme_id: int
    title: str
    text: Optional[str]
    item_type: Optional[str]
    item_id: Optional[int]


class ArchiveNoteCreate(BaseModel):
    archive_theme_id: int
    title: str
    text: Optional[str]
    item_type: Optional[str]
    item_id: Optional[int]


class ArchiveNoteUpdate(BaseModel):
    id: int
    archive_theme_id: Optional[int] = None
    title: Optional[str]
    text: Optional[str]
