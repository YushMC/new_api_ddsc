from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.imagenes import CRUD_IMAGE
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.models.enums import UserRolEnum, ImageTypeEnum
from src.schemas.imagenes import ImageResponse
from src.utils.image_processor import ImageProcessor
from src.utils.s3_manager import S3Manager

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
async def create_image(
    mod_id: int = Form(...),
    image_type: ImageTypeEnum = Form(...),
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear nueva imagen para un mod
    
    - Lee el archivo subido
    - Procesa la imagen (valida, redimensiona, comprime)
    - Convierte a WebP
    - Sube a AWS S3
    - Guarda referencia en la BD
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear imágenes")
    
    try:
        # 1. Leer archivo
        file_content = await file.read()
        
        # 2. Validar imagen
        ImageProcessor.validate_image(file_content, file.filename or "image")
        
        # 3. Procesar a WebP
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "image")
        
        # 4. Subir a S3
        s3_manager = S3Manager()
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            image_type.value,
            file.filename or "image"
        )
        
        # 5. Guardar en BD
        crud = CRUD_IMAGE(db)
        image_data = {
            "mod_id": mod_id,
            "url": image_url,
            "type": image_type
        }
        
        return crud.create_imagen(image_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )

@router.put("/{image_id}", response_model=ImageResponse)
def update_image(image_id: int, image_data: dict, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualizar una imagen (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar imágenes")
    
    crud = CRUD_IMAGE(db)
    return crud.update_imagen(image_id, image_data)

@router.delete("/{image_id}")
def delete_image(image_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Eliminar una imagen (soft delete, requiere autenticación EDITOR/OWNER)
    
    Nota: La imagen se marca como inactiva en BD pero se mantiene en S3
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar imágenes")
    
    crud = CRUD_IMAGE(db)
    crud.delete_imagen(image_id)
    return {"message": "Imagen eliminada"}

