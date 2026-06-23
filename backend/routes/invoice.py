from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.sku import SKU
from services.auspost import get_total_shipping_cost
from services.product import build_invoice

router = APIRouter(prefix="/invoice", tags=["invoice"])


@router.get("/{order_no}")
async def get_invoice(order_no: str, db: Session = Depends(get_db)):
    skus = db.query(SKU).filter(SKU.order_no == order_no).all()
    if not skus:
        raise HTTPException(status_code=404, detail=f"No SKUs found for order {order_no}")

    shipment_fee = await get_total_shipping_cost(order_no)
    data = build_invoice([(s.sku_id, s.qty) for s in skus], shipment_fee=shipment_fee)
    return {"order_no": order_no, **data}
