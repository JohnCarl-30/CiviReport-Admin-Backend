from fastapi import APIRouter, HTTPException
from models.users import User
from schemas.forgot_password import ForgotPasswordRequest, ResetPasswordRequest
from services.otp_service import generate_and_store_otp, verify_otp
from services.email_service import send_otp_email
from dependencies import DbDep, hash_password

router = APIRouter()


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: DbDep):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = await generate_and_store_otp(req.email)
    await send_otp_email(req.email, otp)
    return {"message": "If that email exists, an OTP has been sent."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: DbDep):
    valid = await verify_otp(req.email, req.otp)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    hashed = hash_password(req.new_password)
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user.password = hashed
    db.commit()
    return {"message": "Password reset successful"}