# 🛒 E-Commerce Backend

A clean, professional, modular e-commerce REST API built with **FastAPI + SQLite + bcrypt**.

---

## 📁 Project Structure

```
ecommerce/
│
├── main.py              ← App entry point; registers all routers
├── database.py          ← SQLite setup & table creation (seeds 10 products)
├── requirements.txt
│
├── auth/                ← Signup & Login
│   ├── model.py         ← Pydantic request/response schemas
│   ├── manager.py       ← Business logic (bcrypt hashing, validation)
│   └── router.py        ← FastAPI routes  /auth/signup  /auth/login
│
├── products/            ← Product catalogue & search
│   ├── model.py
│   ├── manager.py       ← get_all_products(), search_products()
│   └── router.py        ← /products/  /products/search  /products/{id}
│
├── cart/                ← Shopping cart
│   ├── model.py
│   ├── manager.py       ← add_to_cart(), get_cart(), remove_from_cart()
│   └── router.py        ← /cart/add  /cart/{user_id}  /cart/remove
│
└── payment/             ← Checkout & payment history
    ├── model.py
    ├── manager.py       ← process_payment() (deducts stock, clears cart)
    └── router.py        ← /payment/checkout  /payment/history/{user_id}
```

---

## 🚀 Getting Started

```bash
# 1 – Install dependencies
pip install -r requirements.txt

# 2 – Start the server
cd ecommerce
uvicorn main:app --reload

# 3 – Open interactive docs
http://127.0.0.1:8000/docs
```

---

## 🔄 User Flow

### 1. Sign Up
```
POST /auth/signup
{
  "name": "Rahul Sharma",
  "email": "rahul@gmail.com",
  "password": "mypassword"
}
→ Returns user id = 1
```

### 2. Login
```
POST /auth/login
{
  "email": "rahul@gmail.com",
  "password": "mypassword"
}
→ Wrong password / no account → clear error message
→ Success → { "id": 1, "name": "Rahul Sharma", ... }
```

### 3. Browse / Search Products
```
GET /products/             ← all products
GET /products/search?q=ip  ← returns iPhone 15, iPad Air
GET /products/3            ← product with id=3
```

### 4. Add to Cart
```
POST /cart/add
{
  "user_id": 1,
  "product_id": 2,
  "quantity": 1
}
```

### 5. View Cart
```
GET /cart/1   ← all items + grand total for user 1
```

### 6. Checkout (Cash on Delivery)
```
POST /payment/checkout
{
  "user_id": 1,
  "method": "cash"
}
→ Payment confirmed, stock deducted, cart cleared
```

### 7. Payment History
```
GET /payment/history/1
```

---

## 🔐 Security

- Passwords are **never stored in plain text**.
- `bcrypt` with salted hashing is used (`bcrypt.hashpw` / `bcrypt.checkpw`).
- If an email does not exist → "Please sign up first" (not "wrong password").

---

## 🗄️ Database Tables

| Table     | Key Columns                                      |
|-----------|--------------------------------------------------|
| users     | id (1,2,3…), name, email, password (hashed)      |
| products  | id (1,2,3…), name, description, price, stock     |
| cart      | id, user_id, product_id, quantity                |
| payments  | id, user_id, total, method, status, created_at   |
