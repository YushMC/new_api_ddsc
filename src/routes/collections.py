from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.collections import CRUD_COLLECTION
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.collections import CollectionResponse, CollectionCreate, CollectionUpdate
from src.utils.response_builder import ResponseBuilder
from src.models.enums import UserRolEnum

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def list_collections(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20
):
    """Listar todas las colecciones activas (públicamente disponible)"""
    crud = CRUD_COLLECTION(db)
    collections = crud.get_collections(skip, limit)
    return ResponseBuilder.list_response(
        data=[CollectionResponse.model_validate(c) for c in collections],
        message="Colecciones obtenidas exitosamente"
    )


@router.get("/admin/all")
def list_collections_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todas las colecciones incluyendo inactivas (solo OWNER/EDITOR)"""
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
        message="Colección obtenida exitosamente"
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
        message="Colección obtenida exitosamente"
    )


@router.post("")
def create_collection(
    data: CollectionCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Crear nueva colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.create_collection(data.name, data.description)
    return ResponseBuilder.created(
        data=CollectionResponse.model_validate(collection),
        message="Colección creada exitosamente"
    )


@router.put("/{collection_id}")
def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Actualizar colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.update_collection(collection_id, data.name, data.description)
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message="Colección actualizada exitosamente"
    )


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Eliminar colección (soft delete - solo OWNER/EDITOR)
    
    Nota: La colección se marca como inactiva pero se mantiene en BD
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar colecciones")
    
    crud = CRUD_COLLECTION(db)
    crud.delete_collection(collection_id)
    return ResponseBuilder.deleted(message="Colección eliminada exitosamente")


@router.post("/{collection_id}/reactivate")
def reactivate_collection(
    collection_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Reactivar una colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para reactivar colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.reactivate_collection(collection_id)
    return ResponseBuilder.updated(
        data=CollectionResponse.model_validate(collection),
        message="Colección reactivada exitosamente"
    )
