"""FastAPI application entrypoint for Vinayaka File Works (Phase 5 skeleton).

Run with (example):
    uvicorn dev.app.main:app --reload --host 0.0.0.0 --port 8000

Environment variables used:
- DATABASE_URL (optional; default sqlite:///dev.db)
- REDIS_URL (optional)
- SECRET_KEY (required by dev.config)
- STORAGE_PATH (optional; local fallback for generated PDFs)
- STRIPE_API_KEY / STRIPE_WEBHOOK_SECRET (optional for payment adapter)
"""
from __future__ import annotations

from typing import List, Optional
import os
import logging

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from dev.app import db as app_db
from dev.app import schemas
from dev.app.services import order_service, payment_adapter, pdf_worker
from dev.app.models import Product, Order, Invoice


app = FastAPI(title="Vinayaka File Works API - Phase 5")
logger = logging.getLogger(__name__)


@app.get("/api/products", response_model=List[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 50, db=Depends(app_db.get_db)) -> List[schemas.ProductOut]:
    """Return a paginated list of products.

    This is intentionally simple for Phase 5. Add caching (Redis) and image
    signed URLs in TASK-06/TASK-05.
    """
    rows = db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    result = []
    for r in rows:
        result.append(
            schemas.ProductOut(
                id=r.id,
                sku=r.sku,
                name=r.name,
                description=r.description,
                unit_price=float(r.unit_price),
                quantity_available=r.quantity_available,
                image_url=r.image_url,
            )
        )
    return result


@app.get("/api/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: str, db=Depends(app_db.get_db)) -> schemas.ProductOut:
    p = db.query(Product).filter(Product.id == product_id).one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return schemas.ProductOut(
        id=p.id,
        sku=p.sku,
        name=p.name,
        description=p.description,
        unit_price=float(p.unit_price),
        quantity_available=p.quantity_available,
        image_url=p.image_url,
    )


@app.post("/api/orders", response_model=schemas.OrderResponse)
def create_order(order_in: schemas.OrderCreate, db=Depends(app_db.get_db), idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")) -> schemas.OrderResponse:
    try:
        out = order_service.create_order(db, order_in, idempotency_key=idempotency_key)
        return schemas.OrderResponse(
            order_id=out["order_id"],
            order_status=out["order_status"],
            payment_status=out["payment_status"],
            total_amount=out["total_amount"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error creating order")
        raise HTTPException(status_code=500, detail="internal error")


@app.get("/api/orders/{order_id}")
def get_order(order_id: str, db=Depends(app_db.get_db)):
    o = db.query(Order).filter(Order.id == order_id).one_or_none()
    if o is None:
        raise HTTPException(status_code=404, detail="Order not found")
    # Minimal order representation
    return {
        "order_id": o.id,
        "order_status": o.order_status,
        "payment_status": o.payment_status,
        "total_amount": float(o.total_amount),
    }


@app.get("/api/orders/{order_id}/invoice", response_model=schemas.InvoiceResponse)
def get_invoice(order_id: str, db=Depends(app_db.get_db)) -> schemas.InvoiceResponse:
    inv = db.query(Invoice).filter(Invoice.order_id == order_id).one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    download_url = None
    # Accept either uppercase or lowercase stored status values by normalizing.
    if (inv.status or "").upper() == "READY" and inv.pdf_path:
        # Local file fallback. In production this should return a signed S3 URL.
        download_url = f"file://{inv.pdf_path}"

    return schemas.InvoiceResponse(invoice_id=inv.id, status=inv.status, download_url=download_url)


@app.post("/api/payments/create-session", response_model=schemas.PaymentSessionOut)
def create_payment_session(payload: schemas.PaymentSessionCreate, request: Request) -> schemas.PaymentSessionOut:
    # Use a payment adapter. For Phase 5 we return a stubbed session.
    adapter = payment_adapter.StripeAdapter()
    session_info = adapter.create_session(amount_cents=payload.amount_cents, metadata={"order_id": payload.order_id})
    return schemas.PaymentSessionOut(session_id=session_info.get("session_id"), url=session_info.get("url"), status=session_info.get("status", "stubbed"))


@app.post("/api/payments/webhook")
async def payments_webhook(request: Request, sig_header: Optional[str] = Header(None, alias="Stripe-Signature")):
    """Webhook handler for payment provider events.

    Read the raw request body correctly in an async FastAPI handler and pass
    it to the payment adapter for verification. The current adapter is a
    stub and returns a minimal event structure; signature verification is a
    TODO for TASK-08.
    """
    raw_body = await request.body()

    adapter = payment_adapter.StripeAdapter()
    # TODO: implement proper signature verification using adapter and fail fast
    event = adapter.verify_webhook(raw_body, sig_header or "")

    # Minimal stub handling
    etype = event.get("type")
    if etype == "payment_intent.succeeded":
        # TODO: map event to order and mark paid, enqueue invoice generation
        return JSONResponse({"status": "ok"})

    return JSONResponse({"status": "unhandled"})


# Admin endpoints (skeleton)
@app.post("/api/admin/login")
def admin_login(credentials: schemas.AdminLogin):
    # TODO: verify credentials using dev.app.auth and create a server-side session
    # For Phase 5 this is a stub that always succeeds for non-empty credentials.
    if not credentials.username or not credentials.password:
        raise HTTPException(status_code=400, detail="missing credentials")
    return {"status": "ok", "message": "login endpoint is a stub in Phase 5"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("dev.app.main:app", host="0.0.0.0", port=port, reload=True)
