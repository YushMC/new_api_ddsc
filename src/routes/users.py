from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.users import CRUD_USERS
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.schemas.users import UserCreate, UserLogin, UserResponse, TokenResponse, BootstrapResponse
from src.utils.jwt import JWT_TOKEN

router = APIRouter()
get_db = DATABASE_INIT().get_db

@router.post("/bootstrap", response_model=BootstrapResponse)
def bootstrap_first_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Crear el primer usuario OWNER (solo funciona si la BD está vacía)
    
    ⚠️ IMPORTANTE: Este endpoint solo funciona UNA SOLA VEZ cuando la BD está vacía.
    Una vez creado el primer usuario, esta ruta retornará error 403.
    
    Parámetros:
    - name: nombre de usuario (case-sensitive)
    - password: contraseña (mínimo 6 caracteres)
    - contact: email o contacto (opcional)
    - logo: URL del logo (opcional)
    
    Retorna:
    - user: datos del usuario creado
    - access_token: token JWT para usar en próximas solicitudes
    - token_type: tipo de token (bearer)
    - message: confirmación de creación
    - warning: aviso de que esta ruta ya no estará disponible
    """
    try:
        crud = CRUD_USERS(db)
        
        # Crear primer usuario como OWNER
        created_user = crud.create_first_owner(user_data.model_dump())
        
        # Generar token JWT
        jwt_handler = JWT_TOKEN()
        token = jwt_handler.create_token(user=created_user)
        
        return {
            "user": created_user,
            "access_token": token,
            "token_type": "bearer",
            "message": f"Usuario OWNER '{created_user.name}' creado exitosamente",
            "warning": "Esta ruta (POST /users/bootstrap) ya no estará disponible para futuras solicitudes. Use POST /users/login para autenticarse."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {str(e)}")

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
