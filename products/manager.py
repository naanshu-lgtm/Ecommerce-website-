from database import get_connection


def get_all_products() -> list[dict]:
    """Return every product in the catalogue."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, stock FROM products")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_products(query: str) -> list[dict]:
    """
    Case-insensitive partial-match search on product name and description.
    E.g. query='ip'  →  ['iPhone 15', 'iPad Air']
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        like_pattern = f"%{query}%"
        cursor.execute(
            """
            SELECT id, name, description, price, stock
            FROM products
            WHERE name        LIKE ? COLLATE NOCASE
               OR description LIKE ? COLLATE NOCASE
            """,
            (like_pattern, like_pattern),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_product_by_id(product_id: int) -> dict | None:
    """Return a single product or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description, price, stock FROM products WHERE id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
