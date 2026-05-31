import bcrypt
from database import get_connection
from admin.model import (
    AdminLoginRequest, AdminCreateRequest,
    ProductCreateRequest, ProductUpdateRequest,
    RestockRequest, UpdatePaymentStatusRequest,
)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════

def admin_login(data: AdminLoginRequest) -> dict:
    """Authenticate an admin by email + password."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = ?", (data.email,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("No admin account found with this email.")
        if not bcrypt.checkpw(data.password.encode(), row["password"].encode()):
            raise ValueError("Incorrect password.")
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role": row["role"],
            "message": f"Welcome, {row['username']}! Admin login successful.",
        }
    finally:
        conn.close()


def create_admin(data: AdminCreateRequest) -> dict:
    """Register a new admin account (superadmin only action — enforced at router)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM admins WHERE email = ? OR username = ?",
            (data.email, data.username),
        )
        if cursor.fetchone():
            raise ValueError("An admin with this email or username already exists.")
        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO admins (username, email, password, role) VALUES (?,?,?,?)",
            (data.username, data.email, hashed, data.role),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "username": data.username,
            "email": data.email,
            "role": data.role,
            "message": f"Admin '{data.username}' created successfully.",
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def get_dashboard_stats() -> dict:
    """
    Return key business metrics:
      • total users, products, orders, revenue
      • low-stock alerts  (stock < 10)
      • top 3 selling products by revenue
      • recent 5 orders
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Counts
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products")
        total_products = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM payments WHERE status = 'confirmed'")
        total_orders = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(total), 0) FROM payments WHERE status = 'confirmed'")
        total_revenue = round(cur.fetchone()[0], 2)

        # Low-stock alerts
        cur.execute(
            "SELECT id, name, stock FROM products WHERE stock < 10 ORDER BY stock ASC"
        )
        low_stock = [dict(r) for r in cur.fetchall()]

        # Recent 5 confirmed orders
        cur.execute(
            """
            SELECT p.id, u.name AS customer, p.total, p.method, p.status, p.created_at
            FROM payments p
            JOIN users u ON u.id = p.user_id
            ORDER BY p.created_at DESC
            LIMIT 5
            """
        )
        recent_orders = [dict(r) for r in cur.fetchall()]

        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "low_stock_alerts": low_stock,
            "recent_orders": recent_orders,
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def get_all_users() -> list[dict]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users ORDER BY id")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_user_detail(user_id: int) -> dict:
    """Full profile: info + order history + current cart."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError(f"User id={user_id} not found.")

        # Order history
        cur.execute(
            """
            SELECT id AS payment_id, total, method, status, created_at
            FROM payments WHERE user_id = ? ORDER BY created_at DESC
            """,
            (user_id,),
        )
        orders = [dict(r) for r in cur.fetchall()]

        # Active cart
        cur.execute(
            """
            SELECT c.id AS cart_id, p.id AS product_id, p.name, p.price,
                   c.quantity, ROUND(p.price * c.quantity, 2) AS subtotal
            FROM cart c JOIN products p ON p.id = c.product_id
            WHERE c.user_id = ?
            """,
            (user_id,),
        )
        cart_items = [dict(r) for r in cur.fetchall()]

        return {
            "user": dict(user),
            "total_orders": len(orders),
            "total_spent": round(sum(o["total"] for o in orders if o["status"] == "confirmed"), 2),
            "order_history": orders,
            "active_cart": cart_items,
        }
    finally:
        conn.close()


def delete_user(user_id: int) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            raise ValueError(f"User id={user_id} not found.")
        cur.execute("DELETE FROM cart     WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM payments WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM users    WHERE id = ?",      (user_id,))
        conn.commit()
        return {"message": f"User id={user_id} and all related data deleted."}
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def add_product(data: ProductCreateRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, description, price, stock) VALUES (?,?,?,?)",
            (data.name, data.description, data.price, data.stock),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "name": data.name,
            "price": data.price,
            "stock": data.stock,
            "message": f"Product '{data.name}' added successfully.",
        }
    finally:
        conn.close()


def update_product(product_id: int, data: ProductUpdateRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        existing = cur.fetchone()
        if not existing:
            raise ValueError(f"Product id={product_id} not found.")

        # Build dynamic SET clause — only update provided fields
        fields = {}
        if data.name        is not None: fields["name"]        = data.name
        if data.description is not None: fields["description"] = data.description
        if data.price       is not None: fields["price"]       = data.price
        if data.stock       is not None: fields["stock"]       = data.stock

        if not fields:
            raise ValueError("No fields provided to update.")

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [product_id]
        cur.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        conn.commit()

        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        updated = dict(cur.fetchone())
        updated["message"] = "Product updated successfully."
        return updated
    finally:
        conn.close()


def restock_product(data: RestockRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, stock FROM products WHERE id = ?", (data.product_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Product id={data.product_id} not found.")
        new_stock = row["stock"] + data.quantity
        cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, data.product_id))
        conn.commit()
        return {
            "product_id": data.product_id,
            "product_name": row["name"],
            "added": data.quantity,
            "new_stock": new_stock,
            "message": f"Restocked '{row['name']}' by {data.quantity} units. New stock: {new_stock}.",
        }
    finally:
        conn.close()


def delete_product(product_id: int) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Product id={product_id} not found.")
        cur.execute("DELETE FROM cart     WHERE product_id = ?", (product_id,))
        cur.execute("DELETE FROM products WHERE id = ?",         (product_id,))
        conn.commit()
        return {"message": f"Product '{row['name']}' (id={product_id}) deleted."}
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  ORDER / PAYMENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def get_all_orders(status: str | None = None) -> list[dict]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if status:
            cur.execute(
                """
                SELECT p.id AS order_id, u.id AS user_id, u.name AS customer,
                       u.email, p.total, p.method, p.status, p.created_at
                FROM payments p JOIN users u ON u.id = p.user_id
                WHERE p.status = ? ORDER BY p.created_at DESC
                """,
                (status,),
            )
        else:
            cur.execute(
                """
                SELECT p.id AS order_id, u.id AS user_id, u.name AS customer,
                       u.email, p.total, p.method, p.status, p.created_at
                FROM payments p JOIN users u ON u.id = p.user_id
                ORDER BY p.created_at DESC
                """
            )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_order_status(data: UpdatePaymentStatusRequest) -> dict:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, status FROM payments WHERE id = ?", (data.payment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Order id={data.payment_id} not found.")
        cur.execute(
            "UPDATE payments SET status = ? WHERE id = ?",
            (data.status, data.payment_id),
        )
        conn.commit()
        return {
            "order_id": data.payment_id,
            "old_status": row["status"],
            "new_status": data.status,
            "message": f"Order {data.payment_id} status updated to '{data.status}'.",
        }
    finally:
        conn.close()


def get_revenue_report() -> dict:
    """Revenue breakdown by day (last 30 days) and by payment method."""
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT DATE(created_at) AS day, COUNT(*) AS orders,
                   ROUND(SUM(total), 2) AS revenue
            FROM payments
            WHERE status = 'confirmed'
              AND created_at >= DATE('now', '-30 days')
            GROUP BY day ORDER BY day DESC
            """
        )
        daily = [dict(r) for r in cur.fetchall()]

        cur.execute(
            """
            SELECT method, COUNT(*) AS orders, ROUND(SUM(total), 2) AS revenue
            FROM payments WHERE status = 'confirmed'
            GROUP BY method
            """
        )
        by_method = [dict(r) for r in cur.fetchall()]

        cur.execute(
            "SELECT ROUND(SUM(total), 2) FROM payments WHERE status = 'confirmed'"
        )
        all_time_revenue = cur.fetchone()[0] or 0.0

        return {
            "all_time_revenue": all_time_revenue,
            "by_payment_method": by_method,
            "last_30_days_daily": daily,
        }
    finally:
        conn.close()
