from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserMe
from app.cruds.user import create_user, authenticate_user, get_user_by_email
from app.core.security import create_access_token, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, не существует ли уже пользователь с таким email
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаем нового пользователя
    db_user = create_user(db=db, user=user)
    
    # Создаем токен
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        token=access_token,
        created_at=db_user.created_at
    )


@router.post("/login/", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    # Аутентифицируем пользователя
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем новый токен
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        token=access_token,
        created_at=db_user.created_at
    )


@router.get("/users/me/", response_model=UserMe)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return UserMe(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at
    ) 