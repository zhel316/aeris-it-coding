from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.tracking import Tracking
from schemas.tracking import TrackingRead

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/", response_model=list[TrackingRead])
def get_tracking(
    assigned_tracking: Annotated[str | None, Query()] = None,
    logistics_company: Annotated[str | None, Query()] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Tracking)
    if assigned_tracking:
        q = q.filter(Tracking.assigned_tracking.ilike(f"%{assigned_tracking}%"))
    if logistics_company:
        q = q.filter(Tracking.logistics_company.ilike(f"%{logistics_company}%"))
    return q.all()
