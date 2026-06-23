import asyncio

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

# Maps raw AusPost tracking status → simplified display label
_STATUS_MAP = {
    "delivered in full": "Delivered",
    "item delivered": "Delivered",
    "delivered": "Delivered",
    "onboard for delivery": "Out for Delivery",
    "in transit": "In Transit",
    "item processed at sorting facility": "In Transit",
    "picked up": "Picked Up",
    "shipping information received by australia post": "Created",
    "created": "Created",
}


def _simplify_status(raw: str) -> str:
    key = (raw or "").lower()
    for k, v in _STATUS_MAP.items():
        if k in key:
            return v
    return raw or "Unknown"


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
        "status": summary.get("status", "Created"),
        "tracking_status": None,      # filled by _enrich_with_tracking
        "tracking_events": [],
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
                "status": i.get("item_summary", {}).get("status", "Created"),
                "tracking_status": None,
                "tracking_events": [],
                "weight": i.get("weight"),
                "packaging_type": i.get("packaging_type"),
            }
            for i in s.get("items", [])
        ],
    }


async def _fetch_tracking(client: httpx.AsyncClient, consignment_ids: list[str]) -> dict:
    """Returns {consignment_id: tracking_result_dict}."""
    if not consignment_ids:
        return {}
    try:
        resp = await client.get(
            "/track",
            params={"tracking_ids": ",".join(consignment_ids)},
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return {}

    result = {}
    for tr in data.get("tracking_results", []):
        tid = tr["tracking_id"]
        consignment = tr.get("consignment", {})
        result[tid] = {
            "status": consignment.get("status", ""),
            "events": consignment.get("events", []),
            "trackable_items": {
                ti["article_id"]: ti
                for ti in tr.get("trackable_items", [])
            },
        }
    return result


async def get_shipments(order_no: str) -> list[dict]:
    async with _client() as client:
        resp = await client.get("/shipments", params={"customer_reference_1": order_no})
        resp.raise_for_status()
        data = resp.json()

        shipments = [_format_shipment(s) for s in data.get("shipments", [])]

        # Collect unique consignment IDs
        consignment_ids = list({
            item["consignment_id"]
            for s in shipments
            for item in s["items"]
            if item.get("consignment_id")
        })

        tracking_map = await _fetch_tracking(client, consignment_ids)

    # Merge tracking data into shipments
    for s in shipments:
        seen_consignments: set[str] = set()
        all_events: list[dict] = []

        for item in s["items"]:
            cid = item.get("consignment_id")
            if not cid or cid not in tracking_map:
                continue

            tr = tracking_map[cid]

            # Consignment-level status → shipment tracking_status (use first seen)
            if cid not in seen_consignments:
                seen_consignments.add(cid)
                all_events.extend(tr["events"])

            # Article-level status
            article_data = tr["trackable_items"].get(item["article_id"], {})
            if article_data:
                item["tracking_status"] = _simplify_status(article_data.get("status", ""))
                item["tracking_events"] = article_data.get("events", [])

        if seen_consignments:
            # Derive shipment-level status from the richest consignment status
            raw_statuses = [tracking_map[c]["status"] for c in seen_consignments]
            s["tracking_status"] = _simplify_status(raw_statuses[0])
            # Sort events newest-first
            s["tracking_events"] = sorted(
                all_events, key=lambda e: e.get("date", ""), reverse=True
            )

    return shipments


async def get_total_shipping_cost(order_no: str) -> float:
    shipments = await get_shipments(order_no)
    return round(sum(s["total_cost"] for s in shipments), 2)
