from typing import Callable

import jwt
from fastapi import Request, HTTPException

from starlette.middleware.base import BaseHTTPMiddleware
from users.accessor import user_manager_extend
from config import settings


async def language_middleware(request: Request, call_next: Callable):
    if 'lang' not in request.cookies:
        request.state.lang = 'ru'  # rus by default
    else:
        request.state.lang = request.cookies['lang']

    response = await call_next(request)
    if 'lang' not in request.cookies:
        response.set_cookie(key="lang", value="ru")
    return response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next, user_manager=user_manager_extend):
        try:
            cookie = request.cookies.get("pf2ru_user")

            if not cookie:
                request.state.user = None
                response = await call_next(request)
                return response

            payload = jwt.decode(cookie, settings.JWT_SECRET, audience=["fastapi-users:auth"], algorithms=['HS256'])
            user_id = payload['sub']
            user = await user_manager.get_user_by_id(int(user_id))

            request.state.user = user

        except Exception as e:
            raise HTTPException(status_code=422, detail="Authentication token incorrect. Clear cookies and try again.")
            # print(e)

        response = await call_next(request)
        return response


# not applied
async def url_converter(request: Request, call_next: Callable):
    # 2010: ‐
    # 2011: ‑
    path = request.scope['path']

    # if '-' in path:
    #     path = path.replace('-', '+')
    # if ' ' in path:
    #     path = path.replace(' ', '-')
    #

    return await call_next(request)


