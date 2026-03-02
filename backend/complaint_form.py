from fastapi import FastAPI,UploadFile,Form, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.complaint import Complaint
from models.complaint_media import Complaint_media
from pydantic import BaseModel, Field, field_validator
import re
from pathlib import Path
import os
from models.users import User
from dependencies import get_current_user
import uuid

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


class ComplaintCreate(BaseModel):
    complaint_type: str = Field(min_length=3)
    complaint_subtype: str = Field(min_length=3)
    additional_notes: str = Field(min_length=10)
    complaint_location: str = Field(min_length=5)

    @field_validator("*")
    @classmethod
    def no_empty_strings(cls,v):
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v
    @classmethod
    def as_form(
         cls,
        complaint_type: str = Form(...),
        complaint_subtype: str = Form(...),
        additional_note: str = Form(...),
        complaint_location: str = Form(...)
        ):
        return cls(
            complaint_type=complaint_type,
            complaint_subtype=complaint_subtype,
            additional_note=additional_note,
            complaint_location=complaint_location
        )


@app.post("/complaint_form")
async def create_complaint(
    data: ComplaintCreate = Depends(ComplaintCreate.as_form),
    files: list[UploadFile] = [],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # save complaint:
    complaint_obj = Complaint(user_id = current_user.user_id, 
                              complaint_type = data.complaint_type, 
                              complaint_subtype = data.complaint_subtype, 
                              additional_notes = data.additional_notes, 
                              complaint_location = data.complaint_location, 
                              complaint_status = "pending"
                              )
    db.add(complaint_obj)
    db.commit()
    db.refresh(complaint_obj)

    # save media:
    for f in files:
        ext  = Path(f.filename).suffix.lower()
        if ext in [".jpg",".png",".gif",".jpeg"]:
            media_type = "image"
        elif ext in [".mov",".mp4",".avi",".mkv"]:
            media_type = "video"
        else:
            media_type = "other"

        filename = f"{uuid.uuid4()}{ext}"


        file_path = os.path.join(UPLOAD_FOLDER, filename) 
        with open(file_path, "wb") as buffer:
            buffer.write(await f.read())

        media = Complaint_media(
            complaint_id = complaint_obj.complaint_id,
            file_url = f"/{UPLOAD_FOLDER}/{f.filename}",
            media_type = media_type
        )
        db.add(media)

    db.commit()
    return{
            "complaint_id": complaint_obj.complaint_id,
            "media_count": len(files),
            "message":"complaint ticket has been succefully submited! thankyou for reporting an issue! a baranggay official will handle your ticket as soon as possible!"
        }


    






