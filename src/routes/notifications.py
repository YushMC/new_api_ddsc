from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.services.notifications import CRUD_NOTIFICATION
from src.schemas.notifications import NotificationResponse
from src.utils.response_builder import ResponseBuilder
from src.models.enums import NotificationStatusEnum
from typing import Optional

router = APIRouter()
db_init = DATABASE_INIT()


@router.get("")
def get_notifications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """
    Obtener notificaciones del usuario autenticado
    
    - status: 'unread' o 'read' (opcional)
    - skip: Para paginación
    - limit: Máximo de resultados (default 50, max 100)
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
        message="Notificaciones obtenidas exitosamente"
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
        message="Notificación marcada como leída"
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
