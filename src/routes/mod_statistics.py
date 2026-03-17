from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mod_statistics import CRUD_MOD_STATISTIC
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.schemas.mod_statistics import ModStatisticResponse, ModStatisticCreate, ModStatisticUpdate
from src.utils.response_builder import ResponseBuilder

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def list_statistics(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20
):
    """Listar todas las estadísticas activas (públicamente disponible)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics(skip, limit)
    return ResponseBuilder.list_response(
        data=[ModStatisticResponse.model_validate(s) for s in statistics],
        message="Estadísticas obtenidas exitosamente"
    )


@router.get("/admin/all")
def list_statistics_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todas las estadísticas incluyendo inactivas (solo OWNER/EDITOR)"""
    crud = CRUD_MOD_STATISTIC(db)
    statistics = crud.get_statistics_admin(skip, limit)
    return ResponseBuilder.list_response(
        data=[ModStatisticResponse.model_validate(s) for s in statistics],
        message="Estadísticas obtenidas exitosamente (incluyendo inactivas)"
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
        data=ModStatisticResponse.model_validate(statistic),
        message="Estadística obtenida exitosamente"
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
        data=ModStatisticResponse.model_validate(statistic),
        message="Estadística obtenida exitosamente"
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
        data=ModStatisticResponse.model_validate(statistic),
        message="Estadística del mod obtenida exitosamente"
    )


@router.post("/mod/{mod_id}/increment")
def increment_statistic(
    mod_id: int,
    data: ModStatisticUpdate,
    db: Session = Depends(db_init.get_db)
):
    """
    Incrementar estadísticas de un mod (público, sin token)
    
    Parámetros:
    - download_pc: cantidad a incrementar descargas PC
    - download_android: cantidad a incrementar descargas Android
    - searchs: cantidad a incrementar búsquedas
    """
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.increment_statistic(
        mod_id,
        data.download_pc,
        data.download_android,
        data.searchs
    )
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(statistic),
        message="Estadísticas incrementadas exitosamente"
    )


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
        data=ModStatisticResponse.model_validate(statistic),
        message="Descargas PC incrementadas exitosamente"
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
        data=ModStatisticResponse.model_validate(statistic),
        message="Descargas Android incrementadas exitosamente"
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
        data=ModStatisticResponse.model_validate(statistic),
        message="Búsquedas incrementadas exitosamente"
    )


@router.delete("/{statistic_id}")
def delete_statistic(
    statistic_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Eliminar estadística (soft delete - solo OWNER/EDITOR)
    
    Nota: La estadística se marca como inactiva pero se mantiene en BD
    """
    from src.models.enums import UserRolEnum
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar estadísticas")
    
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.delete_statistic(statistic_id)
    return ResponseBuilder.deleted(message="Estadística eliminada exitosamente")


@router.post("/{statistic_id}/reactivate")
def reactivate_statistic(
    statistic_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Reactivar una estadística (solo OWNER/EDITOR)"""
    from src.models.enums import UserRolEnum
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para reactivar estadísticas")
    
    crud = CRUD_MOD_STATISTIC(db)
    statistic = crud.reactivate_statistic(statistic_id)
    return ResponseBuilder.updated(
        data=ModStatisticResponse.model_validate(statistic),
        message="Estadística reactivada exitosamente"
    )
