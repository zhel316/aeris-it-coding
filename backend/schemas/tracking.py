from pydantic import BaseModel


class TrackingBase(BaseModel):
    assigned_tracking: str
    track_no: str
    logistics_company: str


class TrackingCreate(TrackingBase):
    pass


class TrackingRead(TrackingBase):
    model_config = {"from_attributes": True}
