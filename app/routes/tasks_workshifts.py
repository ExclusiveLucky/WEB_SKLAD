from .dependencies import *

@router.get("/admin/tasks")
async def get_admin_tasks(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    if user != "admin":
        return {"error": "Access denied"}

    tasks = db.query(Task).all()  # Все задачи
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

# Эндпоинт для отображения задач для пользователя
@router.get("/user/tasks")
async def get_user_tasks(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.username == user).first()
    tasks = db.query(Task).filter(Task.user_id == user.id).all()  # Только задачи текущего пользователя
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

# Эндпоинт для начала смены
@router.post("/start-shift")
async def start_shift(user: str = Depends(get_user_from_cookie), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user).first()
    if not user.is_working:
        new_shift = WorkShift(user_id=user.id, start_time=datetime.utcnow())
        db.add(new_shift)
        db.commit()
        db.refresh(new_shift)
        user.is_working = True
        db.commit()
        return {"message": "Shift started"}
    return {"message": "Already working"}