import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # --- USERS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            email   TEXT    NOT NULL UNIQUE,
            password TEXT   NOT NULL
        )
    """)

    # --- PRODUCTS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0
        )
    """)

    # --- CART TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id)    REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # --- PAYMENTS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            total       REAL    NOT NULL,
            method      TEXT    NOT NULL DEFAULT 'cash',
            status      TEXT    NOT NULL DEFAULT 'pending',
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # --- ADMINS TABLE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'admin'
        )
    """)

    # --- SEED DEFAULT SUPER ADMIN (password: admin123) ---
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        import bcrypt
        hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO admins (username, email, password, role) VALUES (?,?,?,?)",
            ("superadmin", "admin@ecommerce.com", hashed, "superadmin"),
        )

    # --- SEED SAMPLE PRODUCTS ---
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("iPhone 15",        "Apple iPhone 15 – 128GB, 6.1-inch display",       79999, 50),
            ("iPad Air",         "Apple iPad Air – M1 chip, 10.9-inch",              54999, 30),
            ("Samsung Galaxy S24","Samsung Galaxy S24 – 256GB, 6.2-inch",            74999, 40),
            ("OnePlus 12",       "OnePlus 12 – Snapdragon 8 Gen 3, 256GB",           64999, 35),
            ("Laptop Dell XPS",  "Dell XPS 15 – Intel i7, 16GB RAM, 512GB SSD",     129999, 20),
            ("Sony Headphones",  "Sony WH-1000XM5 – Noise Cancelling Wireless",      29999, 60),
            ("Nike Air Max",     "Nike Air Max 270 – Unisex Running Shoes",           8999, 100),
            ("Levi's Jeans",     "Levi's 511 Slim Fit Jeans – Blue Denim",           3999, 80),
            ("Whey Protein",     "Optimum Nutrition Gold Standard Whey – 2lb",        3499, 70),
            ("Smart Watch",      "boAt Xtend Pro Smartwatch – SpO2 & Alexa built-in", 4999, 90),
        ]
        cursor.executemany(
            "INSERT INTO products (name, description, price, stock) VALUES (?,?,?,?)",
            sample_products,
        )

    conn.commit()
    conn.close()
    print("✅  Database initialised at", DB_PATH)
