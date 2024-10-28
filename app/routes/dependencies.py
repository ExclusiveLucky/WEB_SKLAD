from fastapi import APIRouter, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import JSONResponse, RedirectResponse

from sqlalchemy.orm import selectinload, Session
from sqlalchemy import and_, extract, func

from datetime import datetime, timedelta, date

from starlette.status import HTTP_303_SEE_OTHER
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from ..database import get_db
from ..models import Category, Product, User, Task, WorkShift, Invoice, InvoiceItem, WeeklyTask

from pydantic import BaseModel
from pytz import timezone
import pytz


router = APIRouter()

# Настраиваем шаблоны
templates = Jinja2Templates(directory="app/templates")

def get_current_day():
    return datetime.now().isoweekday()

# Функция для получения пользователя из куки
def get_user_from_cookie(user: str = Cookie(None)):
    if user:
        return user
    return None

def calculate_time_and_earnings(shifts):
    total_seconds = sum(
        (shift.end_time - shift.start_time).total_seconds() if shift.end_time else 0
        for shift in shifts
    )
    total_hours, remainder = divmod(total_seconds, 3600)
    total_minutes = remainder // 60
    earnings = (total_seconds / 3600) * 180  # 180 руб/час
    return total_hours, total_minutes, earnings