
from sqlalchemy import Boolean, Column, Integer, String, Date, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), unique=True, nullable=False)
    email = Column(String(255),unique=True, nullable=False)
    contact_num = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    password = Column(String(255), nullable=False)
    date_registered = Column(Date, default=func.current_date())
    role = Column(String(10), default='user')
    is_active = Column(Boolean, default=True)


    complaints = relationship("Complaint", back_populates="user")


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def update_user_password(db: AsyncSession, email: str, hashed_password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        user.password = hashed_password
        await db.commit()