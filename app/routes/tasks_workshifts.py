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
    tasks = db.query(Task).filter(Task.user_id == user.id).all()  # Только задачи текущего пользователя
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