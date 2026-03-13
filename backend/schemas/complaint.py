from fastapi import Form
from pydantic import BaseModel, Field, field_validator


class ComplaintCreate(BaseModel):
 
    complaint_type: str = Field(..., min_length=3, description="Category of the complaint", examples=["Noise"])
    complaint_subtype: str = Field(..., min_length=3, description="Subcategory of the complaint", examples=["Loud Music"])
    additional_notes: str = Field(..., min_length=10, description="Extra details about the complaint", examples=["Ongoing loud music every night past 10PM"])
    complaint_location: str = Field(..., min_length=5, description="Location where the incident occurred", examples=["123 Rizal St, Brgy. San Antonio"])

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
        complaint_type: str = Form(..., min_length=3, description="Category of the complaint"),
        complaint_subtype: str = Form(..., min_length=3, description="Subcategory of the complaint"),
        additional_notes: str = Form(..., min_length=10, description="Extra details about the complaint"),
        complaint_location: str = Form(..., min_length=5, description="Location where the incident occurred"),
    ) -> "ComplaintCreate":
        return cls(
            complaint_type=complaint_type.strip(),
            complaint_subtype=complaint_subtype.strip(),
            additional_notes=additional_notes.strip(),
            complaint_location=complaint_location.strip(),
        )


class ComplaintResponse(BaseModel):

    complaint_id: int = Field(..., description="ID of the created complaint ticket", examples=[1])
    media_count: int = Field(..., description="Number of media files attached", examples=[2])
    message: str = Field(
        default="Complaint ticket has been successfully submitted! A barangay official will handle your ticket shortly.",
        description="Submission status message",
    )