from pydantic import BaseModel
from typing import Literal, Optional


# ── Auth ───────────────────────────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Literal["admin", "superadmin"] = "admin"


# ── Products (CRUD) ────────────────────────────────────────────────────────────

class ProductCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    stock: int


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class RestockRequest(BaseModel):
    product_id: int
    quantity: int


# ── Orders / Payments ─────────────────────────────────────────────────────────

class UpdatePaymentStatusRequest(BaseModel):
    payment_id: int
    status: Literal["pending", "confirmed", "cancelled", "refunded"]
