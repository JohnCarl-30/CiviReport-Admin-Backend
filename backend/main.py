from fastapi import FastAPI
from database import engine, Base
from routes import auth, complaint, forgot_password
from fastapi.security import HTTPBearer

Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="CiviReport Admin API",
    description="Backend API for the CiviReport platform — a barangay complaint management system that allows residents to register, log in, and submit complaint tickets with media attachments.",
    version="1.0.0",
    contact={
        "name": "CiviReport Team",
    },
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(complaint.router, prefix="/complaints", tags=["Complaints"])
app.include_router(forgot_password.router, prefix="/auth", tags=["Authentication"])
