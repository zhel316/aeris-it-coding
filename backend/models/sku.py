from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SKU(Base):
    __tablename__ = "sku"

    sku_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_tracking: Mapped[str | None] = mapped_column(
        String, ForeignKey("tracking.assigned_tracking"), nullable=True
    )
    order_no: Mapped[str] = mapped_column(
        String, ForeignKey("orders.order_no"), nullable=False
    )

    order: Mapped["Order"] = relationship("Order", back_populates="skus")
    tracking: Mapped["Tracking | None"] = relationship("Tracking", back_populates="skus")
