import bcrypt
import random

from database import get_connection


# temporary OTP storage
reset_otps = {}


# =========================
# SIGNUP
# =========================

def signup_user(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=?",
        (data.email,)
    )

    existing_user = cur.fetchone()

    if existing_user:
        return {
            "message": "Email already registered"
        }

    hashed_password = bcrypt.hashpw(
        data.password.encode(),
        bcrypt.gensalt()
    ).decode()

    cur.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
        """,
        (
            data.name,
            data.email,
            hashed_password
        )
    )

    conn.commit()

    return {
        "message": "User registered successfully"
    }


# =========================
# LOGIN
# =========================

def login_user(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=?",
        (data.email,)
    )

    user = cur.fetchone()

    if not user:
        return {
            "message": "Invalid email"
        }

    stored_password = user["password"]

    password_correct = bcrypt.checkpw(
        data.password.encode(),
        stored_password.encode()
    )

    if not password_correct:
        return {
            "message": "Invalid password"
        }

    return {
        "message": "Login successful"
    }


# =========================
# FORGOT PASSWORD
# =========================

def forgot_password(email: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cur.fetchone()

    if not user:
        return {
            "message": "Email not registered"
        }

    otp = str(random.randint(100000, 999999))

    reset_otps[email] = otp

    return {
        "message": "OTP generated successfully",
        "otp": otp
    }


# =========================
# RESET PASSWORD
# =========================

def reset_password(
    email: str,
    otp: str,
    new_password: str
):
    if email not in reset_otps:
        return {
            "message": "No OTP generated"
        }

    if reset_otps[email] != otp:
        return {
            "message": "Invalid OTP"
        }

    hashed_password = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET password=?
        WHERE email=?
        """,
        (
            hashed_password,
            email
        )
    )

    conn.commit()

    del reset_otps[email]

    return {
        "message": "Password reset successful"
    }