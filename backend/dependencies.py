from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = ...
    if not user:
        raise HTTPException(status_code=401, detail="Invalid auth")
    return user