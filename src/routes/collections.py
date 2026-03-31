from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.collections import CRUD_COLLECTION
from src.services.mods_collections import CRUD_MODS_COLLECTION
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.collections import CollectionResponse, CollectionCreate, CollectionUpdate, CollectionSeasonalUpdate, CollectionDatesUpdate, CollectionStatusRequest
from src.schemas.mods import ModCommplete
from src.utils.response_builder import ResponseBuilder, resolve_user_ids
from src.models.enums import UserRolEnum
from src.models.mods import Mod
from src.models.collection import Collection
from src.background_tasks import (
    notify_collection_created, 
    notify_collection_updated,
    notify_collection_status_changed
)

router = APIRouter()
db_init = DATABASE_INIT()


def _prepare_mod_with_full_info(mod, db: Session):
    """Prepara un mod con información completa (info, imágenes, géneros, créditos)"""
    from src.schemas.imagenes import ImageResponse
    from src.schemas.generos import GenreResponse
    from src.services.mods import CRUD_MOD as ModCRUD
    
    mod_dict = ModCommplete.model_validate(mod).model_dump()
    
    # Organizar créditos si existen
    credits = ModCRUD._organize_credits(mod, db)
    mod_dict['credits'] = credits
    
    # Agregar imágenes activas si existen
    images = []
    if hasattr(mod, 'images') and mod.images:
        images = [
            ImageResponse.model_validate(img).model_dump()
            for img in mod.images if img.is_active
        ]
    mod_dict['images'] = images
    
    # Agregar géneros activos si existen
    genres = []
    mod_crud = ModCRUD(db)
    mod_genres = mod_crud.get_mod_genres(mod.id)
    if mod_genres:
        genres = [
            GenreResponse.model_validate(g).model_dump()
            for g in mod_genres
        ]
    mod_dict['genres'] = genres
    
    return mod_dict


def _enrich_collection_with_mods(collection, db: Session):
    """Enriquece una colección con sus mods completos"""
    collection_dict = CollectionResponse.model_validate(collection).model_dump()
    
    # Obtener todos los mods de esta colección
    crud_mods_collections = CRUD_MODS_COLLECTION(db)
    mods_collections = crud_mods_collections.get_collection_mods_with_collection_name(collection.id)
    
    mods = []
    for resource, info in mods_collections:
        mod = db.query(Mod).filter(Mod.id == resource['mod_id']).first()
        if mod:
            mod_info = _prepare_mod_with_full_info(mod, db)
            mods.append(mod_info)
    
    collection_dict['mods'] = mods
    
    # Resolver IDs de usuario a objetos en la colección
    collection_dict = resolve_user_ids(collection_dict, db)
    
    return collection_dict


@router.get("")
def list_collections(
    db: Session = Depends(db_init.get_db)
):
    """
    Listar todas las colecciones activas (públicamente disponible)
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_collections_all()
    
    prepared = []
    for c in collections:
        response_structure = ResponseBuilder._create_response_with_info(
            CollectionResponse.model_validate(c),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Colecciones obtenidas exitosamente",
        "data": prepared
    }


@router.get("/seasonal")
def list_seasonal_collections(
    db: Session = Depends(db_init.get_db)
):
    """
    Listar todas las colecciones estacionales activas sin paginación (públicamente disponible)
    
    Retorna solo colecciones con is_seasonal=true
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_seasonal_collections()
    
    prepared = []
    for c in collections:
        collection_with_mods = _enrich_collection_with_mods(c, db)
        prepared.append({
            "resource": collection_with_mods,
            "mods": collection_with_mods.pop('mods', [])
        })
    
    return {
        "response": "success",
        "message": "Colecciones estacionales obtenidas exitosamente",
        "data": prepared
    }


@router.get("/random-collections")
def get_random_collections(
    db: Session = Depends(db_init.get_db)
):
    """
    Obtener 3 colecciones aleatorias activas que NO sean estacionales (públicamente disponible)
    
    Retorna colecciones con is_seasonal=false al azar (máximo 3)
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_random_collections(limit=3)
    
    prepared = []
    for c in collections:
        collection_with_mods = _enrich_collection_with_mods(c, db)
        prepared.append({
            "resource": collection_with_mods,
            "mods": collection_with_mods.pop('mods', [])
        })
    
    return {
        "response": "success",
        "message": "Colecciones aleatorias obtenidas exitosamente",
        "data": prepared
    }


@router.get("/admin/all")
def list_collections_admin(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las colecciones incluyendo inactivas (solo OWNER/EDITOR)
    """
    crud = CRUD_COLLECTION(db)
    collections = crud.get_collections_admin_all()
    
    prepared = []
    for c in collections:
        response_structure = ResponseBuilder._create_response_with_info(
            CollectionResponse.model_validate(c),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Colecciones obtenidas exitosamente (incluyendo inactivas)",
        "data": prepared
    }


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
    collection = crud.create_collection(data.name, data.description, data.is_seasonal, data.start_date, data.end_date)
    
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
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Activar/desactivar colección (solo OWNER/EDITOR)
    
    Enviar { "is_active": true } para activar o { "is_active": false } para desactivar
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para cambiar el estado de colecciones")
    
    crud = CRUD_COLLECTION(db)
    collection = crud.update_collection_status(collection_id, data.is_active)
    
    # Notificar a Discord
    background_tasks.add_task(notify_collection_status_changed, collection, user, data.is_active)
    
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
