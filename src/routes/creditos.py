from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.creditos import CRUD_CREDITS
from src.services.mods import CRUD_MOD
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.models.credits import Credit
from src.schemas.credits import CreditCreate, CreditResponse, CreditBatchCreate
from src.utils.response_builder import ResponseBuilder
from src.background_tasks import notify_mod_completed
from pydantic import BaseModel
from src.models.enums import CreditsTypeEnum
from typing import cast

router = APIRouter()
db_init = DATABASE_INIT()


class CreditUpdate(BaseModel):
    """Schema para actualizar crédito"""
    id_user: int | None = None
    name: str | None = None
    type: CreditsTypeEnum | None = None


def _enrich_credit_with_user(credit, db: Session):
    """
    Enriquece un crédito con la información del usuario si existe.
    - Si tiene id_user: solo retorna {id, type, user}
    - Si no tiene id_user: retorna {id, id_mod, id_user, name, type, is_active}
    """
    from src.models.users import User
    
    # Si tiene id_user, solo retornar user object
    if credit.id_user:
        user = db.query(User).filter(User.id == credit.id_user).first()
        if user:
            return {
                "id": credit.id,
                "type": credit.type,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "contact": user.contact,
                    "logo": user.logo
                }
            }
    
    # Si no tiene id_user, retornar datos del crédito
    return {
        "id": credit.id,
        "id_mod": credit.id_mod,
        "id_user": credit.id_user,
        "name": credit.name,
        "type": credit.type,
        "is_active": credit.is_active
    }


def _organize_credits_by_type(credits, db: Session):
    """
    Organiza los créditos por tipo en arrays (creators, translators, porters).
    Solo incluye objeto 'user' si el crédito tiene id_user.
    """
    from src.models.enums import CreditsTypeEnum
    
    organized = {
        "creators": [],
        "translators": [],
        "porters": []
    }
    
    for credit in credits:
        enriched = _enrich_credit_with_user(credit, db)
        
        if credit.type == CreditsTypeEnum.ORIGINAL_CREATOR:
            organized["creators"].append(enriched)
        elif credit.type == CreditsTypeEnum.TRANSLATOR:
            organized["translators"].append(enriched)
        elif credit.type == CreditsTypeEnum.PORTER:
            organized["porters"].append(enriched)
    
    return organized


@router.get("/mod/{mod_id}")
def get_credits_by_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener créditos de un mod (públicamente disponible)"""
    crud = CRUD_CREDITS(db)
    credits = crud.get_credits_by_mod(mod_id)
    
    organized_credits = _organize_credits_by_type(credits, db)
    
    return ResponseBuilder.success(
        data=organized_credits,
        message="Créditos obtenidos exitosamente"
    )


@router.get("/admin/all")
def list_credits_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todos los créditos incluyendo inactivos (solo para OWNER/EDITOR)"""
    crud = CRUD_CREDITS(db)
    credits = crud.get_credits_admin(skip, limit)
    
    # Preparar cada crédito con la información enriquecida
    prepared_credits = []
    for credit in credits:
        enriched = _enrich_credit_with_user(credit, db)
        prepared_credits.append(enriched)
    
    return {
        "response": "success",
        "message": "Créditos obtenidos exitosamente (incluyendo inactivos)",
        "data": prepared_credits
    }


@router.get("/{credit_id}")
def get_credit(credit_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un crédito específico (públicamente disponible)"""
    crud = CRUD_CREDITS(db)
    credit = crud.get_credit(credit_id)
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    
    enriched = _enrich_credit_with_user(credit, db)
    
    return ResponseBuilder.success(
        data=enriched,
        message="Crédito obtenido exitosamente"
    )


@router.get("/admin/{credit_id}")
def get_credit_admin(
    credit_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener un crédito específico incluyendo inactivos (solo OWNER/EDITOR)"""
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    
    enriched = _enrich_credit_with_user(credit, db)
    
    return ResponseBuilder.success(
        data=enriched,
        message="Crédito obtenido exitosamente"
    )


@router.post("")
def create_credit(
    data: CreditCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Crear nuevo crédito (requiere token válido)"""
    crud = CRUD_CREDITS(db)
    credit = crud.create_credit(
        id_mod=data.id_mod,
        id_user=data.id_user,
        name=data.name,
        credit_type=data.type
    )
    
    enriched = _enrich_credit_with_user(credit, db)
    
    # Verificar si el mod está completo (tiene imágenes y créditos)
    crud_mod = CRUD_MOD(db)
    if crud_mod.is_mod_complete(data.id_mod):
        # Obtener el mod completo
        mod = crud_mod.get_mod(data.id_mod)
        if mod:
            # Agregar notificación a Discord como background task
            background_tasks.add_task(notify_mod_completed, mod)
    
    return ResponseBuilder.created(
        data=enriched,
        message="Crédito creado exitosamente"
    )


@router.post("/batch")
def create_credits_batch(
    data: CreditBatchCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Crear múltiples créditos de una vez para un mod
    
    Estructura esperada:
    {
        "id_mod": 5,
        "credits": [
            {"id_user": 1, "type": "original_creator"},
            {"name": "Juan Pérez", "type": "translator"},
            {"id_user": 3, "name": null, "type": "porter"}
        ]
    }
    """
    crud = CRUD_CREDITS(db)
    
    # Convertir los créditos batch a diccionarios
    credits_data = [credit.model_dump() for credit in data.credits]
    
    # Crear todos los créditos
    created_credits = crud.create_credits_batch(data.id_mod, credits_data)
    
    # Enriquecer cada crédito con la información del usuario
    enriched_credits = [_enrich_credit_with_user(credit, db) for credit in created_credits]
    
    # Verificar si el mod está completo (tiene imágenes y créditos)
    crud_mod = CRUD_MOD(db)
    if crud_mod.is_mod_complete(data.id_mod):
        # Obtener el mod completo
        mod = crud_mod.get_mod(data.id_mod)
        if mod:
            # Agregar notificación a Discord como background task
            background_tasks.add_task(notify_mod_completed, mod)
    
    return ResponseBuilder.created(
        data=enriched_credits,
        message=f"{len(enriched_credits)} créditos creados exitosamente"
    )


@router.put("/{credit_id}")
def update_credit(
    credit_id: int,
    data: CreditUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar un crédito (requiere token válido)"""
    crud = CRUD_CREDITS(db)
    
    # Obtener el crédito original para saber el mod_id
    original_credit = crud.get_credit(credit_id)
    if not original_credit:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    
    # Lógica de actualización:
    # - Si se proporciona id_user: actualizar id_user y set name a null
    # - Si id_user es null en request: set id_user a null y usar name del request o preservar
    # - Si no se proporciona id_user en request: preservar id_user actual
    
    if data.id_user is not None:
        # Caso 1: Se proporciona id_user (puede ser un número)
        update_id_user = data.id_user
        update_name = None  # name será null cuando hay id_user
    elif "id_user" in data.model_dump() and data.model_dump()["id_user"] is None:
        # Caso 2: Explícitamente se manda id_user: null
        update_id_user = None
        update_name = data.name if data.name is not None else cast(str, original_credit.name)
    else:
        # Caso 3: No se proporciona id_user en el request, preservar
        update_id_user = cast(int, original_credit.id_user)
        update_name = data.name if data.name is not None else cast(str, original_credit.name)
    
    credit = crud.update_credit(
        credit_id=credit_id,
        id_user=cast(int | None, update_id_user),
        name=cast(str | None, update_name),
        credit_type=data.type or cast(CreditsTypeEnum, original_credit.type)
    )
    
    enriched = _enrich_credit_with_user(credit, db)
    
    # Verificar si el mod está completo (tiene imágenes y créditos)
    crud_mod = CRUD_MOD(db)
    if crud_mod.is_mod_complete(cast(int, original_credit.id_mod)):
        # Obtener el mod completo
        mod = crud_mod.get_mod(cast(int, original_credit.id_mod))
        if mod:
            # Agregar notificación a Discord como background task
            background_tasks.add_task(notify_mod_completed, mod)
    
    return ResponseBuilder.updated(
        data=enriched,
        message="Crédito actualizado exitosamente"
    )


@router.delete("/{credit_id}")
def delete_credit(
    credit_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Eliminar un crédito (soft delete, requiere token válido)"""
    crud = CRUD_CREDITS(db)
    crud.delete_credit(credit_id)
    return ResponseBuilder.deleted(message="Crédito eliminado exitosamente")
