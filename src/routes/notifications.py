from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.services.notifications import CRUD_NOTIFICATION
from src.schemas.notifications import NotificationResponse, UpdateNotificationType
from src.utils.response_builder import ResponseBuilder
from src.models.enums import NotificationStatusEnum
from typing import Optional

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def get_notifications(
    status: Optional[str] = Query(None, description="Filtrar por estado: 'unread' o 'read' (opcional, sin filtro retorna todas)"),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=50 omite los primeros 50 resultados."),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 50, max: 100). Ejemplo: limit=25 retorna hasta 25 resultados."),
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Obtener notificaciones del usuario autenticado
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=50 (default)
    - Página 2: skip=50, limit=50
    - Página 3: skip=100, limit=50
    """
    if limit > 100:
        limit = 100
    
    crud = CRUD_NOTIFICATION(db)
    
    # Convertir string a enum si se proporciona
    status_filter = None
    if status:
        if status.lower() == "unread":
            status_filter = NotificationStatusEnum.UNREAD
        elif status.lower() == "read":
            status_filter = NotificationStatusEnum.READ
        else:
            raise HTTPException(status_code=400, detail="Status debe ser 'unread' o 'read'")
    
    notifications = crud.get_user_notifications(
        user_id=user.id,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    
    return ResponseBuilder.success(
        data=[NotificationResponse.model_validate(n).model_dump() for n in notifications],
        message="Notificaciones obtenidas exitosamente",
        db=db
    )


@router.get("/admin/all")
def list_notifications_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=50 omite los primeros 50 resultados."),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 50, max: 100). Ejemplo: limit=25 retorna hasta 25 resultados."),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todas las notificaciones incluyendo inactivas (solo para OWNER/EDITOR)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=50 (default)
    - Página 2: skip=50, limit=50
    - Página 3: skip=100, limit=50
    """
    crud = CRUD_NOTIFICATION(db)
    notifications = crud.get_notifications_admin(skip, limit)
    
    return ResponseBuilder.success(
        data=[NotificationResponse.model_validate(n).model_dump() for n in notifications],
        message="Notificaciones obtenidas exitosamente (incluyendo inactivas)",
        db=db
    )


@router.get("/unread/count")
def get_unread_count(
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Obtener el número de notificaciones sin leer"""
    crud = CRUD_NOTIFICATION(db)
    count = crud.get_unread_count(user.id)
    
    return ResponseBuilder.success(
        data={"unread_count": count},
        message="Contador de notificaciones obtenido"
    )


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Marcar una notificación como leída"""
    crud = CRUD_NOTIFICATION(db)
    notification = crud.mark_as_read(notification_id, user.id)
    
    return ResponseBuilder.updated(
        data=NotificationResponse.model_validate(notification).model_dump(),
        message="Notificación marcada como leída",
        db=db
    )


@router.put("/read-all")
def mark_all_notifications_as_read(
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Marcar todas las notificaciones como leídas"""
    crud = CRUD_NOTIFICATION(db)
    count = crud.mark_all_as_read(user.id)
    
    return ResponseBuilder.updated(
        data={"marked_as_read": count},
        message=f"{count} notificaciones marcadas como leídas"
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Eliminar una notificación (soft delete)"""
    crud = CRUD_NOTIFICATION(db)
    crud.delete_notification(notification_id, user.id)
    
    return ResponseBuilder.deleted(message="Notificación eliminada exitosamente")


@router.put("/{notification_id}/type")
def update_notification_type(
    notification_id: int,
    request: UpdateNotificationType,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Actualizar el tipo de una notificación
    
    - notification_id: ID de la notificación
    - type: Nuevo tipo de notificación (mod_pending_review, mod_approved, mod_rejected)
    """
    crud = CRUD_NOTIFICATION(db)
    notification = crud.update_notification_type(notification_id, user.id, request.type)
    
    return ResponseBuilder.updated(
        data=NotificationResponse.model_validate(notification).model_dump(),
        message="Tipo de notificación actualizado exitosamente",
        db=db
    )
