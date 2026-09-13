"""Pydantic request and response schemas for the FastAPI surface.

Keep schemas minimal for the Phase 5 skeleton. Add fields as needed when
implementing full business logic. Use type hints and validation where useful.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    id: str
    sku: str
    name: str
    description: Optional[str]
    unit_price: float
    quantity_available: int
    image_url: Optional[str]


class CustomerIn(BaseModel):
    full_name: str
    phone: Optional[str]
    # Avoid pydantic[email] extra dependency in tests by using plain str here.
    email: Optional[str]
    address_line1: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]


class OrderItemIn(BaseModel):
    product_id: str = Field(..., alias="product_id")
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer: CustomerIn
    items: List[OrderItemIn]
    payment_method: str = Field("COD", regex="^(COD|ONLINE)$")
    notes: Optional[str]


class OrderResponse(BaseModel):
    order_id: str
    order_status: str
    payment_status: str
    total_amount: float


class PaymentSessionCreate(BaseModel):
    order_id: str
    amount_cents: int


class PaymentSessionOut(BaseModel):
    session_id: str
    url: Optional[str]
    status: str


class InvoiceResponse(BaseModel):
    invoice_id: str
    status: str
    download_url: Optional[str]


class AdminLogin(BaseModel):
    username: str
    password: str
