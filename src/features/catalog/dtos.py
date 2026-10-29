from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from core.dtos import JsonDecimal
from features.catalog.models import StockStatus

# Categories
# Users cannot create or edit categories. Only the Refine admin panel does.

#Admin creates new category
class CategoryCreateRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9_-]+$")  # short name used in code
    name: str = Field(min_length=1, max_length=100)  # name shown in the UI
    is_active: bool = True

#Admin changes a category
class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None

#category that shown in UI and admin panel
class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    name: str
    is_active: bool



# Category criteria (admin only)


#admin adds a new criteria version for a category.
#We should never edit an old version, so old searches stay explainable.
class CategoryCriteriaCreateRequest(BaseModel):
    criteria_schema: dict[str, Any]
    prompt_template: str = Field(min_length=1)
    is_active: bool = True


#One version of the criteria of a category.
class CategoryCriteriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category_id: UUID
    version: int
    criteria_schema: dict[str, Any]
    prompt_template: str
    is_active: bool
    created_at: datetime



# Products

#A product as users see it (search results, favorites)
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source: str  # which site the product came from
    category_id: UUID | None = None
    title: str
    price: JsonDecimal | None = None
    currency: str
    url: str  # link to the product page
    image_url: str | None = None
    specs: dict[str, Any] | None = None  # cleaned specs - Ram
    stock_status: StockStatus
    scraped_at: datetime  #last fetch


#Product view for admins. raw crawler data so we can check parsing problems
class AdminProductResponse(ProductResponse):
    external_id: str
    content_hash: str | None = None
    raw_data: dict[str, Any] | None = None
    updated_at: datetime

#Admin fixes a product by hand when the crawler got something wrong
class ProductUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    category_id: UUID | None = None
    price: JsonDecimal | None = Field(default=None, ge=0)
    stock_status: StockStatus | None = None



# Favorites

class FavoriteCreateRequest(BaseModel):
    product_id: UUID


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    product: ProductResponse