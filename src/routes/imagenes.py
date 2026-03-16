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
db_init = DATABASE_INIT()

# ============================================================================
# RUTAS GENÉRICAS (mantener para compatibilidad)
# ============================================================================

@router.get("/mod/{mod_id}", response_model=list[ImageResponse])
def get_images_by_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener todas las imágenes de un mod"""
    crud = CRUD_IMAGE(db)
    return crud.get_imagenes_mod(mod_id)

@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener una imagen específica"""
    crud = CRUD_IMAGE(db)
    return crud.get_imagen(image_id)

@router.delete("/{image_id}")
def delete_image(image_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """
    Eliminar una imagen (soft delete, requiere autenticación EDITOR/OWNER)
    
    Nota: La imagen se marca como inactiva en BD pero se mantiene en S3
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar imágenes")
    
    crud = CRUD_IMAGE(db)
    crud.delete_imagen(image_id)
    return {"message": "Imagen eliminada"}

# ============================================================================
# RUTAS ESPECÍFICAS POR TIPO DE IMAGEN
# ============================================================================

@router.post("/logo/{mod_id}", response_model=ImageResponse)
async def upload_logo(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Subir logo del mod (solo 1 imagen)
    
    - Valida que solo exista 1 logo por mod
    - Procesa a WebP
    - Sube a S3
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para subir imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        
        # Verificar que solo existe 1 logo por mod
        existing_logo = crud.get_imagen_by_mod_and_type(mod_id, ImageTypeEnum.LOGO)
        if existing_logo:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un logo para este mod. Usa DELETE para reemplazarlo."
            )
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "logo")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "logo")
        
        # Subir a S3
        s3_manager = S3Manager()
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            ImageTypeEnum.LOGO.value,
            file.filename or "logo"
        )
        
        # Guardar en BD
        image_data = {
            "mod_id": mod_id,
            "url": image_url,
            "type": ImageTypeEnum.LOGO
        }
        
        return crud.create_imagen(image_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando logo: {str(e)}"
        )

@router.post("/main/{mod_id}", response_model=ImageResponse)
async def upload_main(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Subir imagen principal del mod (solo 1 imagen)
    
    - Valida que solo exista 1 imagen main por mod
    - Procesa a WebP
    - Sube a S3
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para subir imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        
        # Verificar que solo existe 1 main image por mod
        existing_main = crud.get_imagen_by_mod_and_type(mod_id, ImageTypeEnum.MAIN)
        if existing_main:
            raise HTTPException(
                status_code=409,
                detail="Ya existe una imagen main para este mod. Usa DELETE para reemplazarla."
            )
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "main")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "main")
        
        # Subir a S3
        s3_manager = S3Manager()
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            ImageTypeEnum.MAIN.value,
            file.filename or "main"
        )
        
        # Guardar en BD
        image_data = {
            "mod_id": mod_id,
            "url": image_url,
            "type": ImageTypeEnum.MAIN
        }
        
        return crud.create_imagen(image_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen main: {str(e)}"
        )

@router.post("/screenshots/{mod_id}", response_model=ImageResponse)
async def upload_screenshot(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Subir captura de pantalla del mod (máximo 4 imágenes)
    
    - Valida que no excedan 4 screenshots
    - Procesa a WebP
    - Sube a S3
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para subir imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        
        # Verificar que no excedan 4 screenshots
        screenshot_count = crud.count_imagenes_by_mod_and_type(mod_id, ImageTypeEnum.SCREENSHOT)
        if screenshot_count >= 4:
            raise HTTPException(
                status_code=409,
                detail=f"Este mod ya tiene {screenshot_count} screenshots (máximo 4). Usa DELETE para reemplazar uno."
            )
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "screenshot")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "screenshot")
        
        # Subir a S3
        s3_manager = S3Manager()
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            ImageTypeEnum.SCREENSHOT.value,
            file.filename or "screenshot"
        )
        
        # Guardar en BD
        image_data = {
            "mod_id": mod_id,
            "url": image_url,
            "type": ImageTypeEnum.SCREENSHOT
        }
        
        return crud.create_imagen(image_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando screenshot: {str(e)}"
        )

