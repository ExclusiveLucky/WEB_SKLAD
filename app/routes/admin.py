from .dependencies import *

# Маршрут для отметки товара как проданного (прием данных через AJAX)
@router.post("/sell/{product_id}")
async def sell_product(product_id: int, request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    product = db.query(Product).get(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Получаем данные из тела запроса асинхронно
    body = await request.json()
    quantity = int(body.get("quantity", 1))  # Преобразуем количество в целое число

    if quantity < 1:
        raise HTTPException(status_code=400, detail="Некорректное количество")

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    # Увеличиваем количество проданных товаров
    product.sold_count += quantity

    # Получаем московское время
    moscow_tz = timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    
    # Создаем запись о продаже
    sale = Sale(
        product_id=product_id,
        username=user,
        quantity=quantity,
        sale_time=moscow_time  # Используем московское время
    )
    db.add(sale)
    db.commit()

    return {"status": "sold", "quantity_sold": quantity}

@router.get("/admin/sales")
def admin_panel(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    if user != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    # Получаем текущую дату
    today = date.today()

    # Получаем продажи за сегодня
    sales = (
        db.query(Sale, Product)
        .join(Product, Sale.product_id == Product.id)
        .filter(func.date(Sale.sale_time) == today)
        .all()
    )

    return templates.TemplateResponse("admin.html", {"request": request, "sales": sales})


# Маршрут для пользователя: отображение продаж только этого пользователя за сегодня
@router.get("/user/sales")
def get_user_sales(request: Request, db: Session = Depends(get_db), user: str = Depends(get_user_from_cookie)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sales = db.query(Sale).options(selectinload(Sale.product)).filter(Sale.sale_time >= today, Sale.username == user).all()
    return templates.TemplateResponse("sales.html", {"request": request, "sales": sales})