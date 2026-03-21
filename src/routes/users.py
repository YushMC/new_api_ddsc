from typing import cast

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.users import CRUD_USERS
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.models.enums import UserRolEnum
from src.schemas.users import (
    UserCreate, UserLogin, UserResponse, TokenResponse, BootstrapResponse,
    UpdatePasswordRequest, UpdateContactRequest, UpdateUserLogoResponse,
    UpdateProfileRequest, UpdateRoleRequest, AdminRestorePasswordRequest
)
from src.utils.jwt import JWT_TOKEN
from src.utils.image_processor import ImageProcessor
from src.utils.s3_manager import S3Manager
from src.utils.response_builder import ResponseBuilder

router = APIRouter()
db_init = DATABASE_INIT()

@router.post("/bootstrap")
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
    
    Retorna respuesta con estructura: {response, message, data}
    """
    try:
        crud = CRUD_USERS(db)
        
        # Crear primer usuario como OWNER
        created_user = crud.create_first_owner(user_data.model_dump())
        
        # Generar token JWT
        jwt_handler = JWT_TOKEN()
        token = jwt_handler.create_token(user=created_user)
        
        response_data = {
            "user": UserResponse.model_validate(created_user),
            "access_token": token,
            "token_type": "bearer"
        }
        
        return ResponseBuilder.created(
            data=response_data,
            message="Usuario OWNER creado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {str(e)}")

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(db_init.get_db)):
    """Autenticar usuario y obtener token JWT"""
    crud = CRUD_USERS(db)
    login_result = crud.login(credentials.username, credentials.password)
    return ResponseBuilder.success(
        data=login_result,
        message="Autenticación exitosa"
    )

@router.get("")
def list_users(user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Listar todos los usuarios activos (requiere token válido - cualquier rol)"""
    crud = CRUD_USERS(db)
    users = crud.get_users()
    return ResponseBuilder.list_response(
        data=[UserResponse.model_validate(u) for u in users],
        message="Usuarios obtenidos exitosamente"
    )

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un usuario específico (públicamente disponible sin autenticación)"""
    crud = CRUD_USERS(db)
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return ResponseBuilder.success(
        data=UserResponse.model_validate(user),
        message="Usuario obtenido exitosamente"
    )

@router.get("/admin/all")
def list_users_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todos los usuarios incluyendo inactivos (solo para OWNER/EDITOR)"""
    crud = CRUD_USERS(db)
    users = crud.get_users_admin(skip, limit)
    return ResponseBuilder.list_response(
        data=[UserResponse.model_validate(u) for u in users],
        message="Usuarios obtenidos exitosamente (incluyendo inactivos)"
    )

@router.post("")
def create_user(user_data: UserCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """
    Crear nuevo usuario (requiere autenticación EDITOR/OWNER)
    
    Retorna el usuario creado junto con un token de acceso como si hiciera login
    """
    crud = CRUD_USERS(db)
    created_user = crud.create_user(user_data.model_dump(), user)
    
    # Generar token JWT para el nuevo usuario
    jwt_handler = JWT_TOKEN()
    token = jwt_handler.create_token(user=created_user)
    
    response_data = {
        "user": UserResponse.model_validate(created_user),
        "access_token": token,
        "token_type": "bearer"
    }
    
    return ResponseBuilder.created(
        data=response_data,
        message="Usuario creado exitosamente. Token generado para login automático."
    )

@router.post("/logo")
def upload_user_logo(
    file: UploadFile = File(...),
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Subir logo de usuario a AWS S3
    
    - El usuario se identifica desde el token
    - Formato soportado: JPEG, PNG, WebP, GIF
    - Tamaño máximo: 10 MB
    """
    try:
        user_id = current_user.id
        crud = CRUD_USERS(db)
        user = crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        file_content = file.file.read()
        
        ImageProcessor.validate_image(file_content, file.filename or "logo")
        
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "logo")
        
        s3_manager = S3Manager()
        logo_url = s3_manager.upload_user_logo(webp_content, user_id, file.filename or "logo")
        
        if cast(str, user.logo):
            s3_manager.delete_file(cast(str, user.logo))
        
        updated_user = crud.update_user_logo(user_id, logo_url)
        
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Logo actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo logo: {str(e)}")

@router.patch("/logo")
def update_user_logo(
    file: UploadFile = File(...),
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar logo de usuario en AWS S3
    
    - El usuario se identifica desde el token
    - Formato soportado: JPEG, PNG, WebP, GIF
    - Tamaño máximo: 10 MB
    - Elimina el logo anterior si existe
    """
    try:
        user_id = current_user.id
        crud = CRUD_USERS(db)
        user = crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        file_content = file.file.read()
        
        ImageProcessor.validate_image(file_content, file.filename or "logo")
        
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "logo")
        
        s3_manager = S3Manager()
        
        if cast(str, user.logo):
            s3_manager.delete_file(cast(str, user.logo))
        
        logo_url = s3_manager.upload_user_logo(webp_content, user_id, file.filename or "logo")
        
        updated_user = crud.update_user_logo(user_id, logo_url)
        
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Logo actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando logo: {str(e)}")

@router.patch("/password")
def update_password(
    password_data: UpdatePasswordRequest,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar contraseña del usuario
    
    - El usuario se identifica desde el token
    - Se requiere la contraseña actual para validación
    """
    try:
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Contraseña actualizada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando contraseña: {str(e)}")

@router.patch("/contact")
def update_contact(
    contact_data: UpdateContactRequest,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar contacto del usuario
    
    - El usuario se identifica desde el token
    """
    try:
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_contact(current_user.id, contact_data.contact)
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Contacto actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando contacto: {str(e)}")

@router.put("/profile")
def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar perfil del usuario (name y about_me)
    
    - El usuario se identifica desde el token
    """
    try:
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_profile(
            current_user.id,
            profile_data.name,
            profile_data.about_me
        )
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Perfil actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil: {str(e)}")

@router.patch("/admin/role/{user_id}")
def update_user_role(
    user_id: int,
    role_data: UpdateRoleRequest,
    current_user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar el rol de un usuario (solo OWNER/EDITOR)
    
    - Solo usuarios con rol OWNER o EDITOR pueden cambiar roles
    - No se puede asignar el rol OWNER
    """
    try:
        from src.models.enums import UserRolEnum
        if role_data.role == UserRolEnum.OWNER:
            raise HTTPException(status_code=400, detail="No se puede asignar el rol OWNER")
        
        if current_user.id == user_id:
            raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")
        
        crud = CRUD_USERS(db)
        updated_user = crud.update_user_role(user_id, role_data.role)
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Rol actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando rol: {str(e)}")

@router.patch("/admin/restore/password/{user_id}")
def admin_restore_password(
    user_id: int,
    password_data: AdminRestorePasswordRequest,
    current_user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db)
):
    """
    Restaurar contraseña de un usuario (solo OWNER/EDITOR)
    
    - Permite a un administrador establecer una nueva contraseña para un usuario
    - No requiere la contraseña actual del usuario
    """
    try:
        crud = CRUD_USERS(db)
        updated_user = crud.admin_restore_password(user_id, password_data.new_password)
        return ResponseBuilder.updated(
            data=UserResponse.model_validate(updated_user),
            message="Contraseña restaurada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restaurando contraseña: {str(e)}")
