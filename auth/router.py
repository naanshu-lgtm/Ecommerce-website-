from fastapi import APIRouter

from auth.model import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from auth.manager import (
    signup_user,
    login_user,
    forgot_password,
    reset_password
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# =========================
# SIGNUP
# =========================

@router.post("/signup")
def signup(data: SignupRequest):
    return signup_user(data)


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(data: LoginRequest):
    return login_user(data)


# =========================
# FORGOT PASSWORD
# =========================

@router.post("/forgot-password")
def forgot_password_route(data: ForgotPasswordRequest):
    return forgot_password(data.email)


# =========================
# RESET PASSWORD
# =========================

@router.post("/reset-password")
def reset_password_route(data: ResetPasswordRequest):
    return reset_password(
        data.email,
        data.otp,
        data.new_password
    )