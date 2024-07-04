from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from httpx_oauth.clients.google import GoogleOAuth2
from users.models import User
from users.auth.manager import get_user_manager
from config import settings

cookie_transport = CookieTransport(cookie_name="pf2ru_user", cookie_max_age=60 * 60 * 24 * 365)
SECRET = settings.JWT_SECRET

google_oauth_client = GoogleOAuth2(
    settings.GOOGLE_OAUTH_CLIENT_ID,
    settings.GOOGLE_OAUTH_CLIENT_SECRET,
)


# TODO: Add Refresh Token mechanism
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 60 * 24 * 365)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True, verified=True)
current_user_optional = fastapi_users.current_user(active=True, optional=True)
