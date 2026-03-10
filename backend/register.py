from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, field_validator, model_validator
from database import SessionLocal, engine, Base
from models.users import User
from auth import hash_password, DbDep  # reuse from your auth module
import re

Base.metadata.create_all(bind=engine)

app = FastAPI()



class Register(BaseModel):
    first_name: str
    middle_name: str = ""
    last_name: str
    suffix: str = ""
    username: str | None = None
    email: str
    contact_num: str
    address: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name fields cannot be empty")
        if any(c.isdigit() for c in v):
            raise ValueError("Name must not contain numbers")
        return v

    @model_validator(mode="before")
    @classmethod
    def build_username(cls, values: dict) -> dict:

        if not values.get("username"):
            first = values.get("first_name", "").strip().lower()
            middle = values.get("middle_name", "").strip().lower()
            last = values.get("last_name", "").strip().lower()
         
            values["username"] = f"{first}{middle[0] if middle else ''}{last}"
        return values

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("contact_num")
    @classmethod
    def validate_contact_num(cls, v: str) -> str:
        if not re.match(r"^(09|\+639)\d{9}$", v):
            raise ValueError(
                "Invalid contact number — must be a valid PHL number (09XXXXXXXXX or +639XXXXXXXXX)"
            )
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Address cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def check_passwords_match(self) -> "Register":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    message: str = "Registration successful"

    model_config = {"from_attributes": True}

    

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: Register, db: DbDep):
    new_user = User(
        username=payload.username,
        email=payload.email,
        contact_num=payload.contact_num,
        address=payload.address,
        password=hash_password(payload.password),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email/Username taken")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database connection error")

    db.refresh(new_user)
    return new_user