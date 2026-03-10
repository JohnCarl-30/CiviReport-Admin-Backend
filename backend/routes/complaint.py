from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pathlib import Path
import uuid
from typing import List

from dependencies import CurrentUser, DbDep
from models.complaint import Complaint
from models.complaint_media import Complaint_media
from schemas.complaint import ComplaintCreate, ComplaintResponse

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".avi", ".mkv"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
MAX_FILES = 5
MAX_FILE_SIZE_MB = 10

router = APIRouter()


def get_media_type(ext: str) -> str:
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "other"


@router.post(
    "/complaint-form",                          # kebab-case, consistent with REST convention
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a Complaint Ticket",
    responses={
        401: {"description": "Not authenticated"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
    },
)
async def create_complaint(
    current_user: CurrentUser,
    db: DbDep,
    data: ComplaintCreate = Depends(ComplaintCreate.as_form),
    files: List[UploadFile] = File(default=[], description="Upload images or video"),


):

    if files is None:
        files = []

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES} files allowed per complaint",
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

    for f in files:
        if not f.filename:
            continue

        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{ext}' is not allowed",
            )

        contents = await f.read()
        if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"'{f.filename}' exceeds the {MAX_FILE_SIZE_MB}MB size limit",
            )

        filename = f"{uuid.uuid4()}{ext}"
        (UPLOAD_FOLDER / filename).write_bytes(contents)

        db.add(Complaint_media(
            complaint_id=complaint.complaint_id,
            file_path=f"/uploads/{filename}",
            media_type=get_media_type(ext),
        ))

    db.commit()
    return ComplaintResponse(
        complaint_id=complaint.complaint_id,
        media_count=len(files),
    )