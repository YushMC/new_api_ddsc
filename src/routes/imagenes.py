from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.imagenes import CRUD_IMAGE
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.models.enums import UserRolEnum, ImageTypeEnum
from src.models.imagen import Image
from src.models.mods import Mod
from src.schemas.imagenes import ImageResponse
from src.utils.image_processor import ImageProcessor
from src.utils.s3_manager import S3Manager
from src.utils.response_builder import ResponseBuilder
from src.background_tasks import notify_image_uploaded, notify_image_replaced, notify_image_deleted
from typing import cast

router = APIRouter()
db_init = DATABASE_INIT()

# ============================================================================
# RUTAS GENÉRICAS (mantener para compatibilidad)
# ============================================================================

@router.get("/mod/{mod_id}")
def get_images_by_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener todas las imágenes de un mod (públicamente disponible)"""
    
    crud = CRUD_IMAGE(db)
    images = crud.get_imagenes_mod(mod_id)
    
    # Preparar cada imagen con la estructura info
    prepared_images = []
    for img in images:
        img_dict = ResponseBuilder._create_response_with_info(
            ImageResponse.model_validate(img),
            "success",
            "",
            force_info=True
        )
        prepared_images.append(img_dict["data"])
    
    return {
        "response": "success",
        "message": "Imágenes obtenidas exitosamente",
        "data": prepared_images
    }

@router.get("/admin/all")
def list_images_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todas las imágenes incluyendo inactivas (solo para OWNER/EDITOR)"""
    crud = CRUD_IMAGE(db)
    images = crud.get_imagenes_admin(skip, limit)
    
    # Preparar cada imagen con la estructura info
    prepared_images = []
    for img in images:
        img_dict = ResponseBuilder._create_response_with_info(
            ImageResponse.model_validate(img),
            "success",
            "",
            force_info=True
        )
        prepared_images.append(img_dict["data"])
    
    return {
        "response": "success",
        "message": "Imágenes obtenidas exitosamente (incluyendo inactivas)",
        "data": prepared_images
    }

@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener una imagen específica (públicamente disponible)"""
    
    crud = CRUD_IMAGE(db)
    image = crud.get_imagen(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return ResponseBuilder.success(
        data=ImageResponse.model_validate(image),
        message="Imagen obtenida exitosamente",
        force_info=True
    )

@router.get("/admin/{image_id}")
def get_image_admin(
    image_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener una imagen específica incluyendo inactivas (solo OWNER/EDITOR)"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return ResponseBuilder.success(
        data=ImageResponse.model_validate(image),
        message="Imagen obtenida exitosamente",
        force_info=True
    )

@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Eliminar una imagen (soft delete, requiere autenticación EDITOR/OWNER)
    
    Nota: La imagen se marca como inactiva en BD pero se mantiene en S3
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar imágenes")
    
    crud = CRUD_IMAGE(db)
    image = crud.delete_imagen(image_id)
    
    # Get mod for notification
    mod = db.query(Mod).filter(Mod.id == image.mod_id).first()
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_image_deleted,
        image=image,
        mod=mod,
        user=user
    )
    
    return ResponseBuilder.deleted(message="Imagen eliminada exitosamente")

# ============================================================================
# RUTAS ESPECÍFICAS POR TIPO DE IMAGEN
# ============================================================================

@router.post("/logo/{mod_id}")
async def upload_logo(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
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
        
        # Verificar que el mod existe
        mod = db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
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
        
        image = crud.create_imagen(image_data)
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_uploaded,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.created(
            data=ImageResponse.model_validate(image),
            message="Logo subido exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando logo: {str(e)}"
        )

@router.post("/main/{mod_id}")
async def upload_main(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
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
        
        # Verificar que el mod existe
        mod = db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
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
        
        image = crud.create_imagen(image_data)
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_uploaded,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.created(
            data=ImageResponse.model_validate(image),
            message="Imagen principal subida exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen main: {str(e)}"
        )

@router.post("/screenshots/{mod_id}")
async def upload_screenshot(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
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
        
        # Verificar que el mod existe
        mod = db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
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
        
        image = crud.create_imagen(image_data)
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_uploaded,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.created(
            data=ImageResponse.model_validate(image),
            message="Captura de pantalla subida exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando screenshot: {str(e)}"
        )

# ============================================================================
# RUTAS PUT PARA ACTUALIZAR IMÁGENES (reemplazar anterior)
# ============================================================================

@router.put("/logo/{mod_id}")
async def update_logo(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Actualizar logo del mod (reemplaza el anterior)
    
    - Obtiene el logo actual
    - Elimina el anterior de S3
    - Procesa nueva imagen a WebP
    - Sube a S3
    - Actualiza en BD
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        s3_manager = S3Manager()
        
        # Obtener mod
        mod = db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Obtener logo actual
        existing_logo = crud.get_imagen_by_mod_and_type(mod_id, ImageTypeEnum.LOGO)
        if not existing_logo:
            raise HTTPException(status_code=404, detail="No existe logo para este mod")
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "logo")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "logo")
        
        # Eliminar logo anterior de S3
        s3_manager.delete_file(cast(str, existing_logo.url))
        
        # Subir nueva imagen a S3
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            ImageTypeEnum.LOGO.value,
            file.filename or "logo"
        )
        
        # Actualizar en BD
        image = crud.update_imagen(cast(int, existing_logo.id), {"url": image_url})
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_replaced,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.updated(
            data=ImageResponse.model_validate(image),
            message="Logo actualizado exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando logo: {str(e)}"
        )

@router.put("/main/{mod_id}")
async def update_main(
    mod_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Actualizar imagen principal del mod (reemplaza la anterior)
    
    - Obtiene la imagen actual
    - Elimina la anterior de S3
    - Procesa nueva imagen a WebP
    - Sube a S3
    - Actualiza en BD
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        s3_manager = S3Manager()
        
        # Obtener mod
        mod = db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Obtener imagen main actual
        existing_main = crud.get_imagen_by_mod_and_type(mod_id, ImageTypeEnum.MAIN)
        if not existing_main:
            raise HTTPException(status_code=404, detail="No existe imagen main para este mod")
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "main")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "main")
        
        # Eliminar imagen anterior de S3
        s3_manager.delete_file(cast(str, existing_main.url))
        
        # Subir nueva imagen a S3
        image_url = s3_manager.upload_file(
            webp_content,
            mod_id,
            ImageTypeEnum.MAIN.value,
            file.filename or "main"
        )
        
        # Actualizar en BD
        image = crud.update_imagen(cast(int, existing_main.id), {"url": image_url})
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_replaced,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.updated(
            data=ImageResponse.model_validate(image),
            message="Imagen principal actualizada exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando imagen main: {str(e)}"
        )

@router.put("/screenshots/{image_id}")
async def update_screenshot(
    image_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Actualizar una captura de pantalla específica (reemplaza la anterior)
    
    - Obtiene la screenshot por ID
    - Elimina la anterior de S3
    - Procesa nueva imagen a WebP
    - Sube a S3
    - Actualiza en BD
    
    Requiere autenticación EDITOR/OWNER
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar imágenes")
    
    try:
        crud = CRUD_IMAGE(db)
        s3_manager = S3Manager()
        
        # Obtener screenshot actual
        existing_screenshot = crud.get_imagen(image_id)
        if not existing_screenshot or cast(str, existing_screenshot.type) != ImageTypeEnum.SCREENSHOT.value:
            raise HTTPException(status_code=404, detail="Screenshot no encontrada")
        
        # Obtener mod
        mod = db.query(Mod).filter(Mod.id == existing_screenshot.mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Procesar imagen
        file_content = await file.read()
        ImageProcessor.validate_image(file_content, file.filename or "screenshot")
        webp_content = ImageProcessor.process_to_webp(file_content, file.filename or "screenshot")
        
        # Eliminar screenshot anterior de S3
        s3_manager.delete_file(cast(str, existing_screenshot.url))
        
        # Subir nueva imagen a S3
        image_url = s3_manager.upload_file(
            webp_content,
            cast(int, existing_screenshot.mod_id),
            ImageTypeEnum.SCREENSHOT.value,
            file.filename or "screenshot"
        )
        
        # Actualizar en BD
        image = crud.update_imagen(image_id, {"url": image_url})
        
        # Send Discord notification (non-blocking)
        background_tasks.add_task(
            notify_image_replaced,
            image=image,
            mod=mod,
            user=user
        )
        
        return ResponseBuilder.updated(
            data=ImageResponse.model_validate(image),
            message="Screenshot actualizada exitosamente",
            force_info=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando screenshot: {str(e)}"
        )

