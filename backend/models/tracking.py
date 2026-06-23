from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Tracking(Base):
    __tablename__ = "tracking"

    assigned_tracking: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    track_no: Mapped[str] = mapped_column(String, nullable=False)
    logistics_company: Mapped[str] = mapped_column(String, nullable=False)

    skus: Mapped[list["SKU"]] = relationship("SKU", back_populates="tracking")
