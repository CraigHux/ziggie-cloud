"""
Pagination utilities for Control Center backend

Provides standardized pagination for list endpoints with support for:
- Offset-based pagination (simple and efficient for most use cases)
- Cursor-based pagination (for large datasets and real-time data)
- Metadata including total counts, next/previous links
- Configurable page sizes with sensible defaults
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from math import ceil

# Generic type for paginated items
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters for API requests"""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=50, ge=1, le=200, description="Items per page (max 200)")
    offset: Optional[int] = Field(default=None, ge=0, description="Alternative to page: start offset")

    @property
    def skip(self) -> int:
        """Calculate skip value for database query"""
        if self.offset is not None:
            return self.offset
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit value for database query"""
        return self.page_size


class CursorParams(BaseModel):
    """Cursor-based pagination parameters"""
    cursor: Optional[str] = Field(default=None, description="Cursor for next page")
    page_size: int = Field(default=50, ge=1, le=200, description="Items per page (max 200)")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")
    next_page: Optional[int] = Field(default=None, description="Next page number")
    prev_page: Optional[int] = Field(default=None, description="Previous page number")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated response"""
    items: List[T] = Field(description="List of items for current page")
    meta: PaginationMeta = Field(description="Pagination metadata")
    cached: bool = Field(default=False, description="Whether data is from cache")


class CursorMeta(BaseModel):
    """Cursor-based pagination metadata"""
    page_size: int = Field(description="Items per page")
    has_next: bool = Field(description="Whether there is a next page")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")


class CursorResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response"""
    items: List[T] = Field(description="List of items for current page")
    meta: CursorMeta = Field(description="Cursor pagination metadata")


def paginate_list(
    items: List[Any],
    params: PaginationParams,
    cached: bool = False
) -> Dict[str, Any]:
    """
    Paginate a list of items with standard metadata

    Args:
        items: Full list of items to paginate
        params: Pagination parameters
        cached: Whether the data is from cache

    Returns:
        Dictionary with paginated results and metadata
    """
    total = len(items)
    skip = params.skip
    limit = params.page_size

    # Calculate pagination metadata
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = params.page if params.offset is None else (skip // limit) + 1

    has_next = skip + limit < total
    has_prev = skip > 0

    next_page = current_page + 1 if has_next else None
    prev_page = current_page - 1 if has_prev and current_page > 1 else None

    # Slice items for current page
    paginated_items = items[skip:skip + limit]

    return {
        "items": paginated_items,
        "meta": {
            "total": total,
            "page": current_page,
            "page_size": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": next_page,
            "prev_page": prev_page
        },
        "cached": cached
    }


def create_pagination_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    cached: bool = False
) -> Dict[str, Any]:
    """
    Create pagination response from already-sliced items
    (for database queries that use LIMIT/OFFSET)

    Args:
        items: Items for current page (already sliced)
        total: Total count of items (from COUNT query)
        page: Current page number
        page_size: Items per page
        cached: Whether the data is from cache

    Returns:
        Dictionary with paginated results and metadata
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0

    has_next = page < total_pages
    has_prev = page > 1

    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None

    return {
        "items": items,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": next_page,
            "prev_page": prev_page
        },
        "cached": cached
    }


def create_cursor_response(
    items: List[Any],
    page_size: int,
    next_cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create cursor-based pagination response

    Args:
        items: Items for current page
        page_size: Items per page
        next_cursor: Cursor for next page (if exists)

    Returns:
        Dictionary with cursor-paginated results and metadata
    """
    has_next = next_cursor is not None

    return {
        "items": items,
        "meta": {
            "page_size": page_size,
            "has_next": has_next,
            "next_cursor": next_cursor
        }
    }


# Backward compatibility helpers
def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 50,
    total: Optional[int] = None
) -> Dict[str, Any]:
    """
    Simple pagination helper (backward compatible)

    Args:
        items: List of items (can be full list or pre-sliced)
        page: Page number
        page_size: Items per page
        total: Total count (if items are pre-sliced)

    Returns:
        Paginated response dictionary
    """
    if total is not None:
        # Pre-sliced items with known total
        return create_pagination_response(items, total, page, page_size)
    else:
        # Full list - slice it
        params = PaginationParams(page=page, page_size=page_size)
        return paginate_list(items, params)


# Query parameter helpers for FastAPI
def get_pagination_params(
    page: int = 1,
    page_size: int = 50,
    offset: Optional[int] = None
) -> PaginationParams:
    """
    Helper to create PaginationParams from query parameters

    Usage in FastAPI:
        @router.get("/items")
        async def list_items(
            page: int = Query(1, ge=1),
            page_size: int = Query(50, ge=1, le=200),
            offset: Optional[int] = Query(None, ge=0)
        ):
            params = get_pagination_params(page, page_size, offset)
            # ... use params
    """
    return PaginationParams(page=page, page_size=page_size, offset=offset)
