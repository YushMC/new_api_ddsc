from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.collections import CRUD_COLLECTION
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.collections import CollectionResponse, CollectionCreate, CollectionUpdate, CollectionSeasonalUpdate, CollectionDatesUpdate, CollectionStatusRequest
from src.utils.response_builder import ResponseBuilder
from src.models.enums import UserRolEnum
from src.background_tasks import (
    notify_collection_created, 
    notify_collection_updated
)

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def list_collections(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados.")
):
    """
    Listar todas las colecciones activas (públicamente disponible)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_collections(skip, limit)
    return ResponseBuilder.list_response(
        data=[CollectionResponse.model_validate(c) for c in collections],
        message="Colecciones obtenidas exitosamente"
    )


@router.get("/admin/all")
def list_collections_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados."),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las colecciones incluyendo inactivas (solo OWNER/EDITOR)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_collections_admin(skip, limit)
    return ResponseBuilder.list_response(
        data=[CollectionResponse.model_validate(c) for c in collections],
        message="Colecciones obtenidas exitosamente (incluyendo inactivas)"
    )


@router.get("/{collection_id}")
def get_collection(
    collection_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener una colección específica (públicamente disponible)"""
    crud = CRUD_COLLECTION(db)
    collection = crud.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return ResponseBuilder.success(
        data=CollectionResponse.model_validate(collection),
        message="Colección obtenida exitosamente",
        db=db
    )


@router.get("/admin/{collection_id}")
def get_collection_admin(
    collection_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener una colección incluyendo si está inactiva (solo OWNER/EDITOR)"""
    crud = CRUD_COLLECTION(db)
    collection = crud.get_collection_admin(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return ResponseBuilder.success(
        data=CollectionResponse.model_validate(collection),
        message="Colección obtenida exitosamente",
        db=db
    )


@router.post("")
def create_collection(
    data: CollectionCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Crear nueva colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.create_collection(data.name, data.description)
    
    # Agregar notificación a Discord
    background_tasks.add_task(notify_collection_created, collection, user)
    
    return ResponseBuilder.created(
        data=CollectionResponse.model_validate(collection),
        message="Colección creada exitosamente",
        db=db
    )


@router.put("/{collection_id}")
def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection, changes = crud.update_collection(collection_id, data.name, data.description, data.is_seasonal, data.start_date, data.end_date)
    
    # Agregar notificación a Discord si hay cambios
    if changes:
        background_tasks.add_task(notify_collection_updated, collection, user, changes)
    
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message="Colección actualizada exitosamente",
        db=db
    )


@router.patch("/status/{collection_id}")
def update_collection_status(
    collection_id: int,
    data: CollectionStatusRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Activar/desactivar colección (solo OWNER/EDITOR)
    
    Enviar { "is_active": true } para activar o { "is_active": false } para desactivar
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para cambiar el estado de colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.update_collection_status(collection_id, data.is_active)
    
    status_text = "activada" if data.is_active else "desactivada"
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message=f"Colección {status_text} exitosamente",
        db=db
    )


@router.patch("/seasonal/{collection_id}")
def update_collection_seasonal(
    collection_id: int,
    data: CollectionSeasonalUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Actualizar si la colección es por temporada (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.update_seasonal(collection_id, data.is_seasonal)
    
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message="Estado de temporada actualizado exitosamente",
        db=db
    )


@router.patch("/dates/{collection_id}")
def update_collection_dates(
    collection_id: int,
    data: CollectionDatesUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Actualizar fechas de temporada de la colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.update_dates(collection_id, data.start_date, data.end_date)
    
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message="Fechas de temporada actualizadas exitosamente",
        db=db
    )
