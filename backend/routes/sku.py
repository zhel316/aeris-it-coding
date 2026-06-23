from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.sku import SKU
from schemas.sku import SKURead

router = APIRouter(prefix="/sku", tags=["sku"])


@router.get("/", response_model=list[SKURead])
def get_skus(
    sku_id: Annotated[str | None, Query()] = None,
    order_no: Annotated[str | None, Query()] = None,
    assigned_tracking: Annotated[str | None, Query()] = None,
    db: Session = Depends(get_db),
):
    q = db.query(SKU)
    if sku_id:
        q = q.filter(SKU.sku_id.ilike(f"%{sku_id}%"))
    if order_no:
        q = q.filter(SKU.order_no == order_no)
    if assigned_tracking:
        q = q.filter(SKU.assigned_tracking == assigned_tracking)
    return q.all()
