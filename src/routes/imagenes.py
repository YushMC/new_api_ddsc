from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.imagenes import CRUD_IMAGE
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.models.enums import UserRolEnum
from src.schemas.imagenes import ImageCreate, ImageResponse, ImageUpdate

router = APIRouter()
get_db = DATABASE_INIT().get_db

@router.get("/mod/{mod_id}", response_model=list[ImageResponse])
def get_images_by_mod(mod_id: int, db: Session = Depends(get_db)):
    """Obtener todas las imágenes de un mod"""
    crud = CRUD_IMAGE(db)
    return crud.get_imagenes_mod(mod_id)

@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """Obtener una imagen específica"""
    crud = CRUD_IMAGE(db)
    return crud.get_imagen(image_id)

@router.post("", response_model=ImageResponse)
def create_image(image_data: ImageCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Crear nueva imagen para un mod (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear imágenes")
    
    crud = CRUD_IMAGE(db)
    return crud.create_imagen(image_data.model_dump())

@router.put("/{image_id}", response_model=ImageResponse)
def update_image(image_id: int, image_data: ImageUpdate, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualizar una imagen (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar imágenes")
    
    crud = CRUD_IMAGE(db)
    return crud.update_imagen(image_id, image_data.model_dump(exclude_unset=True))

@router.delete("/{image_id}")
def delete_image(image_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar una imagen (soft delete, requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar imágenes")
    
    crud = CRUD_IMAGE(db)
    crud.delete_imagen(image_id)
    return {"message": "Imagen eliminada"}
