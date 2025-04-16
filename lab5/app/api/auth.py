from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserOut
from app.cruds import user as user_crud
from app.core.security import create_access_token
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    existing = user_crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = user_crud.create_user(db, user)
    token = create_access_token(data={"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}
