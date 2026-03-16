from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.users import CRUD_USERS
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.schemas.users import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter()
get_db = DATABASE_INIT().get_db

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Autenticar usuario y obtener token JWT"""
    crud = CRUD_USERS(db)
    return crud.login(credentials.username, credentials.password)

@router.get("", response_model=list[UserResponse])
def list_users(user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Listar todos los usuarios activos (requiere autenticación)"""
    crud = CRUD_USERS(db)
    return crud.get_users()

@router.post("", response_model=UserResponse)
def create_user(user_data: UserCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Crear nuevo usuario (requiere autenticación EDITOR/OWNER)"""
    crud = CRUD_USERS(db)
    created_user = crud.create_user(user_data.model_dump(), user)
    return created_user
