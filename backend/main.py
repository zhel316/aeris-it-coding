import models  # noqa: F401 — ensures all models are registered before create_all
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auspost_router, invoice_router, orders_router, sku_router, tracking_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ordering System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders_router)
app.include_router(sku_router)
app.include_router(tracking_router)
app.include_router(invoice_router)
app.include_router(auspost_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
