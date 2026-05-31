"""
E-Commerce Backend
==================
Run with:  uvicorn main:app --reload
Docs at:   http://127.0.0.1:8000/docs
"""

import sys
import os

# Make sure sub-packages can import `database` from the project root
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from database import init_db

from auth.router    import router as auth_router
from products.router import router as products_router
from cart.router    import router as cart_router
from payment.router import router as payment_router
from admin.router   import router as admin_router

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="🛒 E-Commerce Backend",
    description=(
        "A clean, modular e-commerce REST API.\n\n"
        "**Flow:** Signup → Login → Browse/Search Products → Add to Cart → Checkout"
    ),
    version="1.0.0",
)

# ── DB init on startup ─────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()

# ── Register routers ───────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(payment_router)
app.include_router(admin_router)

# ── Root ───────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the E-Commerce API 🛒",
        "docs": "/docs",
        "endpoints": {
            "auth":     ["/auth/signup", "/auth/login"],
            "products": ["/products/", "/products/search?q=<keyword>", "/products/{id}"],
            "cart":     ["/cart/add", "/cart/{user_id}", "/cart/remove"],
            "payment":  ["/payment/checkout", "/payment/history/{user_id}"],
            "admin":    [
                "/admin/login",
                "/admin/dashboard",
                "/admin/users",
                "/admin/users/{user_id}",
                "/admin/products  (POST/PATCH/DELETE)",
                "/admin/products/restock",
                "/admin/orders",
                "/admin/orders/status",
                "/admin/revenue",
            ],
        },
    }
