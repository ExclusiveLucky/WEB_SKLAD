from .dependencies import *

# class User():
#     nickname: str
#     status: str


@router.get("/stuff/invoices")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    # invoices = db.query(Invoice).filter(func.date(Invoice.created_at) == date.today()).all()
    invoices = db.query(Invoice).all()
    return templates.TemplateResponse("stuff/invoices.html", 
                                      {"request": request,
                                       "user":user,
                                       "invoices": invoices,
                                       "label":"Закрытые счета",})


@router.get("/stuff/tasks")
def status(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    user = db.query(User).filter(User.username == user).first()
    tasks = db.query(Task).filter(Task.user_id == user.id).filter(Task.is_completed == 0)  # Только задачи текущего пользователя
    return templates.TemplateResponse("stuff/tasks.html", {"request": request, "tasks": tasks, "user":user})

@router.post("/stuff/start-shift")
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


@router.post("/stuff/end-shift")
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


@router.get("/stuff/menu")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    categories = db.query(Category).all()
    user = db.query(User).filter(User.username == user).first()
    return templates.TemplateResponse("stuff/menu.html", {"request": request, "categories": categories,"user":user})

# Страница товаров для конкретной категории
@router.get("/stuff/category/{category_id}", response_class=HTMLResponse)
def get_products(request: Request, category_id: int, db: Session = Depends(get_db), user: str = Cookie(None)):
    category = db.query(Category).filter(Category.id == category_id).first()
    products = db.query(Product).filter(Product.category_id == category_id).all()
    user = db.query(User).filter(User.username == user).first()

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return templates.TemplateResponse("stuff/category.html", {"request": request, "products": products, "category": category,"user":user})

@router.get("/stuff/settings")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    return templates.TemplateResponse("stuff/settings.html", {"request": request,"user":user})

@router.get("/stuff/profile")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    return templates.TemplateResponse("stuff/profile.html", {"request": request,"user":user})