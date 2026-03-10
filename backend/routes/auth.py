from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.users import User
from dependencies import DbDep, verify_password, hash_password, create_access_token
from schemas.auth import UserLogin, Register, TokenResponse, RegisterResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DbDep = None):
    user = db.query(User).filter(User.email == form_data.username.lower()).first()

   
    if not user or not verify_password(form_data.password, user.password):
      
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 3. Create Token
    token = create_access_token(user_id=str(user.user_id))
    
    # 4. DAPAT MAY RETURN DITO NA NAG-MAMATCH SA TokenResponse
    return {
        "access_token": token, 
        "token_type": "bearer"
    }

@router.post("/user/", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: Register, db: DbDep):
    new_user = User(
        user_name=payload.user_name,
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists",
        )

    db.refresh(new_user)
    return RegisterResponse(user_id=new_user.user_id)