from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mods_collections import CRUD_MODS_COLLECTION
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.mods_collections import ModsCollectionResponse, ModsCollectionCreate, ModsCollectionResponseWithCollection
from src.utils.response_builder import ResponseBuilder, resolve_user_ids
from src.models.enums import UserRolEnum
from src.models.mods import Mod
from src.models.collection import Collection
from src.background_tasks import notify_mod_added_to_collection, notify_mod_removed_from_collection, notify_mods_collection_status_changed

router = APIRouter()
db_init = DATABASE_INIT()


class UpdateModsCollectionStatus(BaseModel):
    is_active: bool


class UpdateModsCollectionId(BaseModel):
    collection_id: int


@router.get("")
def list_mods_collections(
    db: Session = Depends(db_init.get_db)
):
    """
    Listar todas las relaciones mods-colecciones activas (públicamente disponible)
    """
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mods_collections_with_collection_name_all()
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mods_collections:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Relaciones mods-colecciones obtenidas exitosamente",
        "data": response_data
    }


@router.get("/admin/all")
def list_mods_collections_admin(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las relaciones incluyendo inactivas (solo OWNER/EDITOR)
    """
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mods_collections_admin_with_collection_name_all()
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mods_collections:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Relaciones mods-colecciones obtenidas exitosamente (incluyendo inactivas)",
        "data": response_data
    }


@router.get("/{mods_collection_id}")
def get_mods_collection(
    mods_collection_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener una relación mods-colecciones específica (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    result = crud.get_mods_collection_with_collection_name(mods_collection_id)
    if not result:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    resource, info = result
    info_resolved = resolve_user_ids(info, db)
    
    response_data = {
        "resource": resource,
        "info": info_resolved
    }
    
    return ResponseBuilder.success(
        data=response_data,
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
    result = crud.get_mods_collection_admin_with_collection_name(mods_collection_id)
    if not result:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    resource, info = result
    info_resolved = resolve_user_ids(info, db)
    
    response_data = {
        "resource": resource,
        "info": info_resolved
    }
    
    return ResponseBuilder.success(
        data=response_data,
        message="Relación obtenida exitosamente"
    )


@router.get("/mod/{mod_id}")
def get_mod_collections(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todas las colecciones de un mod (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mod_collections_with_collection_name(mod_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mods_collections:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Colecciones del mod obtenidas exitosamente",
        "data": response_data
    }


@router.get("/admin/mod/{mod_id}")
def get_mod_collections_admin(
    mod_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener todas las colecciones de un mod incluyendo inactivas (solo OWNER/EDITOR)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_mod_collections_admin_with_collection_name(mod_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mods_collections:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Colecciones del mod obtenidas exitosamente (incluyendo inactivas)",
        "data": response_data
    }


@router.get("/collection/{collection_id}")
def get_collection_mods(
    collection_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todos los mods de una colección (públicamente disponible)"""
    crud = CRUD_MODS_COLLECTION(db)
    mods_collections = crud.get_collection_mods_with_collection_name(collection_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mods_collections:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Mods de la colección obtenidos exitosamente",
        "data": response_data
    }


@router.post("")
def add_mod_to_collection(
    data: ModsCollectionCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Agregar un mod a una colección (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para agregar mods a colecciones")
    
    crud = CRUD_MODS_COLLECTION(db)
    mod, collection, mods_collection = crud.add_mod_to_collection(data.mod_id, data.collection_id)
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_mod_added_to_collection,
        mod=mod,
        collection=collection,
        user=user
    )
    
    return ResponseBuilder.created(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Mod agregado a colección exitosamente",
        db=db
    )


@router.patch("/admin/status/{mods_collection_id}")
def update_mods_collection_status(
    mods_collection_id: int,
    data: UpdateModsCollectionStatus,
    user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar el estado is_active de una relación mods-colecciones (solo OWNER/EDITOR)"""
    
    crud = CRUD_MODS_COLLECTION(db)
    mods_collection = crud.update_mods_collection_status(mods_collection_id, data.is_active)
    
    # Get mod and collection for Discord notification
    mod = db.query(Mod).filter(Mod.id == mods_collection.mod_id).first()
    collection = db.query(Collection).filter(Collection.id == mods_collection.collection_id).first()
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_mods_collection_status_changed,
        mod=mod,
        collection=collection,
        user=user,
        is_active=data.is_active
    )
    
    return ResponseBuilder.updated(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Estado de la relación actualizado exitosamente",
        db=db
    )


@router.put("/{mods_collection_id}")
def update_mods_collection_id(
    mods_collection_id: int,
    data: UpdateModsCollectionId,
    user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar el id_collection de una relación mods-colecciones (solo OWNER/EDITOR)"""
    
    crud = CRUD_MODS_COLLECTION(db)
    
    # Obtener la relación antigua para obtener la colección anterior
    old_mods_collection = crud.get_mods_collection_admin(mods_collection_id)
    if not old_mods_collection:
        raise HTTPException(status_code=404, detail="Relación mods-colecciones no encontrada")
    
    old_collection = db.query(Collection).filter(Collection.id == old_mods_collection.collection_id).first()
    
    # Actualizar la colección
    mods_collection = crud.update_collection_id(mods_collection_id, data.collection_id)
    
    # Get mod and new collection for Discord notification
    mod = db.query(Mod).filter(Mod.id == mods_collection.mod_id).first()
    new_collection = db.query(Collection).filter(Collection.id == mods_collection.collection_id).first()
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_mod_removed_from_collection,
        mod=mod,
        collection=old_collection,
        user=user
    )
    background_tasks.add_task(
        notify_mod_added_to_collection,
        mod=mod,
        collection=new_collection,
        user=user
    )
    
    return ResponseBuilder.updated(
        data=ModsCollectionResponse.model_validate(mods_collection),
        message="Colección de la relación actualizada exitosamente",
        db=db
    )
