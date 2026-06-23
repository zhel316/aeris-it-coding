# Aeris IT — Order Management System

Internal tool for warehouse staff to look up orders, SKUs, tracking records, product pricing, and live AusPost shipment status.

## Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Python · FastAPI · SQLAlchemy · SQLite |
| Frontend | Vue 3 · Vite · Vue Router |
| Shipping | AusPost Shipping API (StarTrack Express & Premium) |

---

## Project Structure

```
aeris-it-coding/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLite engine & session
│   ├── config.py               # All environment settings
│   ├── init.sql                # Seed data (run once after first start)
│   ├── data/
│   │   └── products.json       # Local product catalogue (RRP, names, etc.)
│   ├── models/                 # SQLAlchemy ORM models (order, sku, tracking)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── routes/                 # API route handlers
│   │   ├── orders.py           # GET /orders/
│   │   ├── sku.py              # GET /sku/
│   │   ├── tracking.py         # GET /tracking/
│   │   ├── invoice.py          # GET /invoice/{order_no}
│   │   └── auspost.py          # GET /auspost/shipments/{order_no}
│   └── services/
│       ├── product.py          # Product class — reads products.json, builds invoice
│       └── auspost.py          # AusPost API client
└── fronted/
    ├── src/
    │   ├── views/
    │   │   ├── OrderList.vue   # Page 1 — filterable order list
    │   │   └── OrderDetail.vue # Page 2 — order info, shipments, invoice
    │   ├── api/index.js        # Fetch wrappers for all backend endpoints
    │   └── router/index.js     # Vue Router (/ and /orders/:orderNo)
    └── vite.config.js          # Dev proxy: /api → http://localhost:8000
```

---

## How to Run

### Prerequisites

- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment (first time only)
python -m venv ../venv
source ../venv/bin/activate          # Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server (creates orders.db automatically on first run)
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

#### Seed the database (first time only)

After the server has started once (so tables exist), run:

```bash
sqlite3 orders.db < init.sql
```

### 2. Frontend

```bash
cd fronted
npm install          # first time only
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/orders/` | List orders with optional filters |
| GET | `/sku/` | List SKUs with optional filters |
| GET | `/tracking/` | List tracking records |
| GET | `/invoice/{order_no}` | Invoice with product details & live shipping cost |
| GET | `/auspost/shipments/{order_no}` | AusPost shipments for an order |

### Order filters

`/orders/?order_no=&status=&company_name=&customer_name=&date_from=&date_to=`

Status values: `completed` · `in-transit`

---

## Configuration

All settings live in `backend/config.py` and can be overridden with a `backend/.env` file.

| Setting | Default | Description |
|---------|---------|-------------|
| `product_api_url` | `https://tinyurl.com/2zp5p54a` | External product SQL API (unused — see below) |
| `auspost_api_key` | `8ba91b84-...` | AusPost API key |
| `auspost_password` | `kE1Rt1ualfjjL2ESLLB4` | AusPost API password |
| `auspost_account_number` | `04456017` | StarTrack test account |
| `auspost_base_url` | `https://digitalapi.auspost.com.au/test/shipping/v1` | AusPost testbed URL |

Example `backend/.env`:

```env
AUSPOST_API_KEY=your-real-key
AUSPOST_PASSWORD=your-real-password
AUSPOST_ACCOUNT_NUMBER=your-account
AUSPOST_BASE_URL=https://digitalapi.auspost.com.au/shipping/v1
```

---

## Modifications & Notes

### Product catalogue — local JSON instead of remote SQL API

The original design fetched product data (names, RRP) from a Google Apps Script SQL API (`product_api_url`). That endpoint requires Google account authentication and cannot be called server-to-server without credentials.

**Current approach:** product data is stored locally in `backend/data/products.json`.

To add or update products, edit `products.json` directly — no restart required; the file is reloaded on each server start. Each entry must include at minimum:

```json
{
  "SKU": "YOURSKU01",
  "ProductName": "Your Product Name",
  "RRP": "99.00"
}
```

To switch back to the remote API, update `services/product.py` to restore the `httpx` fetch logic and set `product_api_url` in `.env` to an accessible endpoint.

### Switching from AusPost testbed to production

1. Change `auspost_base_url` in `.env`:
   ```env
   AUSPOST_BASE_URL=https://digitalapi.auspost.com.au/shipping/v1
   ```
2. Replace `auspost_api_key`, `auspost_password`, and `auspost_account_number` with your production credentials.

### AusPost account numbers (testbed)

| Products | Test Account Number |
|----------|-------------------|
| StarTrack Express & Premium | `04456017` |
| Australia Post Domestic & International | `2004456017` |
| Same Day Services | `3004456017` |

### Known Limitations / Not Yet Implemented

- **TNT delivery status tracking** — Orders shipped via TNT (e.g. `assigned_tracking = Track 3`, logistics company = TNT) do not have live tracking status. The current tracking integration only covers StarTrack/AusPost consignments via the AusPost Shipping API (`GET /track`). TNT uses a separate tracking API that has not been integrated. TNT shipments will show no `tracking_status` or events in the Order Detail page.

### Invoice calculation

- **Line Total** = RRP × Qty  
- **Subtotal** = sum of all Line Totals  
- **GST** = Subtotal × 10% (RRP already includes GST; this is shown as a display component)  
- **Shipment Fee** = sum of `total_cost` from AusPost for all shipments under the order  
- **Total** = Subtotal + GST + Shipment Fee
