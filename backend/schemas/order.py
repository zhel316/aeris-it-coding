from datetime import date

from pydantic import BaseModel, EmailStr

from models.order import OrderStatus


class OrderBase(BaseModel):
    order_no: str
    order_data: date
    status: OrderStatus
    company_name: str
    customer_name: str
    phone: str
    email: EmailStr
    address: str


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    model_config = {"from_attributes": True}
