from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import auth, categories_products, tasks_workshifts, invoices
from app.middleware import AuthMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()

# Подключаем middleware для проверки авторизации
app.add_middleware(AuthMiddleware)

# Подключаем маршруты
app.include_router(auth.router)
app.include_router(categories_products.router)
app.include_router(tasks_workshifts.router)
app.include_router(invoices.router)

# Подключаем статические файлы (CSS, изображения)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
