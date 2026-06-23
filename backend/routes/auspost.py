from fastapi import APIRouter, HTTPException

from services.auspost import get_shipments

router = APIRouter(prefix="/auspost", tags=["auspost"])


@router.get("/shipments/{order_no}")
async def list_shipments(order_no: str):
    try:
        shipments = await get_shipments(order_no)
        return {"order_no": order_no, "shipments": shipments}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AusPost API error: {exc}")
