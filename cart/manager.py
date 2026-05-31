from database import get_connection
from cart.model import AddToCartRequest


def add_to_cart(data: AddToCartRequest) -> dict:
    """
    Add a product to a user's cart.
    Validates that both user and product exist, and that stock is available.
    Uses user_id + product_id as the logical key.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Validate user
        cursor.execute("SELECT id FROM users WHERE id = ?", (data.user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User with id={data.user_id} does not exist.")

        # Validate product & check stock
        cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (data.product_id,))
        product = cursor.fetchone()
        if not product:
            raise ValueError(f"Product with id={data.product_id} does not exist.")
        if product["stock"] < data.quantity:
            raise ValueError(f"Only {product['stock']} units available for '{product['name']}'.")

        # If item already in cart → update quantity
        cursor.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (data.user_id, data.product_id),
        )
        existing = cursor.fetchone()
        if existing:
            new_qty = existing["quantity"] + data.quantity
            cursor.execute(
                "UPDATE cart SET quantity = ? WHERE id = ?",
                (new_qty, existing["id"]),
            )
            cart_id = existing["id"]
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (data.user_id, data.product_id, data.quantity),
            )
            cart_id = cursor.lastrowid

        conn.commit()

        return {
            "message": f"'{product['name']}' added to cart!",
            "cart_id": cart_id,
            "user_id": data.user_id,
            "product_id": data.product_id,
            "product_name": product["name"],
            "price": product["price"],
            "quantity": data.quantity,
            "subtotal": round(product["price"] * data.quantity, 2),
        }
    finally:
        conn.close()


def get_cart(user_id: int) -> dict:
    """Return all items in a user's cart with totals."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User with id={user_id} does not exist.")

        cursor.execute(
            """
            SELECT c.id AS cart_id,
                   c.user_id,
                   c.product_id,
                   p.name  AS product_name,
                   p.price,
                   c.quantity,
                   ROUND(p.price * c.quantity, 2) AS subtotal
            FROM cart c
            JOIN products p ON p.id = c.product_id
            WHERE c.user_id = ?
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        items = [dict(r) for r in rows]
        grand_total = round(sum(item["subtotal"] for item in items), 2)
        return {"user_id": user_id, "items": items, "grand_total": grand_total}
    finally:
        conn.close()


def remove_from_cart(cart_id: int, user_id: int) -> dict:
    """Remove a specific cart entry (ownership is verified)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM cart WHERE id = ? AND user_id = ?", (cart_id, user_id)
        )
        if not cursor.fetchone():
            raise ValueError("Cart item not found or does not belong to this user.")
        cursor.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        conn.commit()
        return {"message": "Item removed from cart.", "cart_id": cart_id}
    finally:
        conn.close()


def clear_cart(user_id: int):
    """Delete all cart items for a user (called after successful payment)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
