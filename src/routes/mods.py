from src.schemas.mods import ModBase
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from src.middleware.jwt import get_current_user
from src.conf.database import DATABASE_INIT
from src.services.mods import CRUD_MOD
from src.services.token import TokenUser
from src.background_tasks import notify_mod_created, notify_mod_updated
from sqlalchemy.orm import Session

router = APIRouter()
db_init = DATABASE_INIT()

@router.get("/all")
def list_mods(db: Session = Depends(db_init.get_db)):
    """Listar todos los mods activos"""
    crud = CRUD_MOD(db)
    return crud.get_mods()

@router.get("/{mod_id}")
def get_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un mod específico por ID"""
    crud = CRUD_MOD(db)
    mod = crud.get_mod(mod_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    return mod

@router.post("")
def create_mod_route(
    data: ModBase,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Crear un nuevo mod (requiere autenticación)"""
    crud = CRUD_MOD(db)
    mod = crud.create_mod(data, user)
    
    # Agregar notificación a Discord como background task (no bloquea respuesta)
    background_tasks.add_task(notify_mod_created, mod, user)
    
    return mod

@router.put("/{mod_id}")
def update_mod_route(
    mod_id: int,
    data: ModBase,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar un mod existente (requiere autenticación)"""
    crud = CRUD_MOD(db)
    mod, changes = crud.update_mod(mod_id, data, user)
    
    # Agregar notificación a Discord como background task (no bloquea respuesta)
    background_tasks.add_task(notify_mod_updated, mod, user, changes)
    
    return mod

@router.delete("/{mod_id}")
def delete_mod_route(
    mod_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Eliminar un mod (soft delete, requiere autenticación)"""
    crud = CRUD_MOD(db)
    return crud.delete_mod(mod_id, user)