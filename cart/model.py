from pydantic import BaseModel, field_validator


class AddToCartRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class CartItemResponse(BaseModel):
    cart_id: int
    user_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float


class RemoveFromCartRequest(BaseModel):
    cart_id: int
    user_id: int
