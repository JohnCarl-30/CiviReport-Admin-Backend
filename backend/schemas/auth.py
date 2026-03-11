from pydantic import BaseModel, Field, field_validator, model_validator
import re




class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: str = Field(..., description="Registered email address", examples=["juan@example.com"])
    password: str = Field(..., description="Account password", examples=["securepass123"])


class Register(BaseModel):
    """Schema for new user registration."""
    first_name: str = Field(..., description="User's first name", examples=["Juan"])
    middle_name: str | None = Field(default=None, description="User's middle name", examples=["Dela"])
    last_name: str = Field(..., description="User's last name", examples=["Cruz"])
    suffix: str | None = Field(default=None, description="User's suffix", examples=["Jr."])
    user_name: str | None = Field(default=None, description="Auto-generated from first, middle, and last name")
    email: str = Field(..., description="Valid email address", examples=["juan@example.com"])
    contact_num: str = Field(..., description="Philippine phone number (09xx or +639xx)", examples=["09171234567"])
    address: str = Field(..., description="Current home address", examples=["123 Rizal St, Brgy. San Antonio, Manila"])
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    confirm_password: str = Field(..., min_length=8, description="Must match password")

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name fields cannot be empty!")
        if any(char.isdigit() for char in v):
            raise ValueError("Name must not contain any numbers")
        return v

    @model_validator(mode="before")
    @classmethod
    def combine_names(cls, values):
        first = (values.get("first_name") or "").strip()
        middle = (values.get("middle_name") or "").strip()
        last = (values.get("last_name") or "").strip()
        suffix = (values.get("suffix") or "").strip()
        parts = [p for p in [first, middle, last, suffix] if p]
        values["user_name"] = "".join(parts)
        return values

    @field_validator("contact_num")
    @classmethod
    def validate_contact_num(cls, v):
        phone_regex = r"^(09|\+639)\d{9}$"
        if not re.match(phone_regex, v):
            raise ValueError(
                "Invalid contact number, make sure that your number is a valid PHL number(+63) with 11 digits"
            )
        return v

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise ValueError(
                "password do not match! please make sure that your password is consistent"
            )
        return self

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if not v.strip():
            raise ValueError(
                "Address cannot be empty, please enter your current home address"
            )
        return v




class LoginResponse(BaseModel):
    """Response returned after successful login."""
    message: str = Field(..., description="Login status message", examples=["Login successfully!"])


class RegisterResponse(BaseModel):
    """Response returned after successful registration."""
    user_id: int = Field(..., description="ID of the newly created user", examples=[1])
    message: str = Field(..., description="Registration status message", examples=["Registration Success, new user has been created"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"