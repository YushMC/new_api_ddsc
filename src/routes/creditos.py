from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.creditos import CRUD_CREDITS
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.schemas.credits import CreditCreate, CreditResponse
from src.utils.response_builder import ResponseBuilder
from pydantic import BaseModel
from src.models.enums import CreditsTypeEnum

router = APIRouter()
db_init = DATABASE_INIT()


class CreditUpdate(BaseModel):
    """Schema para actualizar crédito"""
    id_user: int | None = None
    name: str | None = None
    type: CreditsTypeEnum | None = None


def _enrich_credit_with_user(credit, db: Session):
    """
    Enriquece un crédito con la información del usuario si existe
    """
    from src.models.users import User
    
    credit_dict = {
        "id": credit.id,
        "id_mod": credit.id_mod,
        "id_user": credit.id_user,
        "name": credit.name,
        "type": credit.type,
        "is_active": credit.is_active
    }
    
    # Si tiene id_user, obtener la información del usuario
    if credit.id_user:
        user = db.query(User).filter(User.id == credit.id_user).first()
        if user:
            credit_dict["user"] = {
                "id": user.id,
                "name": user.name,
                "contact": user.contact,
                "logo": user.logo
            }
    else:
        # Si no tiene id_user, crear un objeto user con los datos del nombre
        if credit.name:
            credit_dict["user"] = {
                "id": None,
                "name": credit.name,
                "contact": None,
                "logo": None
            }
    
    return credit_dict


def _organize_credits_by_type(credits, db: Session):
    """
    Organiza los créditos por tipo en arrays (creators, translators, porters)
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


@router.get("/{credit_id}")
def get_credit(credit_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un crédito específico (públicamente disponible)"""
    crud = CRUD_CREDITS(db)
    credit = crud.get_credit(credit_id)
    
    enriched = _enrich_credit_with_user(credit, db)
    
    return ResponseBuilder.success(
        data=enriched,
        message="Crédito obtenido exitosamente"
    )


@router.post("")
def create_credit(
    data: CreditCreate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
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
    
    return ResponseBuilder.created(
        data=enriched,
        message="Crédito creado exitosamente"
    )


@router.put("/{credit_id}")
def update_credit(
    credit_id: int,
    data: CreditUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Actualizar un crédito (requiere token válido)"""
    crud = CRUD_CREDITS(db)
    credit = crud.update_credit(
        credit_id=credit_id,
        id_user=data.id_user,
        name=data.name,
        credit_type=data.type
    )
    
    enriched = _enrich_credit_with_user(credit, db)
    
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
