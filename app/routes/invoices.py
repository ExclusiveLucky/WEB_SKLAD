from .dependencies import *

@router.get("/invoices")
def view_invoices(request: Request, product_id: int = None, quantity: int = None, product_name: str = None, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()

    return templates.TemplateResponse("invoices.html", {
        "request": request,
        "invoices": invoices,
        "product_id": product_id,
        "quantity": quantity,
        "product_name": product_name
    })


@router.get("/select_invoice/{product_id}/{quantity}/{category_id}")
def select_invoice(request: Request, product_id: int, quantity: int, category_id: int, db: Session = Depends(get_db), user: str = Cookie(None)):
    user_obj = db.query(User).filter(User.username == user).first()
    invoices = db.query(Invoice).filter(Invoice.user_id == user_obj.id).all()
    return templates.TemplateResponse("select_invoice.html", {
        "request": request,  # Передаем request в контексте
        "invoices": invoices, 
        "product_id": product_id, 
        "quantity": quantity, 
        "category_id": category_id
    })

class InvoiceItemCreate(BaseModel):
    product_id: int
    quantity: int

@router.post("/add_to_invoice/{invoice_id}")
def add_to_invoice(request: Request, invoice_id: int, item: InvoiceItemCreate, db: Session = Depends(get_db)):
    # Получаем товар
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Добавляем товар к счету
    invoice_item = InvoiceItem(invoice_id=invoice_id, product_id=item.product_id, quantity=item.quantity)
    db.add(invoice_item)

    # Пересчитываем общую сумму счета
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    invoice.total_amount += invoice_item.quantity * product.price
    db.commit()

class InvoiceCreateRequest(BaseModel):
    product_id: int
    quantity: int

@router.post("/create_invoice")
def create_invoice(invoice_request: InvoiceCreateRequest, db: Session = Depends(get_db), user: str = Cookie(None)):
    # Получаем пользователя
    user_obj = db.query(User).filter(User.username == user).first()

    # Создаем новый счет
    new_invoice = Invoice(user_id=user_obj.id, total_amount=0)
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    # Добавляем товар в новый счет
    product = db.query(Product).filter(Product.id == invoice_request.product_id).first()
    invoice_item = InvoiceItem(invoice_id=new_invoice.id, product_id=product.id, quantity=invoice_request.quantity)
    db.add(invoice_item)

    # Пересчитываем общую сумму счета
    new_invoice.total_amount = invoice_item.quantity * product.price
    db.commit()

@router.get("/invoice/{invoice_id}")
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
                "price": item.product.price
            }
            for item in invoice.items
        ],
        "total_amount": invoice.total_amount
    }