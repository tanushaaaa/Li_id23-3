from fastapi import APIRouter, Depends
from app.db.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/")
def read_current_user():
    return {"message": "User info would go here"}
