from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import os, uuid

from database import SessionLocal
from models.complaint import Complaint
from models.complaint_media import Complaint_media
from models.users import User
from auth import DbDep, CurrentUser

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_VIDEO_EXTS = {".mov", ".mp4", ".avi", ".mkv"}
MAX_FILE_SIZE_MB = 10
MAX_FILES = 5


# --- Schema ---
class ComplaintCreate(BaseModel):
    complaint_type: str = Field(..., min_length=3)
    complaint_subtype: str = Field(..., min_length=3)
    additional_notes: str = Field(..., min_length=10)
    complaint_location: str = Field(..., min_length=5)

    @field_validator("*")
    @classmethod
    def no_empty_strings(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v

    @classmethod
    def as_form(
        cls,
        complaint_type: str = Form(...),
        complaint_subtype: str = Form(...),
        additional_notes: str = Form(...),   # fixed: was "additional_note"
        complaint_location: str = Form(...),
    ) -> "ComplaintCreate":
        return cls(
            complaint_type=complaint_type,
            complaint_subtype=complaint_subtype,
            additional_notes=additional_notes,
            complaint_location=complaint_location,
        )



class ComplaintResponse(BaseModel):
    complaint_id: int
    media_count: int
    message: str = "Complaint submitted successfully. A barangay official will handle your ticket shortly."



router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/complaint-form", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate = Depends(ComplaintCreate.as_form),
    files: list[UploadFile] = File(default=[]),
    current_user: CurrentUser = Depends(),
    db: DbDep = Depends(),
):
    # Validate file count
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES} files allowed",
        )

  
    complaint = Complaint(
        user_id=current_user.user_id,
        complaint_type=data.complaint_type,
        complaint_subtype=data.complaint_subtype,
        additional_notes=data.additional_notes,
        complaint_location=data.complaint_location,
        complaint_status="pending",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Save media
    saved = 0
    for f in files:
        if not f.filename:
            continue

        ext = Path(f.filename).suffix.lower()
        if ext in ALLOWED_IMAGE_EXTS:
            media_type = "image"
        elif ext in ALLOWED_VIDEO_EXTS:
            media_type = "video"
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{ext}' is not allowed",
            )

        contents = await f.read()
        if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{f.filename}' exceeds {MAX_FILE_SIZE_MB}MB limit",
            )

        # Use uuid filename to avoid collisions and path traversal
        filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_FOLDER / filename

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        db.add(Complaint_media(
            complaint_id=complaint.complaint_id,
            file_url=f"/uploads/{filename}",   # fixed: was using f.filename (original name)
            media_type=media_type,
        ))
        saved += 1

    db.commit()

    return ComplaintResponse(complaint_id=complaint.complaint_id, media_count=saved)