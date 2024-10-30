from ..dependencies import *

class InvoiceItemData(BaseModel):
    product_id: int
    quantity: int
    invoice_id: int

class CloseInvoiceData(BaseModel):
    pay_type: str


@router.get("/stuff/invoices")
def status(request: Request, db: Session = Depends(get_db), user: str = Cookie(None)):
    user = db.query(User).filter(User.username == user).first()
    if user.username == "admin":
        # invoices = db.query(Invoice).filter(func.date(Invoice.created_at) == date.today()).all()
        invoices = db.query(Invoice).all()
    else:
        invoices = db.query(Invoice).filter(func.date(Invoice.created_at) == date.today(), Invoice.user_id == user.id).all()
    return templates.TemplateResponse("stuff/invoices.html", 
                                      {"request": request,
                                       "user":user,
                                       "invoices": invoices})


@router.get("/stuff/invoice/{invoice_id}")
def get_invoice_details(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счет не найден")

    return {
        "id": invoice.id,
        "created_at": invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "user": {
            "first_name": invoice.user.first_name,
            "last_name": invoice.user.last_name
        },
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "id": item.product_id
            }
            for item in invoice.items
        ],
        "total_amount": invoice.total_amount,
        "status": invoice.status,
        "pay_type": invoice.pay_type
    }


@router.post("/stuff/create_invoice")
def create_invoice(invoice_request: InvoiceItemData, db: Session = Depends(get_db), user: str = Cookie(None)):
    # Получаем пользователя
    user_obj = db.query(User).filter(User.username == user).first()

    # Создаем новый счет
    new_invoice = Invoice(user_id=user_obj.id, total_amount=0, created_at = datetime.now(pytz.timezone('Europe/Moscow')))
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    if invoice_request.quantity != 0:
        # Добавляем товар в новый счет
        product = db.query(Product).filter(Product.id == invoice_request.product_id).first()
        invoice_item = InvoiceItem(invoice_id=new_invoice.id, product_id=product.id, quantity=invoice_request.quantity)
        db.add(invoice_item)

        # Пересчитываем общую сумму счета
        new_invoice.total_amount = invoice_item.quantity * product.price
        db.commit()

    return {"invoiceId": new_invoice.id}


@router.get("/stuff/select_invoice/{product_id}/{quantity}/{category_id}")
def select_invoice(request: Request, product_id: int, quantity: int, category_id: int, db: Session = Depends(get_db), user: str = Cookie(None)):
    user_obj = db.query(User).filter(User.username == user).first()
    # invoices = db.query(Invoice).filter(Invoice.user_id == user_obj.id).all()
    invoices = db.query(Invoice).filter(Invoice.status == "open").filter(Invoice.user_id == user_obj.id).all()
    return templates.TemplateResponse("/stuff/select_invoice.html", {
        "request": request,  # Передаем request в контексте
        "invoices": invoices, 
        "product_id": product_id, 
        "user": user_obj,
        "quantity": quantity, 
        "category_id": category_id
    })    

@router.post("/stuff/add_to_invoice")
def add_to_invoice(request: InvoiceItemData, db: Session = Depends(get_db)):
    # Получаем товар
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Добавляем товар к счету
    invoice_item = InvoiceItem(invoice_id=request.invoice_id, product_id=request.product_id, quantity=request.quantity)
    db.add(invoice_item)

    # Пересчитываем общую сумму счета
    invoice = db.query(Invoice).filter(Invoice.id == request.invoice_id).first()
    invoice.total_amount += invoice_item.quantity * product.price
    db.commit()

@router.post("/stuff/update_quantity")
def update_quantity(request: InvoiceItemData, db: Session = Depends(get_db)):
    print(f"Получены данные: product_id={request.product_id}, quantity={request.quantity}")
    item = db.query(InvoiceItem).filter(InvoiceItem.product_id == request.product_id).filter(InvoiceItem.invoice_id == request.invoice_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    item.quantity = request.quantity
    db.commit()
    # return {}

@router.post("/stuff/invoice/{invoice_id}/close/{pay_type}")
def close_invoice(invoice_id: int, pay_type: str, db: Session = Depends(get_db), user: str = Cookie(None)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счет не найден")
    
    user_obj = db.query(User).filter(User.username == user).first()
    invoice.closed_at = datetime.now(pytz.timezone('Europe/Moscow'))
    invoice.closed_by = user_obj.id
    invoice.status = "closed"
    invoice.pay_type = pay_type

    db.commit()
    return {"message": f"Счет закрыт ({pay_type})"}















