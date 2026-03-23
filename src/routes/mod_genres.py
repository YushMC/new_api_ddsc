from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mod_genres import CRUD_MOD_GENRE
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.mod_genres import ModGenreResponse, ModGenreCreate, ModGenreResponseWithGenre
from src.utils.response_builder import ResponseBuilder, resolve_user_ids
from src.models.enums import UserRolEnum
from src.models.mods import Mod
from src.models.generos import Genre
from src.background_tasks import notify_genres_added, notify_genres_removed

router = APIRouter()
db_init = DATABASE_INIT()


class UpdateModGenreStatus(BaseModel):
    is_active: bool


class UpdateModGenreId(BaseModel):
    genre_id: int


@router.get("")
def list_mod_genres(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados.")
):
    """
    Listar todas las relaciones mod-géneros activas (públicamente disponible)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_MOD_GENRE(db)
    mod_genres = crud.get_mod_genres_with_genre(skip, limit)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mod_genres:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Relaciones mod-géneros obtenidas exitosamente",
        "data": response_data
    }


@router.get("/admin/all")
def list_mod_genres_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados."),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las relaciones incluyendo inactivas (solo OWNER/EDITOR)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_MOD_GENRE(db)
    mod_genres = crud.get_mod_genres_admin_with_genre(skip, limit)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mod_genres:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Relaciones mod-géneros obtenidas exitosamente (incluyendo inactivas)",
        "data": response_data
    }


@router.get("/{mod_genre_id}")
def get_mod_genre(
    mod_genre_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener una relación mod-género específica (públicamente disponible)"""
    crud = CRUD_MOD_GENRE(db)
    result = crud.get_mod_genre_with_genre(mod_genre_id)
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


@router.get("/admin/{mod_genre_id}")
def get_mod_genre_admin(
    mod_genre_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener una relación incluyendo si está inactiva (solo OWNER/EDITOR)"""
    crud = CRUD_MOD_GENRE(db)
    result = crud.get_mod_genre_admin_with_genre(mod_genre_id)
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
def get_mod_all_genres(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todos los géneros de un mod (públicamente disponible)"""
    crud = CRUD_MOD_GENRE(db)
    mod_genres = crud.get_mod_all_genres_with_genre(mod_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mod_genres:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Géneros del mod obtenidos exitosamente",
        "data": response_data
    }


@router.get("/admin/mod/{mod_id}")
def get_mod_all_genres_admin(
    mod_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener todos los géneros de un mod incluyendo inactivos (solo OWNER/EDITOR)"""
    crud = CRUD_MOD_GENRE(db)
    mod_genres = crud.get_mod_all_genres_admin_with_genre(mod_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mod_genres:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Géneros del mod obtenidos exitosamente (incluyendo inactivos)",
        "data": response_data
    }


@router.get("/genre/{genre_id}")
def get_genre_all_mods(
    genre_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener todos los mods de un género (públicamente disponible)"""
    crud = CRUD_MOD_GENRE(db)
    mod_genres = crud.get_genre_all_mods_with_genre(genre_id)
    
    # Construir respuesta con structure (resource + info)
    response_data = []
    for resource, info in mod_genres:
        # Resolver IDs de usuario a objetos
        info_resolved = resolve_user_ids(info, db)
        response_data.append({
            "resource": resource,
            "info": info_resolved
        })
    
    return {
        "response": "success",
        "message": "Mods del género obtenidos exitosamente",
        "data": response_data
    }


@router.post("")
def add_genre_to_mod(
    data: ModGenreCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Agregar un género a un mod (solo OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para agregar géneros a mods")
    
    crud = CRUD_MOD_GENRE(db)
    mod, genre, mod_genre = crud.add_genre_to_mod(data.mod_id, data.genre_id)
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_genres_added,
        mod=mod,
        genres=[genre],
        user=user
    )
    
    return ResponseBuilder.created(
        data=ModGenreResponse.model_validate(mod_genre),
        message="Género agregado a mod exitosamente",
        db=db
    )


@router.patch("/admin/status/{mod_genre_id}")
def update_mod_genre_status(
    mod_genre_id: int,
    data: UpdateModGenreStatus,
    user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar el estado is_active de una relación mod-género (solo OWNER/EDITOR)"""
    
    crud = CRUD_MOD_GENRE(db)
    mod_genre = crud.update_mod_genre_status(mod_genre_id, data.is_active)
    
    # Get mod and genre for Discord notification
    mod = db.query(Mod).filter(Mod.id == mod_genre.mod_id).first()
    genre = db.query(Genre).filter(Genre.id == mod_genre.genre_id).first()
    
    # Send Discord notification (non-blocking)
    # We'll use the existing notify functions with a custom handling
    if data.is_active:
        background_tasks.add_task(
            notify_genres_added,
            mod=mod,
            genres=[genre],
            user=user
        )
    else:
        background_tasks.add_task(
            notify_genres_removed,
            mod=mod,
            genres=[genre],
            user=user
        )
    
    return ResponseBuilder.updated(
        data=ModGenreResponse.model_validate(mod_genre),
        message="Estado de la relación actualizado exitosamente",
        db=db
    )


@router.put("/{mod_genre_id}")
def update_mod_genre_id(
    mod_genre_id: int,
    data: UpdateModGenreId,
    user: TokenUser = Depends(verify_admin_role),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar el id_genre de una relación mod-género (solo OWNER/EDITOR)"""
    
    crud = CRUD_MOD_GENRE(db)
    
    # Obtener la relación antigua para obtener el género anterior
    old_mod_genre = crud.get_mod_genre_admin(mod_genre_id)
    if not old_mod_genre:
        raise HTTPException(status_code=404, detail="Relación mod-género no encontrada")
    
    old_genre = db.query(Genre).filter(Genre.id == old_mod_genre.genre_id).first()
    
    # Actualizar el género
    mod_genre = crud.update_genre_id(mod_genre_id, data.genre_id)
    
    # Get mod and new genre for Discord notification
    mod = db.query(Mod).filter(Mod.id == mod_genre.mod_id).first()
    new_genre = db.query(Genre).filter(Genre.id == mod_genre.genre_id).first()
    
    # Send Discord notification (non-blocking)
    background_tasks.add_task(
        notify_genres_removed,
        mod=mod,
        genres=[old_genre] if old_genre else [],
        user=user
    )
    background_tasks.add_task(
        notify_genres_added,
        mod=mod,
        genres=[new_genre] if new_genre else [],
        user=user
    )
    
    return ResponseBuilder.updated(
        data=ModGenreResponse.model_validate(mod_genre),
        message="Género de la relación actualizado exitosamente",
        db=db
    )
