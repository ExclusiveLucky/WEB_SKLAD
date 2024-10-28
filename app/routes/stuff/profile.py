from ..dependencies import *
from fastapi import Query
@router.get("/stuff/profile")
def profile(
    request: Request, 
    db: Session = Depends(get_db), 
    user: str = Cookie(None),
    period: str = Query("day")
):
    user = db.query(User).filter(User.username == user).first()
    if user.username == "admin":
        start_date = None
        if period == "day":
            start_date = datetime.now() - timedelta(days=1)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)

        # Продажи и выручка по товарам
        product_sales = [
            {"name": item[0], "sold_count": item[1]}
            for item in db.query(Product.name, func.sum(InvoiceItem.quantity).label("sold_count"))
                .join(InvoiceItem, Product.id == InvoiceItem.product_id)
                .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
                .filter(Invoice.created_at >= start_date if start_date else True)
                .group_by(Product.name)
                .all()
        ]
        
        product_revenue = [
            {"name": item[0], "total_revenue": item[1]}
            for item in db.query(Product.name, func.sum(InvoiceItem.quantity * Product.price).label("total_revenue"))
                .join(InvoiceItem, Product.id == InvoiceItem.product_id)
                .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
                .filter(Invoice.created_at >= start_date if start_date else True)
                .group_by(Product.name)
                .all()
        ]

        # Выручка по сотрудникам
        employee_revenue = []
        if period in ["month", "all"]:
            employee_revenue = [
                {"first_name": emp[0], "last_name": emp[1], "total_revenue": emp[2]}
                for emp in db.query(User.first_name, User.last_name, func.sum(InvoiceItem.quantity * Product.price).label("total_revenue"))
                    .join(Invoice, Invoice.user_id == User.id)
                    .join(InvoiceItem, InvoiceItem.invoice_id == Invoice.id)
                    .join(Product, InvoiceItem.product_id == Product.id)
                    .filter(Invoice.created_at >= start_date if start_date else True)
                    .group_by(User.id)
                    .all()
            ]

        # Средний чек по сотрудникам
        average_check = [
            {"first_name": emp[0], "last_name": emp[1], "average_check": emp[2] / emp[3] if emp[3] else 0}
            for emp in db.query(User.first_name, User.last_name, func.sum(Invoice.total_amount).label("total_revenue"), func.count(Invoice.id).label("invoice_count"))
                .join(Invoice, Invoice.user_id == User.id)
                .filter(Invoice.created_at >= start_date if start_date else True)
                .group_by(User.id)
                .all()
        ]

        # Частота продаж по времени
        sales_frequency = [
            {"hour": sale[0], "count": sale[1]}
            for sale in db.query(func.extract('hour', Invoice.created_at).label("hour"), func.count(Invoice.id))
                .filter(Invoice.created_at >= start_date if start_date else True)
                .group_by(func.extract('hour', Invoice.created_at))
                .order_by("hour")
                .all()
        ]

        # Популярность категорий
        category_popularity = [
            {"category_name": category[0], "sales": category[1]}
            for category in db.query(Category.name, func.sum(InvoiceItem.quantity))
                .join(Product, Product.category_id == Category.id)
                .join(InvoiceItem, InvoiceItem.product_id == Product.id)
                .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
                .filter(Invoice.created_at >= start_date if start_date else True)
                .group_by(Category.name)
                .all()
        ]

        total_revenue = sum(item["total_revenue"] for item in product_revenue)

        return templates.TemplateResponse(
            "stuff/admin_profile.html", 
            {
                "request": request,
                "user": user,
                "product_sales": product_sales,
                "product_revenue": product_revenue,
                "employee_revenue": employee_revenue,
                "average_check": average_check,
                "sales_frequency": sales_frequency,
                "category_popularity": category_popularity,
                "total_revenue": total_revenue,
                "period": period
            }
        )
        
    else:
        # Текущая дата и время
        today = datetime.utcnow().date()
        start_of_month = today.replace(day=1)

        # Время работы за сегодня
        today_shifts = db.query(WorkShift).filter(
            WorkShift.user_id == user.id,
            WorkShift.start_time >= today,
            WorkShift.start_time < today + timedelta(days=1),
        ).all()

        # Время работы за месяц
        month_shifts = db.query(WorkShift).filter(
            WorkShift.user_id == user.id,
            WorkShift.start_time >= start_of_month,
            WorkShift.start_time < today + timedelta(days=1),
        ).all()

        # Количество чеков за месяц
        month_invoices = db.query(Invoice).filter(
            Invoice.user_id == user.id,
            Invoice.created_at >= start_of_month,
            Invoice.created_at < today + timedelta(days=1),
            Invoice.status == "closed"
        ).count()

        today_hours, today_minutes, today_earnings = calculate_time_and_earnings(today_shifts)
        month_hours, month_minutes, month_earnings = calculate_time_and_earnings(month_shifts)

        context = {
            "request": request,
            "user": user,
            "today_hours": int(today_hours),
            "today_minutes": int(today_minutes),
            "today_earnings": int(today_earnings),
            "month_hours": int(month_hours),
            "month_minutes": int(month_minutes),
            "month_earnings": int(month_earnings),
            "month_invoices": month_invoices,
        }
        return templates.TemplateResponse("stuff/profile.html", context)