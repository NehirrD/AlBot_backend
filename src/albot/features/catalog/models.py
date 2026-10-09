"""categories, category_criteria, products, favorites"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from albot.core.database import Base

class StockStatus(str, enum.Enum):
    IN_STOCK="in_stock"
    OUT_OF_STOCK="out_of_stock"
    UNKNOWN="unknown"

class Category(Base):
    __tablename__="categories"
    id:Mapped[uuid.UUID]=mapped_column( UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    slug: Mapped[str]=mapped_column(String, unique=True, nullable=False)
    name=Mapped[str]=mapped_column(String,nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean,server_default=text("true"),nullable=False)

class CategoryCriteria(Base):
    __tablename__="category_criteria"
    __table_args__=(UniqueConstraint("category_id","version"))

    id:Mapped[uuid.UUID]=mapped_column( UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    category_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("categories.id"),nullable=False)
    version: Mapped[int]=mapped_column(Integer, server_default=text("1"),nullable=False)
    criteria_schema: Mapped[dict]=mapped_column(JSONB,nullable=False)
    prompt_template: Mapped[str]=mapped_column(Text,nullable=False)
    is_active=Mapped[bool]=mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)

class Product(Base):
    __tablename__="products"
    __table_args__ = (
        UniqueConstraint("source", "external_id"),
        Index("ix_products_category_price", "category_id", "price"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    source:Mapped[str]=mapped_column(String,nullable=False)
    external_id:Mapped[str]=mapped_column(String,nullable=False)
    category_id:Mapped[uuid.UUID | None]=mapped_column(ForeignKey("categories.id"))
    title: Mapped[str]=mapped_column(String,nullable=False)
    price:Mapped[Decimal]=mapped_column(Numeric(12,2))
    currency:Mapped[str]=mapped_column(String,server_default=text("'TRY'"), nullable=False)
    url:Mapped[str]=mapped_column(Text,nullable=False)
    image_url:Mapped[str | None]=mapped_column(Text)
    specs:Mapped[dict | None]= mapped_column(JSONB)
    raw_data:Mapped[dict]=mapped_column(JSONB)
    stock_status: Mapped[StockStatus]=mapped_column(Enum(
        StockStatus,
        name="stock_status",
        values_callable=lambda e: [m.value for m in e],
    ),
    server_default="unknown", nullable=False)
    content_hash: Mapped[str|None]=mapped_column(String)
    scraped_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Favorite(Base):
    __tablename__="favorites"
    __table_args__ = (UniqueConstraint("user_id", "product_id"))
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True, server_default=text("gen_random_uuid()"))
    user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("users.id"),nullable=False)
    prooduct_id:Mapped[uuid.UUID]=mapped_column(ForeignKey("products.id"),nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)
















