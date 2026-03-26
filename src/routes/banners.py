from src.schemas.banners import BannerCreate, BannerUpdate, BannerResponse, BannerResponseComplete, BannerCreateAuto
from fastapi import APIRouter, Depends, HTTPException, Query
from src.middleware.jwt import get_current_user, verify_admin_role
from src.conf.database import DATABASE_INIT
from src.services.banners import CRUD_BANNER
from src.services.token import TokenUser
from src.utils.response_builder import ResponseBuilder
from src.models.enums import UserRolEnum
from sqlalchemy.orm import Session

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("/active")
def get_active_banners(db: Session = Depends(db_init.get_db)):
    """
    Obtener todos los banners activos y vigentes
    - Filtra banners con is_active=True
    - Respeta las fechas start_date y end_date
    """
    try:
        crud = CRUD_BANNER(db)
        banners = crud.get_active_banners()
        
        response_data = [
            BannerResponse.model_validate(banner).model_dump()
            for banner in banners
        ]
        
        return ResponseBuilder.success(response_data, "Banners activos obtenidos correctamente")
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/latest/active")
def get_latest_active_banner(db: Session = Depends(db_init.get_db)):
    """
    Obtener el banner más reciente activo y vigente
    - Solo devuelve el banner más reciente creado
    - Filtra banners con is_active=True
    - Respeta las fechas start_date y end_date
    """
    try:
        crud = CRUD_BANNER(db)
        banner = crud.get_latest_active_banner()
        
        if not banner:
            return ResponseBuilder.success(None, "No hay banners activos disponibles")
        
        response_data = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response_data, "Banner más reciente obtenido correctamente")
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/latest")
def get_latest_banner(db: Session = Depends(db_init.get_db)):
    """
    Obtener el banner más reciente
    - Solo devuelve el banner más reciente creado
    - Filtra banners con is_active=True
    """
    try:
        crud = CRUD_BANNER(db)
        banner = crud.get_latest_banner()
        
        if not banner:
            return ResponseBuilder.success(None, "No hay banners disponibles")
        
        response_data = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response_data, "Banner más reciente obtenido correctamente")
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("", response_model=dict)
def get_banners(
    db: Session = Depends(db_init.get_db),
    current_user: TokenUser = Depends(get_current_user)
):
    """
    Obtener todos los banners
    - Los EDITORS y OWNERS ven todos los banners
    - Los demás usuarios solo ven activos
    """
    try:
        crud = CRUD_BANNER(db)
        
        # Verificar si es admin
        is_admin = current_user.role in [UserRolEnum.EDITOR, UserRolEnum.OWNER]
        
        if is_admin:
            banners = crud.get_banners_admin_all()
        else:
            banners = crud.get_banners_all()
        
        response_data = [
            BannerResponse.model_validate(banner).model_dump()
            for banner in banners
        ]
        
        return ResponseBuilder.success(response_data, "Banners obtenidos correctamente")
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/{banner_id}", response_model=dict)
def get_banner(banner_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un banner específico"""
    try:
        crud = CRUD_BANNER(db)
        banner = crud.get_banner(banner_id)
        
        response = BannerResponseComplete.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response, "Banner obtenido correctamente")
    except HTTPException as e:
        return ResponseBuilder.error(e.detail, e.status_code)
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.post("", response_model=dict)
def create_banner(
    banner_data: BannerCreate,
    db: Session = Depends(db_init.get_db),
    current_user: TokenUser = Depends(get_current_user),
    verify_role: None = Depends(verify_admin_role)
):
    """
    Crear nuevo banner (manual)
    - Solo EDITORS y OWNERS pueden crear banners
    """
    try:
        crud = CRUD_BANNER(db)
        
        banner = crud.create_banner(
            title=banner_data.title,
            message=banner_data.message,
            type=banner_data.type,
            created_by=current_user.id,
            style=banner_data.style,
            url=banner_data.url,
            start_date=banner_data.start_date,
            end_date=banner_data.end_date
        )
        
        response = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response, "Banner creado correctamente", 201)
    except HTTPException as e:
        return ResponseBuilder.error(e.detail, e.status_code)
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.put("/{banner_id}", response_model=dict)
def update_banner(
    banner_id: int,
    banner_data: BannerUpdate,
    db: Session = Depends(db_init.get_db),
    current_user: TokenUser = Depends(get_current_user),
    verify_role: None = Depends(verify_admin_role)
):
    """
    Actualizar un banner
    - Solo EDITORS y OWNERS pueden actualizar banners
    """
    try:
        crud = CRUD_BANNER(db)
        
        # Validar que el banner existe
        existing_banner = crud.get_banner(banner_id)
        
        update_data = banner_data.model_dump(exclude_unset=True)
        banner = crud.update_banner(banner_id, **update_data)
        
        response = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response, "Banner actualizado correctamente")
    except HTTPException as e:
        return ResponseBuilder.error(e.detail, e.status_code)
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.delete("/{banner_id}", response_model=dict)
def delete_banner(
    banner_id: int,
    db: Session = Depends(db_init.get_db),
    current_user: TokenUser = Depends(get_current_user),
    verify_role: None = Depends(verify_admin_role)
):
    """
    Eliminar un banner (soft delete)
    - Solo EDITORS y OWNERS pueden eliminar banners
    """
    try:
        crud = CRUD_BANNER(db)
        
        # Validar que el banner existe
        crud.get_banner(banner_id)
        
        banner = crud.delete_banner(banner_id)
        
        response = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response, "Banner eliminado correctamente")
    except HTTPException as e:
        return ResponseBuilder.error(e.detail, e.status_code)
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.post("/{banner_id}/restore", response_model=dict)
def restore_banner(
    banner_id: int,
    db: Session = Depends(db_init.get_db),
    current_user: TokenUser = Depends(get_current_user),
    verify_role: None = Depends(verify_admin_role)
):
    """
    Restaurar un banner eliminado
    - Solo EDITORS y OWNERS pueden restaurar banners
    """
    try:
        crud = CRUD_BANNER(db)
        
        banner = crud.restore_banner(banner_id)
        
        response = BannerResponse.model_validate(banner).model_dump()
        
        return ResponseBuilder.success(response, "Banner restaurado correctamente")
    except HTTPException as e:
        return ResponseBuilder.error(e.detail, e.status_code)
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)
