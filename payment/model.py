from pydantic import BaseModel
from typing import Literal


class PaymentRequest(BaseModel):
    user_id: int
    method: Literal["cash"] = "cash"


class PaymentResponse(BaseModel):
    payment_id: int
    user_id: int
    total: float
    method: str
    status: str
    message: str
    items_purchased: list
