from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from schemas.order import OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[OrderRead])
def get_orders(
    order_no: Annotated[str | None, Query()] = None,
    status: Annotated[OrderStatus | None, Query()] = None,
    company_name: Annotated[str | None, Query()] = None,
    customer_name: Annotated[str | None, Query()] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if order_no:
        q = q.filter(Order.order_no.ilike(f"%{order_no}%"))
    if status:
        q = q.filter(Order.status == status)
    if company_name:
        q = q.filter(Order.company_name.ilike(f"%{company_name}%"))
    if customer_name:
        q = q.filter(Order.customer_name.ilike(f"%{customer_name}%"))
    if date_from:
        q = q.filter(Order.order_data >= date_from)
    if date_to:
        q = q.filter(Order.order_data <= date_to)
    return q.all()
