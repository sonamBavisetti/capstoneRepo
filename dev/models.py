from __future__ import annotations
"""Data models for Vinayaka File Works (SQLAlchemy declarative models).
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from dev.db import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    sku = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    image_url = Column(String(1024))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(32))
    email = Column(String(255))
    address_line1 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(2))
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(64), unique=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(32))  # COD / ONLINE
    payment_status = Column(String(32), default="PENDING")
    order_status = Column(String(32), default="PENDING")
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    shipping_charges = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    notes = Column(Text)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    invoice_number = Column(String(64), unique=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    pdf_path = Column(String(1024))
    status = Column(String(32), default="PENDING")

    order = relationship("Order", back_populates="invoice")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    last_login = Column(DateTime)
