from .dependencies import *

@router.get("/site/menu")
def menu(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    category = db.query(Category).all()
    return templates.TemplateResponse("site_menu.html", {"request": request,"category":category})