from ..dependencies import *

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