from fastapi import APIRouter, HTTPException
from payment.model import PaymentRequest
from payment import manager as payment_manager

router = APIRouter(prefix="/payment", tags=["Payment"])


@router.post("/checkout", summary="Pay for cart items (Cash on Delivery)")
def checkout(data: PaymentRequest):
    """
    Processes payment for all items currently in the user's cart.

    - **user_id**: ID of the logged-in user
    - **method**: payment method — currently supports `cash` (Cash on Delivery)

    On success: stock is deducted, payment recorded, cart is cleared.
    """
    try:
        return payment_manager.process_payment(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{user_id}", summary="View past payments")
def payment_history(user_id: int):
    """Return all confirmed payments for the given user."""
    try:
        history = payment_manager.get_payment_history(user_id)
        if not history:
            return {"message": "No payment history found.", "payments": []}
        return {"payments": history}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
