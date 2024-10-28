from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware import AuthMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.routes.client import site
from app.routes.stuff import auth, head, invoices, tasks, menu, settings, profile
# nohup uvicorn main:app --host 0.0.0.0 --port 8000 &

app = FastAPI()

# Подключаем middleware для проверки авторизации
app.add_middleware(AuthMiddleware)

# Подключаем маршруты
app.include_router(auth.router)
app.include_router(head.router)
app.include_router(invoices.router)
app.include_router(tasks.router)
app.include_router(menu.router)
app.include_router(settings.router)
app.include_router(profile.router)
app.include_router(site.router)


# Подключаем статические файлы (CSS, изображения)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/images", StaticFiles(directory="app/images"), name="images")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")

from datetime import date
print(date.today())

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
# Отображение задачь. Базовые задачи.
# Разобраться с масштабированием на айфонах.

# Разделить задачи на задачи  от админа которые видно всегда и задачи по смене, которые видны только после начала смены. 
# Можно ли завершить смену с невыполненными задачами? 
# Уровни задач ввести. Необязательный. Обязательный. Обязательный с фото. 
# Учет рабочего времени

## СКЛАД:
# 


## САЙТ:
# 

