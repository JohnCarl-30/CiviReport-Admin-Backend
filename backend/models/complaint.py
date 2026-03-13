from sqlalchemy import Column, Integer, String,Date,ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base
from models.users import User
class Complaint(Base):
    __tablename__ = "complaint"


    complaint_id = Column(Integer, primary_key=True, index= True)
    complaint_date = Column(Date, default=func.current_date())
    user_id = Column(Integer, ForeignKey("users.user_id"))
    complaint_type = Column(String(255), nullable=False )
    complaint_subtype= Column(String(255), nullable = False)
    additional_notes = Column(String(255), nullable= True)
    complaint_location = Column(String(500), nullable= False)
    complaint_status = Column(String(255), nullable=False)

    user = relationship("User", back_populates="complaints")
    complaint_media = relationship("Complaint_media", back_populates="complaint")