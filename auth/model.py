from pydantic import BaseModel


# =========================
# SIGNUP REQUEST
# =========================

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


# =========================
# LOGIN REQUEST
# =========================

class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# USER RESPONSE
# =========================

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    message: str = ""


# =========================
# FORGOT PASSWORD REQUEST
# =========================

class ForgotPasswordRequest(BaseModel):
    email: str


# =========================
# RESET PASSWORD REQUEST
# =========================

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str