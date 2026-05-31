from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from admin.model import (
    AdminLoginRequest, AdminCreateRequest,
    ProductCreateRequest, ProductUpdateRequest,
    RestockRequest, UpdatePaymentStatusRequest,
)
from admin import manager as admin_manager

router = APIRouter(prefix="/admin", tags=["Admin"])


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/login", summary="Admin login")
def admin_login(data: AdminLoginRequest):
    """
    Authenticate as an admin.
    Default credentials (change after first run):
    - **email**: admin@ecommerce.com
    - **password**: admin123
    """
    try:
        return admin_manager.admin_login(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/create", summary="Create a new admin account")
def create_admin(data: AdminCreateRequest):
    """
    Create a new admin or superadmin account.
    In production this route should be protected by a superadmin auth header.
    """
    try:
        return admin_manager.create_admin(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/dashboard", summary="Business overview & KPIs")
def dashboard():
    """
    Returns:
    - Total users, products, confirmed orders, revenue
    - ⚠️  Low-stock alerts (stock < 10)
    - 5 most recent orders
    """
    return admin_manager.get_dashboard_stats()


# ══════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/users", summary="List all registered users")
def list_users():
    """Return id, name and email of every registered customer."""
    return {"users": admin_manager.get_all_users()}


@router.get("/users/{user_id}", summary="Full profile of a specific user")
def user_detail(user_id: int):
    """
    Returns:
    - Basic info (name, email)
    - Full order history with totals
    - Items currently in their cart
    - Total amount spent
    """
    try:
        return admin_manager.get_user_detail(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}", summary="Delete a user account")
def delete_user(user_id: int):
    """
    Permanently deletes the user and all their cart items and payment records.
    Use with caution.
    """
    try:
        return admin_manager.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/products", summary="Add a new product")
def add_product(data: ProductCreateRequest):
    """Add a brand-new product to the catalogue."""
    try:
        return admin_manager.add_product(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/products/{product_id}", summary="Update product details")
def update_product(product_id: int, data: ProductUpdateRequest):
    """
    Partially update a product — only pass the fields you want to change.
    E.g. send only `price` to update the price without touching name/stock.
    """
    try:
        return admin_manager.update_product(product_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/products/restock", summary="Add stock to a product")
def restock(data: RestockRequest):
    """Increase a product's stock by the given quantity."""
    try:
        return admin_manager.restock_product(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/products/{product_id}", summary="Delete a product")
def delete_product(product_id: int):
    """
    Remove a product from the catalogue.
    Also removes it from any active customer carts.
    """
    try:
        return admin_manager.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  ORDER / PAYMENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/orders", summary="View all customer orders")
def all_orders(
    status: Optional[str] = Query(
        None,
        description="Filter by status: pending | confirmed | cancelled | refunded",
    )
):
    """
    Returns every order across all customers.
    - Leave `status` blank to see all orders.
    - Use `?status=confirmed` to see only paid orders, etc.
    """
    return {"orders": admin_manager.get_all_orders(status)}


@router.patch("/orders/status", summary="Update an order status")
def update_order_status(data: UpdatePaymentStatusRequest):
    """
    Change the status of any order.
    Allowed values: `pending` | `confirmed` | `cancelled` | `refunded`
    """
    try:
        return admin_manager.update_order_status(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/revenue", summary="Revenue report")
def revenue_report():
    """
    Returns:
    - All-time total revenue
    - Revenue grouped by payment method
    - Day-by-day revenue for the last 30 days
    """
    return admin_manager.get_revenue_report()
