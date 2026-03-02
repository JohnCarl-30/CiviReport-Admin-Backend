from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base
from pydantic import BaseModel,field_validator, Field, model_validator
from models.users import User
from datetime import date
from passlib.hash import bcrypt
import re


Base.metadata.create_all(bind=engine)

app = FastAPI()
class Register(BaseModel):
    first_name:str
    middle_name:str
    last_name:str
    user_name: str | None = None
    email:str
    contact_num:str
    address:str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
   
    @field_validator('first_name','middle_name','last_name')
    @classmethod
    def name_not_empty(cls,v):
        v = v.strip()
        if not v:
            raise ValueError("Name fields cannot be empty!")
        
        if any(char.isdigit() for char in v):
            raise ValueError("Name must not contain any numbers")
        
        return v
    
    @model_validator(mode = 'before')
    def combine_names(cls,values):
        first = values.get('first_name', '').strip()
        middle = values.get('middle_name', '').strip()
        last = values.get('last_name', '').strip()
        user_name = f"{first}{middle}{last}"
        values['user_name'] = user_name
        return values
    
    @field_validator('email')
    def validate_email(cls, v):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex,v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator('contact_num')
    def validate_contact_num(cls, v):
        phone_rejex = r'^(09|\+639)\d{9}$'
        if not re.match(phone_rejex,v):
            raise ValueError("Invalid contact number, make sure that your number is a valid PHL number(+63) with 11 digits")
        return v
    @model_validator(mode='after')
    def check_password(cls, model):
        if model.password != model.confirm_password:
            raise ValueError("password do not match! please make sure that your password is consistent")
        return model
    @field_validator('address')
    def validate_address(cls,v):
        if not v.strip():
            raise ValueError("Address cannot be empty, please enter your current home address")
        return v

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/user/")
def register_user(user: Register, db: Session = Depends(get_db)):

    try:
        hashed_pass = bcrypt.hash(user.password[:72])


        new_user = User(
            user_name = user.user_name,
            email = user.email,
            contact_num = user.contact_num,
            address=user.address,
            password = hashed_pass,
            
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"user_id": new_user.user_id, "message": "Registration Success, new user has been created"}
    except Exception as e:
        print(f"server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail= "Internal server error, please try again later"
            )
