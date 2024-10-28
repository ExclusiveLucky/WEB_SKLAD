from .dependencies import *

@router.get("/task/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    # Получаем задачу по ID
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Возвращаем данные задачи
    return {
        "id": task.id,
        "task_description": task.task_description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

@router.post("/task/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Задача выполнена"}


@router.get("/admin/tasks")
async def get_admin_tasks(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    if user != "admin":
        return {"error": "Access denied"}

    tasks = db.query(Task).all()  # Все задачи
    return templates.TemplateResponse(
        "tasks.html", 
        {
            "request": request, 
            "tasks": tasks,
            "user": user, 
            "users": db.query(User).all()
            }
        )

# Эндпоинт для отображения задач для пользователя
@router.get("/user/tasks")
async def get_user_tasks(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.username == user).first()
    tasks = db.query(Task).filter(Task.user_id == user.id).filter(Task.is_completed == 0)  # Только задачи текущего пользователя
    return templates.TemplateResponse(
        "tasks.html", 
        {
            "request": request, 
            "tasks": tasks, 
            "user": user
            }
        )

class TaskCreate(BaseModel):
    task_description: str
    user_id: int

@router.post("/admin/add-task")
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        return {"success": False, "message": "Пользователь не найден"}
    
    new_task = Task(task_description=task.task_description, user_id=task.user_id, is_completed=False)
    db.add(new_task)
    db.commit()

    return {"success": True, "message": "Задача добавлена"}


@router.post("/start-shift")
def start_shift(db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    day_of_week = get_current_day()
    print(f"Today is: {day_of_week}")

    # Выбираем задачи для текущего дня
    weekly_tasks = db.query(WeeklyTask).filter(WeeklyTask.day == day_of_week).all()
    
    user_obj = db.query(User).filter(User.username == user).first()

    # Обновляем флаг "в работе"
    user_obj.is_working = True
    db.add(user_obj)  # Добавляем обновление в сессию
    db.add(WorkShift(user_id=user_obj.id))

    # Добавляем задачи в таблицу tasks
    for task in weekly_tasks:
        new_task = Task(user_id=user_obj.id, task_description=task.description, level=task.level, result=None, is_completed=False)
        db.add(new_task)

    db.commit()  # Коммитим обновления пользователя и задач


@router.post("/end-shift")
def end_shift(db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):

    user_obj = db.query(User).filter(User.username == user).first()

    user_obj.is_working = False
    db.add(user_obj)  # Добавляем обновление в сессию
    # Находим текущую смену пользователя
    work_shift = db.query(WorkShift).filter(WorkShift.user_id == user_obj.id, WorkShift.end_time == None).first()
    if work_shift:
        work_shift.end_time = datetime.utcnow()  # Устанавливаем время завершения смены
        db.add(work_shift)

    db.commit()  # Коммитим обновления пользователя и смены


