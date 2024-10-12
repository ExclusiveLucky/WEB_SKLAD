from fastapi import APIRouter, Depends, HTTPException, Request, Form, Cookie
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from ..database import get_db
from pytz import timezone
from datetime import datetime, date
from ..models import Category, Product, User, Task, WorkShift, Invoice, InvoiceItem
from pydantic import BaseModel

router = APIRouter()

# Настраиваем шаблоны
templates = Jinja2Templates(directory="app/templates")

# Функция для получения пользователя из куки
def get_user_from_cookie(user: str = Cookie(None)):
    if user:
        return user
    return None