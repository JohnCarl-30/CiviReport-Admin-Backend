from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session 
from database import SessionLocal, engine, Base 
from pydantic import BaseModel
from model import User
from passlib.context import CryptContext


Base.metadata.create_all(bind = engine)

app = FastAPI()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



class UserLogin(BaseModel):
    email: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(user_login: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(status_code=400, detail = "Invalid Email")
    if not pwd_context.verify(user_login.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    return {"message" : "Login success!"}

