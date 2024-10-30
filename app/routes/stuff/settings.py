from ..dependencies import *

@router.get("/stuff/settings")
def settings(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    if user.username == "admin":
        return templates.TemplateResponse("stuff/admin/settings.html", {"request": request,"user":user})


model = {
    "products":Product,
    "categories":Category,
    "invoices":Invoice,
    "weekly_tasks":WeeklyTask

}

set = {
    "products":{
        "name":"Название", 
        "price":0.0, 
        "category_id":1, 
        "sold_count":0, 
        "image_url":""
    },
    "categories":{
        "name":"Название", 
        "icon_url":""
    },
    "invoices":{
        "user_id":1, 
        "total_amount":0, 
        "status":"open"
    },
    "weekly_tasks":{
        "day":1, 
        "description":"", 
        "level":1
    }
}


@router.get("/stuff/admin/settings/{table}")
def get(table: str, db: Session = Depends(get_db)):
    return db.query(model[table]).all()

@router.post("/stuff/admin/settings/{table}")
def add(table: str, db: Session = Depends(get_db)):
    new_product = model[table](**set[table])
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.patch("/stuff/admin/settings/{table}/{product_id}")
async def update(table: str, product_id: int, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    product = db.query(model[table]).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    setattr(product, data["field"], data["value"])
    db.commit()
    db.refresh(product)
    return product

@router.delete("/stuff/admin/settings/{table}/{product_id}")
def delete(table: str, product_id: int, db: Session = Depends(get_db)):
    product = db.query(model[table]).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "success"}

