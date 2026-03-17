from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mods_collections import CRUD_MODS_COLLECTION
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.mods_collections import ModsCollectionResponse, ModsCollectionCreate
from src.utils.response_builder import ResponseBuilder
from src.models.enums import UserRolEnum

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def list_mods_collections(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20
):
    """Listar todas las relaciones mods-colecciones activas (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mods_collections(skip, limit)
    return ResponseBuilder.list_response(
        data=[ModsCollectionResponse.model_validate(mc) for mc in mods_collections],
        message="Relaciones mods-colecciones obtenidas exitosamente"
    )


@router.get("/admin/all")
def list_mods_collections_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todas las relaciones incluyendo inactivas (solo OWNER/EDITOR)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mods_collections_admin(skip, limit)
    return ResponseBuilder.list_response(
        data=[ModsCollectionResponse.model_validate(mc) for mc in mods_collections],
        message="Relaciones mods-colecciones obtenidas exitosamente (incluyendo inactivas)"
    )


@router.get("/{mods_collection_id}")
def get_mods_collection(
    mods_collection_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener una relación mods-colecciones específica (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collection = crud.get_mods_collection(mods_collection_id)
    if not mods_collection:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return ResponseBuilder.success(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Relación obtenida exitosamente"
    )


@router.get("/admin/{mods_collection_id}")
def get_mods_collection_admin(
    mods_collection_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener una relación incluyendo si está inactiva (solo OWNER/EDITOR)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collection = crud.get_mods_collection_admin(mods_collection_id)
    if not mods_collection:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return ResponseBuilder.success(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Relación obtenida exitosamente"
    )


@router.get("/mod/{mod_id}")
def get_mod_collections(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todas las colecciones de un mod (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mod_collections(mod_id)
    return ResponseBuilder.list_response(
        data=[ModsCollectionResponse.model_validate(mc) for mc in mods_collections],
        message="Colecciones del mod obtenidas exitosamente"
    )


@router.get("/collection/{collection_id}")
def get_collection_mods(
    collection_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todos los mods de una colección (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_collection_mods(collection_id)
    return ResponseBuilder.list_response(
        data=[ModsCollectionResponse.model_validate(mc) for mc in mods_collections],
        message="Mods de la colección obtenidos exitosamente"
    )


@router.post("")
def add_mod_to_collection(
    data: ModsCollectionCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Agregar un mod a una colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para agregar mods a colecciones")
    
    crud = CRUD_MODS_COLLECTION(db)
    mods_collection = crud.add_mod_to_collection(data.mod_id, data.collection_id)
    return ResponseBuilder.created(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Mod agregado a colección exitosamente"
    )


@router.delete("/{mods_collection_id}")
def remove_mod_from_collection(
    mods_collection_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Remover un mod de una colección (soft delete - solo OWNER/EDITOR)
    
    Nota: La relación se marca como inactiva pero se mantiene en BD
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para remover mods de colecciones")
    
    crud = CRUD_MODS_COLLECTION(db)
    crud.remove_mod_from_collection(mods_collection_id)
    return ResponseBuilder.deleted(message="Mod removido de colección exitosamente")


@router.post("/{mods_collection_id}/reactivate")
def reactivate_mod_collection(
    mods_collection_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Reactivar un mod en colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para reactivar mods en colecciones")
    
    crud = CRUD_MODS_COLLECTION(db)
    mods_collection = crud.reactivate_mod_collection(mods_collection_id)
    return ResponseBuilder.updated(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Mod reactivado en colección exitosamente"
    )
