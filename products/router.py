from fastapi import APIRouter, HTTPException, Query
from products import manager as product_manager

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", summary="List all products")
def list_products():
    """Fetch the complete product catalogue."""
    return product_manager.get_all_products()


@router.get("/search", summary="Search products by name or description")
def search_products(q: str = Query(..., min_length=1, description="Search keyword e.g. 'ip'")):
    """
    Partial, case-insensitive search.
    - `?q=ip` → returns iPhone, iPad …
    - `?q=head` → returns Headphones …
    """
    results = product_manager.search_products(q)
    if not results:
        return {"message": f"No products found matching '{q}'", "results": []}
    return {"results": results, "count": len(results)}


@router.get("/{product_id}", summary="Get a product by ID")
def get_product(product_id: int):
    """Return a single product by its numeric ID (1, 2, 3 …)."""
    product = product_manager.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id={product_id} not found")
    return product
