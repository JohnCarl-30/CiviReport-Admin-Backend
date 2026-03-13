from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Complaint_media(Base):
    __tablename__ = "complaint_media"


    media_id = Column(Integer, primary_key=True, index= True)
    complaint_id = Column(Integer, ForeignKey("complaint.complaint_id"))
    file_path = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)
    
    complaint = relationship("Complaint", back_populates="complaint_media")