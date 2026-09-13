"""Background PDF worker (skeleton).

This module exposes a helper used by background workers to generate invoice
PDFs. By default it will write to a local `storage/invoices/` folder. In
production the storage adapter should write to S3 and return a signed URL.

TODOs:
- Replace local file storage with the pluggable storage adapter (dev/app/storage)
- Integrate with RQ/Celery worker process and retry/DLQ semantics
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

from sqlalchemy.orm import Session

from dev.app.db import SessionLocal
from dev.app.models import Invoice, Order

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")


def _ensure_storage_path() -> Path:
    p = Path(STORAGE_PATH) / "invoices"
    p.mkdir(parents=True, exist_ok=True)
    return p


def generate_invoice_pdf(invoice_id: str, db: Optional[Session] = None) -> Optional[str]:
    """Generate a simple invoice PDF for the given invoice record.

    Returns the path to the generated PDF (local filesystem) or None on
    failure. The function updates the Invoice.pdf_path and status when done.
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).one_or_none()
        if inv is None:
            raise ValueError(f"Invoice not found: {invoice_id}")

        order = db.query(Order).filter(Order.id == inv.order_id).one_or_none()
        if order is None:
            raise ValueError(f"Order not found for invoice: {invoice_id}")

        storage_dir = _ensure_storage_path()
        filename = f"invoice_{invoice_id}.pdf"
        full_path = storage_dir / filename

        # Simple deterministic PDF content for Phase 5
        c = canvas.Canvas(str(full_path), pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(40, 800, f"Vinayaka File Works - Invoice")
        c.drawString(40, 785, f"Invoice ID: {inv.id}")
        c.drawString(40, 770, f"Order ID: {order.id}")
        c.drawString(40, 755, f"Generated: {datetime.utcnow().isoformat()}")
        c.drawString(40, 720, f"Total: {order.total_amount}")
        c.showPage()
        c.save()

        inv.pdf_path = str(full_path)
        inv.status = "READY"
        inv.generated_at = datetime.utcnow()
        db.add(inv)
        db.commit()

        return str(full_path)
    except Exception:
        if db is not None:
            try:
                inv = db.query(Invoice).filter(Invoice.id == invoice_id).one_or_none()
                if inv:
                    inv.status = "FAILED"
                    db.add(inv)
                    db.commit()
            except Exception:
                pass
        raise
    finally:
        if own_session:
            db.close()
