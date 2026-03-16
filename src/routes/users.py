from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.users import CRUD_USERS
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.schemas.users import (
    UserCreate, UserLogin, UserResponse, TokenResponse, BootstrapResponse,
    UpdatePasswordRequest, UpdateContactRequest, UpdateUserLogoResponse
)
from src.utils.jwt import JWT_TOKEN
from src.utils.image_processor import ImageProcessor
from src.utils.s3_manager import S3Manager

router = APIRouter()
db_init = DATABASE_INIT()

@router.post("/bootstrap", response_model=BootstrapResponse)
def bootstrap_first_user(user_data: UserCreate, db: Session = Depends(db_init.get_db)):
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
def login(credentials: UserLogin, db: Session = Depends(db_init.get_db)):
    """Autenticar usuario y obtener token JWT"""
    crud = CRUD_USERS(db)
    return crud.login(credentials.username, credentials.password)

@router.get("", response_model=list[UserResponse])
def list_users(user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Listar todos los usuarios activos (requiere autenticación)"""
    crud = CRUD_USERS(db)
    return crud.get_users()

@router.post("", response_model=UserResponse)
def create_user(user_data: UserCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Crear nuevo usuario (requiere autenticación EDITOR/OWNER)"""
    crud = CRUD_USERS(db)
    created_user = crud.create_user(user_data.model_dump(), user)
    return created_user

@router.post("/{user_id}/logo", response_model=UpdateUserLogoResponse)
def upload_user_logo(
    user_id: int,
    file: UploadFile = File(...),
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Subir o actualizar logo de usuario a AWS S3
    
    - Solo el usuario dueño o OWNER pueden actualizar su propio logo
    - Formato soportado: JPEG, PNG, WebP, GIF
    - Tamaño máximo: 10 MB
    """
    try:
        # Verificar autorización: solo el usuario o OWNER pueden actualizar su propio logo
        from src.models.enums import UserRolEnum
        if current_user.id != user_id and current_user.rol != UserRolEnum.OWNER:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar este logo")
        
        # Verificar que el usuario existe
        crud = CRUD_USERS(db)
        user = crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Leer contenido del archivo
        file_content = file.file.read()
        
        # Validar imagen
        ImageProcessor.validate_image(file_content, file.filename or "logo")
        
        # Procesar imagen a WebP
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "logo")
        
        # Subir a S3
        s3_manager = S3Manager()
        logo_url = s3_manager.upload_user_logo(webp_content, user_id, file.filename or "logo")
        
        # Eliminar logo anterior si existe
        if user.logo:
            s3_manager.delete_file(user.logo)
        
        # Actualizar en BD
        updated_user = crud.update_user_logo(user_id, logo_url)
        
        return {
            "id": updated_user.id,
            "name": updated_user.name,
            "logo": updated_user.logo,
            "message": f"Logo actualizado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo logo: {str(e)}")

@router.patch("/{user_id}/password", response_model=UserResponse)
def update_password(
    user_id: int,
    password_data: UpdatePasswordRequest,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar contraseña del usuario
    
    - Solo el usuario dueño o OWNER pueden actualizar su contraseña
    - Se requiere la contraseña actual para validación
    """
    try:
        # Verificar autorización: solo el usuario o OWNER pueden actualizar su propia contraseña
        from src.models.enums import UserRolEnum
        if current_user.id != user_id and current_user.rol != UserRolEnum.OWNER:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar esta contraseña")
        
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_password(
            user_id,
            password_data.current_password,
            password_data.new_password
        )
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando contraseña: {str(e)}")

@router.patch("/{user_id}/contact", response_model=UserResponse)
def update_contact(
    user_id: int,
    contact_data: UpdateContactRequest,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar contacto del usuario
    
    - Solo el usuario dueño o OWNER pueden actualizar su contacto
    """
    try:
        # Verificar autorización: solo el usuario o OWNER pueden actualizar su propio contacto
        from src.models.enums import UserRolEnum
        if current_user.id != user_id and current_user.rol != UserRolEnum.OWNER:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar este contacto")
        
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_contact(user_id, contact_data.contact)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando contacto: {str(e)}")
