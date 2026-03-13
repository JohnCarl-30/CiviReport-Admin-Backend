# routes.py
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext

from schemas import ForgotPasswordRequest, ResetPasswordRequest
from otp_service import generate_and_store_otp, verify_otp
from email_service import send_otp_email
from models  import get_user_by_email, update_user_password

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    # Replace with your actual DB lookup
    user = await get_user_by_email(req.email)
    if not user:
        # Don't reveal if email exists — always return success
        return {"message": "If that email exists, an OTP has been sent."}

    otp = await generate_and_store_otp(req.email)
    await send_otp_email(req.email, otp)
    return {"message": "If that email exists, an OTP has been sent."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    valid = await verify_otp(req.email, req.otp)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    hashed = pwd_context.hash(req.new_password)
    # Replace with your actual DB update
    await update_user_password(req.email, hashed)
    return {"message": "Password reset successful"}