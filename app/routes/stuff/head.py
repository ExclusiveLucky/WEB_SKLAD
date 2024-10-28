from ..dependencies import *

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