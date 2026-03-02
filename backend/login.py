from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session 
from database import SessionLocal, engine, Base 
from pydantic import BaseModel
from models.users import User
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
    try: 
        user = db.query(User).filter(User.email == user_login.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Invalid Email, please double check your email")
        if not pwd_context.verify(user_login.password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password, please double check your password")
        
        return {"message" : "Login successfully!"}
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Internal server error. Please try again later."
        )

