from database import get_connection
from payment.model import PaymentRequest
from cart.manager import get_cart, clear_cart


def process_payment(data: PaymentRequest) -> dict:
    """
    Process a cash payment for everything currently in the user's cart.

    Steps:
      1. Fetch cart & compute grand total
      2. Deduct stock for each product
      3. Record payment row
      4. Clear the user's cart
    """
    # 1 – Fetch cart
    cart = get_cart(data.user_id)        # raises ValueError if user missing
    items = cart["items"]

    if not items:
        raise ValueError("Your cart is empty. Add products before checking out.")

    grand_total = cart["grand_total"]

    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 2 – Deduct stock
        for item in items:
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                (item["quantity"], item["product_id"], item["quantity"]),
            )
            if cursor.rowcount == 0:
                raise ValueError(
                    f"Insufficient stock for '{item['product_name']}' at checkout."
                )

        # 3 – Insert payment record
        cursor.execute(
            """
            INSERT INTO payments (user_id, total, method, status)
            VALUES (?, ?, ?, 'confirmed')
            """,
            (data.user_id, grand_total, data.method),
        )
        payment_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()

    # 4 – Clear cart
    clear_cart(data.user_id)

    return {
        "payment_id": payment_id,
        "user_id": data.user_id,
        "total": grand_total,
        "method": data.method,
        "status": "confirmed",
        "message": (
            f"✅  Payment of ₹{grand_total:,.2f} via {data.method.upper()} confirmed! "
            "Thank you for shopping with us."
        ),
        "items_purchased": [
            {
                "product_id":   i["product_id"],
                "product_name": i["product_name"],
                "quantity":     i["quantity"],
                "subtotal":     i["subtotal"],
            }
            for i in items
        ],
    }


def get_payment_history(user_id: int) -> list[dict]:
    """Return all past payments for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User with id={user_id} does not exist.")

        cursor.execute(
            """
            SELECT id AS payment_id, user_id, total, method, status, created_at
            FROM payments
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
