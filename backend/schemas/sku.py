from pydantic import BaseModel


class SKUBase(BaseModel):
    sku_id: str
    qty: int
    assigned_tracking: str | None = None
    order_no: str


class SKUCreate(SKUBase):
    pass


class SKURead(SKUBase):
    model_config = {"from_attributes": True}
