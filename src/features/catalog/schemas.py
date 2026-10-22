from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.schemas import JsonDecimal
from features.catalog.models import StockStatus

#Should not be seen by users. User cannot create category.
#Only for admin panel Refine
class CategoryCreateRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    name: str
    is_active: bool



class CriteriaCreateRequest(BaseModel):
    criteria_schema: dict[str, Any]
    prompt_template: str = Field(min_length=1)
    is_active: bool = True


class CriteriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category_id: UUID
    version: int
    criteria_schema: dict[str, Any]
    prompt_template: str
    is_active: bool
    created_at: datetime

#For users:
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source: str
    category_id: UUID | None = None
    title: str
    price: JsonDecimal | None = None
    currency: str
    url: str
    image_url: str | None = None
    specs: dict[str, Any] | None = None
    stock_status: StockStatus
    scraped_at: datetime

#For admins: Admins should see crawls raw data
class AdminProductResponse(ProductResponse):
    external_id: str
    content_hash: str | None = None
    raw_data: dict[str, Any] | None = None
    updated_at: datetime

#Manuel correction by admin when needed
class ProductUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    category_id: UUID | None = None
    price: JsonDecimal | None = Field(default=None, ge=0)
    stock_status: StockStatus | None = None


class FavoriteCreateRequest(BaseModel):
    product_id: UUID
    #user id comes from Zitadel token


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    product: ProductResponse