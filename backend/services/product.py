import json
from pathlib import Path

_DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"
_PLACEHOLDER = "https://placehold.co/72x72/dbeafe/1d4ed8"

# Load once at import time; keyed by SKU for O(1) lookup
_CATALOGUE: dict[str, dict] = {}

def _load() -> None:
    rows: list[dict] = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    for row in rows:
        _CATALOGUE[row["SKU"]] = row

_load()


class Product:
    def __init__(self, sku_id: str, qty: int):
        self.sku_id = sku_id
        self.qty = qty
        self._data: dict | None = _CATALOGUE.get(sku_id)

    @property
    def product_name(self) -> str:
        return (self._data or {}).get("ProductName") or self.sku_id

    @property
    def rrp(self) -> float:
        val = (self._data or {}).get("RRP")
        try:
            return float(val) if val is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

    @property
    def line_total(self) -> float:
        return round(self.rrp * self.qty, 2)

    @property
    def image_url(self) -> str:
        return f"{_PLACEHOLDER}?text={self.sku_id[:8]}"

    def to_dict(self) -> dict:
        return {
            "sku_id": self.sku_id,
            "qty": self.qty,
            "product_name": self.product_name,
            "rrp": self.rrp,
            "line_total": self.line_total,
            "image_url": self.image_url,
        }


def build_invoice(
    sku_qty_pairs: list[tuple[str, int]],
    shipment_fee: float = 0.0,
) -> dict:
    products = [Product(sku, qty) for sku, qty in sku_qty_pairs]
    subtotal = round(sum(p.line_total for p in products), 2)
    gst = round(subtotal * 0.10, 2)
    total = round(subtotal + shipment_fee, 2)

    return {
        "items": [p.to_dict() for p in products],
        "subtotal": subtotal,
        "gst": gst,
        "shipment_fee": shipment_fee,
        "total": total,
    }
