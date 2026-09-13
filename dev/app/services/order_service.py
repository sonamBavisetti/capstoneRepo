"""Order service skeleton.

Implements the basic flow to persist an order and its items. This module is
intentionally minimal for Phase 5 and includes TODOs where business logic
(such as idempotency mapping, reservation checks, and transactional final
order confirmation) must be implemented.
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from decimal import Decimal
import logging

from sqlalchemy.orm import Session

from dev.app.models import Product, Customer, Order, OrderItem, Invoice
from dev.app.schemas import OrderCreate


def create_order(db: Session, order_in: OrderCreate, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
    """Create a new order (basic implementation).

    This function:
    - (1) performs basic validation
    - (2) creates or re-uses a Customer row
    - (3) creates an Order and corresponding OrderItem rows
    - (4) persists an Invoice record in status=PENDING

    Important TODOs (not implemented here fully):
    - Respect Idempotency-Key header by using a Redis mapping (key -> order_id)
      with a TTL (24h). If a key is seen again, return the original order
      response instead of creating a duplicate.
    - Reserve inventory using reservation tokens (Redis) before persisting the
      order, or perform SELECT ... FOR UPDATE transactional decrements when
      Redis is unavailable.
    - Implement robust money arithmetic using integers (cents) or Decimal and
      avoid floats in production.
    """
    if not order_in.items:
        raise ValueError("Order must contain at least one item")

    # NOTE: idempotency handling should be performed here. For Phase 5 this is
    # a stubbed comment; integrate with dev.app.services.reservation and a
    # Redis-backed idempotency store in TASK-07/TASK-08.
    if idempotency_key:
        logging.debug("Idempotency-Key provided (stub): %s", idempotency_key)

    # Create or fetch customer
    customer_data = order_in.customer
    customer = None
    if customer_data.email:
        customer = db.query(Customer).filter(Customer.email == customer_data.email).one_or_none()

    if not customer:
        customer = Customer(
            full_name=customer_data.full_name,
            phone=customer_data.phone,
            email=customer_data.email,
            address_line1=customer_data.address_line1,
            city=customer_data.city,
            state=customer_data.state,
            postal_code=customer_data.postal_code,
            country=customer_data.country,
        )
        db.add(customer)
        db.flush()  # assign id

    # Build order
    order = Order(
        customer_id=customer.id,
        payment_method=order_in.payment_method,
        payment_status="PENDING",
        order_status="PENDING",
        notes=order_in.notes,
    )
    db.add(order)
    db.flush()  # get order.id for FK relations

    subtotal = Decimal("0.00")

    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).one_or_none()
        if product is None:
            raise ValueError(f"Product not found: {item.product_id}")

        unit_price = Decimal(product.unit_price)
        line_total = unit_price * int(item.quantity)
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
            line_total=line_total,
        )
        db.add(oi)
        subtotal += line_total

    # TODO: shipping calculation, taxes, discounts
    order.subtotal = subtotal
    order.shipping_charges = Decimal("0.00")
    order.total_amount = subtotal + order.shipping_charges

    # Create an invoice placeholder. The asynchronous worker will generate the
    # PDF and update this invoice record (status -> READY|FAILED).
    invoice = Invoice(order_id=order.id, status="PENDING")
    db.add(invoice)

    db.commit()

    # TODO: record idempotency mapping in Redis here

    return {
        "order_id": order.id,
        "order_status": order.order_status,
        "payment_status": order.payment_status,
        "total_amount": float(order.total_amount),
    }
