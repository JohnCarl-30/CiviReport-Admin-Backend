from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from models.users import User
from dependencies import DbDep, verify_password, hash_password, create_access_token, DUMMY_HASH
from schemas.auth import Register, TokenResponse, RegisterResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(db: DbDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username.lower()).first()

    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user_id=str(user.user_id))

    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "Login successful",
    }


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: Register, db: DbDep):

    user_name = f"{payload.first_name} {payload.last_name}"
    new_user = User(
        user_name=user_name,
        email=payload.email.lower(),
        contact_num=payload.contact_num,
        address=payload.address,
        password=hash_password(payload.password),
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists",
        )

    return RegisterResponse(user_id=new_user.user_id)