from .dependencies import *

@router.get("/register")
def register_form(request: Request):
    # Отрисовка формы регистрации
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(None),
    birth_date: str = Form(None),
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь с таким именем
    user_obj = db.query(User).filter(User.username == username).first()
    
    if user_obj:
        # Перенаправляем на страницу регистрации с сообщением об ошибке
        return RedirectResponse(url="/register?error=Пользователь уже существует", status_code=HTTP_303_SEE_OTHER)

    # Создание нового пользователя
    new_user = User(
        username=username,
        password=password,  # Пароль пока что сохраняем в открытом виде
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date() if birth_date else None
    )
    
    db.add(new_user)
    db.commit()

    # После успешной регистрации перенаправляем на страницу логина
    return RedirectResponse(url="/admin/tasks", status_code=HTTP_303_SEE_OTHER)

# Страница входа
@router.get("/login")
def login_page():
    return templates.TemplateResponse("login.html", {"request": {}})

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user_obj = db.query(User).filter(User.username == username).first()
    
    if user_obj is None:
        # Перенаправляем на страницу логина с сообщением об ошибке
        return RedirectResponse(url="/login?error=Неправильный логин", status_code=HTTP_303_SEE_OTHER)

    if user_obj.password == password:
        response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
        response.set_cookie(key="user", value=username)  # Устанавливаем куки с логином
        return response
    else:
        # Перенаправляем на страницу логина с сообщением об ошибке
        return RedirectResponse(url="/login?error=Неправильный пароль", status_code=HTTP_303_SEE_OTHER)

# Маршрут для выхода из системы
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user")  # Удаляем куки
    return response

# Функция для получения пользователя из куки
def get_user_from_cookie(user: str = Cookie(None)):
    if user:
        return user
    return None