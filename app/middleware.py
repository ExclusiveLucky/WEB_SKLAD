from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Проверяем наличие куки "user"
        user = request.cookies.get("user")
        
        # Если пользователь не залогинен и не находится на странице логина
        if not user and request.url.path not in ["/login", "/logout", "/register"]:
            return RedirectResponse(url="/login")
        
        # Продолжаем обработку запроса
        response = await call_next(request)
        return response