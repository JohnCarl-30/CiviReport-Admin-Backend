
from sqlalchemy import Column, Integer, String,Date, func
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), nullable=False)
    email = Column(String(255),unique=True, nullable=False)
    contact_num = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    password = Column(String(255), nullable=False)
    date_registered = Column(Date, default=func.current_date())
    role = Column(String(10), default='user')

    complaints = relationship("Complaint", back_populates="user")
