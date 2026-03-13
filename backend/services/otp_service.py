# otp_service.py
import random
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

OTP_EXPIRE_SECONDS = 300  # 5 minutes
OTP_PREFIX = "otp:"

async def generate_and_store_otp(email: str) -> str:
    otp = f"{random.randint(100000, 999999)}"
    key = f"{OTP_PREFIX}{email}"
    await redis_client.set(key, otp, ex=OTP_EXPIRE_SECONDS)
    return otp

async def verify_otp(email: str, otp: str) -> bool:
    key = f"{OTP_PREFIX}{email}"
    stored = await redis_client.get(key)
    if stored and stored == otp:
        await redis_client.delete(key)  # one-time use
        return True
    return False