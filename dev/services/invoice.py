from typing import Optional
import os

from dev.db import SessionLocal
from dev.models import Invoice, Order
from dev.storage.local import LocalStorage

STORAGE = LocalStorage(base_path=os.path.join(os.getcwd(), 'storage'))


def generate_invoice(order_id: str) -> Optional[str]:
    """Generate a minimal invoice artifact for the given order."""
    with SessionLocal() as session:
        order = session.get(Order, order_id)
        if not order:
            return None

        inv = session.query(Invoice).filter_by(order_id=order_id).first()
        if not inv:
            inv = Invoice(order_id=order_id, status='PENDING')
            session.add(inv)

        content = f"Invoice for order {order_id}\nTotal: {order.total_amount}\n"
        filename = f"invoice_{order_id}.txt"
        path = STORAGE.save(filename, content.encode('utf-8'))
        inv.pdf_path = path
        # Use canonical uppercase status values to match other parts of the
        # codebase (e.g. dev.app.services.pdf_worker and dev.app.main).
        inv.status = 'READY'
        session.commit()
        return path
