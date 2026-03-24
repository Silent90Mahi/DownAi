"""
Pagination Schemas
Generic pagination response model for all list endpoints
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model.

    Usage:
        from typing import List
        from app.schemas.pagination import PaginatedResponse
        from app.schemas.product import ProductResponse

        ProductList = PaginatedResponse[ProductResponse]

    In router:
        @router.get("/", response_model=PaginatedResponse[ProductResponse])
        async def get_products(page: int = 1, page_size: int = 20):
            ...
    """
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }


class PaginationParams(BaseModel):
    """
    Pagination query parameters.
    Use this as dependency in endpoints:
        pagination: PaginationParams = Depends()
    """
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page (max 100)")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20
            }
        }


def paginate(query, page: int, page_size: int):
    """
    Helper function to paginate SQLAlchemy queries.

    Usage:
        from app.schemas.pagination import paginate

        @router.get("/")
        async def get_items(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
            query = db.query(Item)
            total = query.count()
            items = paginate(query, page, page_size).all()

            return PaginatedResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
    """
    total = query.count()
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)
