from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mod_statistics import CRUD_MOD_STATISTIC
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.mod_statistics import ModStatisticResponse, ModStatisticStatusRequest, ModStatisticsRequest, ModStatisticCreateRequest, transform_statistic_to_response
from src.utils.response_builder import ResponseBuilder
from src.models.enums import UserRolEnum

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def list_statistics(
    db: Session = Depends(db_init.get_db)
):
    """
    Listar todas las estadísticas activas (públicamente disponible)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics_all()
    
    prepared = []
    for s in statistics:
        response_structure = ResponseBuilder._create_response_with_info(
            ModStatisticResponse.model_validate(transform_statistic_to_response(s)),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Estadísticas obtenidas exitosamente",
        "data": prepared
    }


@router.get("/admin/all")
def list_statistics_admin(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las estadísticas incluyendo inactivas (solo OWNER/EDITOR)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics_admin_all()
    
    prepared = []
    for s in statistics:
        response_structure = ResponseBuilder._create_response_with_info(
            ModStatisticResponse.model_validate(transform_statistic_to_response(s)),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Estadísticas obtenidas exitosamente (incluyendo inactivas)",
        "data": prepared
    }


@router.get("/my-statistics")
def get_my_statistics(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(get_current_user)
):
    """
    Obtener todas las estadísticas de mods creados por el usuario autenticado (cualquier rol)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics_by_creator_all(user.id)
    
    prepared = []
    for s in statistics:
        response_structure = ResponseBuilder._create_response_with_info(
            ModStatisticResponse.model_validate(transform_statistic_to_response(s)),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Estadísticas del usuario obtenidas exitosamente",
        "data": prepared
    }


@router.post("")
def create_statistic(
    data: ModStatisticCreateRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Crear una nueva estadística para un mod (requiere autenticación, cualquier rol)
    
    Solo requiere mod_id. El created_by se auto-popula del token del usuario autenticado.
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.create_statistic(data.mod_id)
    
    return ResponseBuilder.created(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Estadística creada exitosamente",
        db=db
    )


@router.get("/{statistic_id}")
def get_statistic(
    statistic_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener una estadística específica (públicamente disponible)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.get_statistic(statistic_id)
    if not statistic:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")
    return ResponseBuilder.success(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Estadística obtenida exitosamente",
        db=db
    )


@router.get("/admin/{statistic_id}")
def get_statistic_admin(
    statistic_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener una estadística incluyendo si está inactiva (solo OWNER/EDITOR)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.get_statistic_admin(statistic_id)
    if not statistic:
        raise HTTPException(status_code=404, detail="Estadística no encontrada")
    return ResponseBuilder.success(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Estadística obtenida exitosamente",
        db=db
    )


@router.get("/mod/{mod_id}")
def get_mod_statistic(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener estadística de un mod específico (públicamente disponible)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.get_statistic_by_mod(mod_id)
    if not statistic:
        raise HTTPException(status_code=404, detail="Estadística no encontrada para este mod")
    return ResponseBuilder.success(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Estadística del mod obtenida exitosamente",
        db=db
    )


@router.get("/mod/{mod_id}/views")
def get_mod_views(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """Obtener número de vistas de un mod específico (públicamente disponible)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.get_statistic_by_mod(mod_id)
    if not statistic:
        raise HTTPException(status_code=404, detail="Estadística no encontrada para este mod")
    return ResponseBuilder.success(
        data={"mod_id": mod_id, "views": statistic.views},
        message="Vistas del mod obtenidas exitosamente",
        db=db
    )


@router.post("/by-mods")
def get_statistics_by_mods(
    data: ModStatisticsRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Obtener estadísticas de múltiples mods (requiere autenticación, cualquier rol)
    
    Enviar array de mod_ids en el body: { "mod_ids": [1, 2, 3] }
    """
    if not data.mod_ids:
        raise HTTPException(status_code=400, detail="mod_ids no puede estar vacío")
    
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics_by_mods(data.mod_ids)
    
    prepared = []
    for s in statistics:
        response_structure = ResponseBuilder._create_response_with_info(
            ModStatisticResponse.model_validate(transform_statistic_to_response(s)),
            "success",
            "",
            db=db
        )
        prepared.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Estadísticas obtenidas exitosamente",
        "data": prepared
    }




@router.post("/mod/{mod_id}/increment-download-pc")
def increment_download_pc(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """
    Incrementar descargas PC en 1 (público, sin token)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.increment_download_pc(mod_id)
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Descargas PC incrementadas exitosamente",
        db=db
    )


@router.post("/mod/{mod_id}/increment-download-android")
def increment_download_android(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """
    Incrementar descargas Android en 1 (público, sin token)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.increment_download_android(mod_id)
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Descargas Android incrementadas exitosamente",
        db=db
    )


@router.post("/mod/{mod_id}/increment-searchs")
def increment_searchs(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """
    Incrementar búsquedas en 1 (público, sin token)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.increment_searchs(mod_id)
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Búsquedas incrementadas exitosamente",
        db=db
    )


@router.post("/mod/{mod_id}/increment-views")
def increment_views(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """
    Incrementar vistas en 1 (público, sin token)
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.increment_views(mod_id)
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message="Vistas incrementadas exitosamente",
        db=db
    )


@router.patch("/status/{statistic_id}")
def update_statistic_status(
    statistic_id: int,
    data: ModStatisticStatusRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Activar/desactivar estadística (solo OWNER/EDITOR)
    
    Enviar { "is_active": true } para activar o { "is_active": false } para desactivar
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para cambiar estado de estadísticas")
    
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.update_statistic_status(statistic_id, data.is_active)
    
    status_text = "activada" if data.is_active else "desactivada"
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(transform_statistic_to_response(statistic)),
        message=f"Estadística {status_text} exitosamente",
        db=db
    )
