from ..dependencies import *

@router.get("/stuff/settings")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    return templates.TemplateResponse("stuff/settings.html", {"request": request,"user":user})
