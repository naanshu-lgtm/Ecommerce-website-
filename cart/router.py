from fastapi import APIRouter, HTTPException
from cart.model import AddToCartRequest, RemoveFromCartRequest
from cart import manager as cart_manager

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add", summary="Add a product to cart")
def add_to_cart(data: AddToCartRequest):
    """
    Add a product to the user's cart using their IDs.
    - **user_id**: ID returned at login (e.g. 1)
    - **product_id**: ID from the product listing (e.g. 3)
    - **quantity**: defaults to 1
    """
    try:
        return cart_manager.add_to_cart(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", summary="View user's cart")
def view_cart(user_id: int):
    """Return all cart items and grand total for the given user."""
    try:
        return cart_manager.get_cart(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/remove", summary="Remove an item from cart")
def remove_from_cart(data: RemoveFromCartRequest):
    """Remove a specific cart item by cart_id (ownership verified by user_id)."""
    try:
        return cart_manager.remove_from_cart(data.cart_id, data.user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
