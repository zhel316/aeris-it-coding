import httpx

from config import settings

_PRODUCT_NAMES = {
    "EXP": "StarTrack Express",
    "PRM": "StarTrack Premium",
    "RET": "Express Tail-Lift",
    "RE2": "Express Tail-Lift 2 Man",
    "FPP": "Fixed Price Premium",
    "FPA": "Fixed Price Airlock",
    "ARL": "Airlock",
}


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.auspost_base_url,
        auth=(settings.auspost_api_key, settings.auspost_password),
        headers={
            "account-number": settings.auspost_account_number,
            "Content-Type": "application/json",
        },
        timeout=15,
    )


def _format_shipment(s: dict) -> dict:
    summary = s.get("shipment_summary", {})
    return {
        "shipment_id": s.get("shipment_id"),
        "shipment_reference": s.get("shipment_reference"),
        "customer_reference": s.get("customer_reference_1"),
        "status": summary.get("status"),
        "total_cost": summary.get("total_cost", 0.0),
        "total_cost_ex_gst": summary.get("total_cost_ex_gst", 0.0),
        "total_gst": summary.get("total_gst", 0.0),
        "number_of_items": summary.get("number_of_items", 0),
        "created": s.get("shipment_creation_date"),
        "items": [
            {
                "article_id": i.get("tracking_details", {}).get("article_id"),
                "consignment_id": i.get("tracking_details", {}).get("consignment_id"),
                "product_id": i.get("product_id"),
                "product_name": _PRODUCT_NAMES.get(i.get("product_id", ""), i.get("product_id", "")),
                "status": i.get("item_summary", {}).get("status"),
                "weight": i.get("weight"),
                "packaging_type": i.get("packaging_type"),
            }
            for i in s.get("items", [])
        ],
    }


async def get_shipments(order_no: str) -> list[dict]:
    async with _client() as client:
        resp = await client.get("/shipments", params={"customer_reference_1": order_no})
        resp.raise_for_status()
        data = resp.json()
    return [_format_shipment(s) for s in data.get("shipments", [])]


async def get_total_shipping_cost(order_no: str) -> float:
    shipments = await get_shipments(order_no)
    return round(sum(s["total_cost"] for s in shipments), 2)
