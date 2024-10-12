from .dependencies import *

@router.get("/")
def get_categories(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    categories = db.query(Category).all()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    return templates.TemplateResponse("categories.html", {"request": request, "categories": categories, "user": user})

# Страница товаров для конкретной категории
@router.get("/category/{category_id}", response_class=HTMLResponse)
def get_products(request: Request, category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    products = db.query(Product).filter(Product.category_id == category_id).all()

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return templates.TemplateResponse("products.html", {"request": request, "products": products, "category": category})