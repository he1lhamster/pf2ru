from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi_users import InvalidPasswordException

from starlette.responses import RedirectResponse

from templatetags import NewTemplateResponse
from users.accessor import UserManagerExtend
from users.auth.auth import fastapi_users, auth_backend, current_user, SECRET, google_oauth_client, cookie_transport, \
    current_user_optional
from users.auth.manager import UserManager, get_user_manager
from users.schemas import UserRead, UserCreate, UserUpdate
from config import settings

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/users",
    tags=["users", ],
)


@router.post("/auth/register", response_model=UserRead)
async def register(
        request: Request,
        user_create: UserCreate,
        user_manager: UserManager = Depends(get_user_manager)
):
    # user_create = UserCreate(email=email, password=password, username=username)
    user = await user_manager.create(user_create)
    return user


@router.get("/")
async def users_default(request: Request, user=Depends(current_user_optional)):
    if user:
        return RedirectResponse('/users/profile')
    return RedirectResponse('/users/login')


@router.get("/register")
async def user_register(request: Request):
    return await NewTemplateResponse("users/register.html", {"request": request})


@router.get("/reset-password")
async def reset_password(request: Request):
    return await NewTemplateResponse("users/forgot_password.html", {"request": request})


@router.get("/login")
async def login(request: Request, user=Depends(current_user_optional)):
    if user:
        return RedirectResponse('/users/profile')
    return await NewTemplateResponse("users/login.html", {"request": request})


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(cookie_transport.cookie_name)
    return


@router.get("/profile")
async def profile(request: Request, user=Depends(current_user), user_manager_e: UserManagerExtend = Depends()):
    if not user:
        return RedirectResponse("/")
    archive = await user_manager_e.get_archive_by_user_id(user.id)

    return await NewTemplateResponse("users/profile.html", {"request": request, "archive": archive})


@router.get("/is-authenticated")
async def users_is_authenticated(request: Request, user=Depends(current_user)):
    return {"message": "Authenticated"}


@router.get("/forgot-password")
async def user_forgot_password(request: Request):
    return await NewTemplateResponse('users/forgot_password.html', {'request': request})


@router.get("/reset")
async def user_reset_password(request: Request, token: str):
    return await NewTemplateResponse('users/reset_password.html', {'request': request, 'token': token})


@router.post("/is-valid-update")
async def user_is_valid_update(request: Request,
                               user_update: UserUpdate,
                               user=Depends(current_user),
                               user_manager=Depends(get_user_manager)
                               ):
    # TODO: correct change password form
    # if user_update.password:
    #     try:
    #         is_valid_password = await user_manager.validate_password(user_update.password, user_update)
    #     except InvalidPasswordException:
    #         raise HTTPException(status_code=400, detail="Неверный пароль")

    if not user_update.username:
        user_update.username = user.username
    else:
        is_valid_username = await user_manager.is_valid_username(user_update.username)
        if not is_valid_username:
            raise HTTPException(status_code=400, detail="Такое имя пользователя уже существует")

    return {"username": user_update.username}


@router.post("/is-valid-create")
async def user_is_valid_create(request: Request,
                               user_create: UserCreate,
                               user_manager=Depends(get_user_manager)
                               ):
    is_valid_email = await user_manager.is_valid_email(user_create.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail="Такая почта уже зарегистрирована")

    is_valid_username = await user_manager.is_valid_username(user_create.username)
    if not is_valid_username:
        raise HTTPException(status_code=400, detail="Такое имя пользователя уже существует")

    return {"status": 200}


@router.get("/verify")
async def verify_email(request: Request, token: str):
    return await NewTemplateResponse('users/verify.html', {'request': request, 'token': token})


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api",
    tags=["users"],
)
router.include_router(
    fastapi_users.get_oauth_router(google_oauth_client,
                                   auth_backend,
                                   SECRET,
                                   # redirect_url=settings.GOOGLE_REDIRECT_URI,
                                   redirect_url='http://localhost:8000/users/auth/google/callback',
                                   associate_by_email=True,
                                   is_verified_by_default=True,
                                   ),
    prefix="/auth/google",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, SECRET),
    prefix="/auth/associate/google",
    tags=["auth"],
)

