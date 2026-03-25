from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.notifications import Notification
from src.models.enums import NotificationTypeEnum, NotificationStatusEnum, UserRolEnum
from src.services.token import TokenUser
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


def get_notification_content(notification_type: NotificationTypeEnum, mod_name: str, action_by: str | None = None) -> tuple[str, str]:
    """
    Genera el título y mensaje según el tipo de notificación
    
    Args:
        notification_type: Tipo de notificación
        mod_name: Nombre del mod
        action_by: Nombre del usuario que realizó la acción (opcional)
    
    Returns:
        Tupla (title, message)
    """
    if notification_type == NotificationTypeEnum.MOD_PENDING_REVIEW:
        title = f"Nuevo Mod pendiente de revisión: {mod_name}"
        message = f"El usuario {action_by} ha creado un nuevo mod que requiere tu revisión."
    elif notification_type == NotificationTypeEnum.MOD_APPROVED:
        title = f"¡Tu mod ha sido aprobado! {mod_name}"
        message = f"Tu mod '{mod_name}' ha sido aprobado por {action_by} y ahora es visible públicamente."
    elif notification_type == NotificationTypeEnum.MOD_REJECTED:
        title = f"Tu mod ha sido rechazado: {mod_name}"
        message = f"Tu mod '{mod_name}' ha sido rechazado por {action_by}. Por favor revisa los comentarios para más detalles."
    else:
        title = f"Notificación del mod: {mod_name}"
        message = "Se ha actualizado el estado de tu mod."
    
    return title, message


class CRUD_NOTIFICATION:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def create_notification(
        self,
        id_user: int,
        id_mod: int,
        notification_type: NotificationTypeEnum,
        title: str,
        message: str = None,
        action_by: str = None,
        mod_name: str = None
    ):
        """
        Crea una notificación
        
        Args:
            id_user: ID del usuario que recibe la notificación
            id_mod: ID del mod relacionado
            notification_type: Tipo de notificación
            title: Título de la notificación
            message: Mensaje detallado (opcional)
            action_by: Nombre del usuario que realizó la acción
            mod_name: Nombre del mod (para preservar si se elimina el mod)
        
        Returns:
            Notification creada
        """
        notification = Notification(
            id_user=id_user,
            id_mod=id_mod,
            type=notification_type,
            title=title,
            message=message,
            action_by=action_by,
            mod_name=mod_name,
            status=NotificationStatusEnum.UNREAD
        )
        
        self.__db.add(notification)
        self.__db.commit()
        self.__db.refresh(notification)
        
        return notification
    
    def get_user_notifications(self, user_id: int, status: NotificationStatusEnum = None, skip: int = 0, limit: int = 50):
        """
        Obtiene notificaciones de un usuario
        
        Args:
            user_id: ID del usuario
            status: Filtrar por estado (unread, read) - opcional
            skip: Offset para paginación
            limit: Límite de resultados
        
        Returns:
            Lista de notificaciones ordenadas por fecha más reciente
        """
        query = self.__db.query(Notification).filter(
            Notification.id_user == user_id,
            Notification.is_active == True
        )
        
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_notifications_all(self, user_id: int, status: NotificationStatusEnum = None):
        """
        Obtiene TODAS las notificaciones sin paginación de un usuario
        
        Args:
            user_id: ID del usuario
            status: Filtrar por estado (unread, read) - opcional
        
        Returns:
            Lista de notificaciones ordenadas por fecha más reciente
        """
        query = self.__db.query(Notification).filter(
            Notification.id_user == user_id,
            Notification.is_active == True
        )
        
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).all()
    
    def get_notifications_admin(self, skip: int = 0, limit: int = 50):
        """Obtener todas las notificaciones (incluyendo inactivas) - Solo para administradores"""
        return self.__db.query(Notification).offset(skip).limit(limit).all()
    
    def get_notifications_admin_all(self):
        """Obtener TODAS las notificaciones sin paginación (incluyendo inactivas) - Solo para administradores"""
        return self.__db.query(Notification).all()
    
    def get_unread_count(self, user_id: int) -> int:
        """
        Obtiene el número de notificaciones sin leer
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Cantidad de notificaciones sin leer
        """
        return self.__db.query(Notification).filter(
            Notification.id_user == user_id,
            Notification.status == NotificationStatusEnum.UNREAD,
            Notification.is_active == True
        ).count()
    
    def mark_as_read(self, notification_id: int, user_id: int):
        """
        Marca una notificación como leída
        
        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para validar ownership)
        
        Returns:
            Notification actualizada
        """
        notification = self.__db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.id_user == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        notification.status = NotificationStatusEnum.READ
        notification.read_at = datetime.now(UTC)  # type: ignore
        
        self.__db.commit()
        self.__db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, user_id: int):
        """
        Marca todas las notificaciones de un usuario como leídas
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Cantidad de notificaciones marcadas como leídas
        """
        notifications = self.__db.query(Notification).filter(
            Notification.id_user == user_id,
            Notification.status == NotificationStatusEnum.UNREAD,
            Notification.is_active == True
        ).all()
        
        now = datetime.now(UTC)
        for notification in notifications:
            notification.status = NotificationStatusEnum.READ
            notification.read_at = now  # type: ignore
        
        self.__db.commit()
        
        return len(notifications)
    
    def delete_notification(self, notification_id: int, user_id: int):
        """
        Soft delete de una notificación
        
        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para validar ownership)
        
        Returns:
            Notification actualizada
        """
        notification = self.__db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.id_user == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        notification.is_active = False
        
        self.__db.commit()
        self.__db.refresh(notification)
        
        return notification
    
    def update_notification_type(self, notification_id: int, user_id: int, new_type: NotificationTypeEnum):
        """
        Actualiza el tipo de una notificación y su título y mensaje correspondientes
        
        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para validar ownership)
            new_type: Nuevo tipo de notificación
        
        Returns:
            Notification actualizada
        """
        notification = self.__db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.id_user == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        notification.type = new_type
        
        # Generar nuevo título y mensaje según el tipo actualizado
        title, message = get_notification_content(
            notification_type=new_type,
            mod_name=notification.mod_name or "Mod",
            action_by=notification.action_by
        )
        notification.title = title
        notification.message = message
        
        self.__db.commit()
        self.__db.refresh(notification)
        
        return notification
    
    def notify_mod_pending_review(self, mod_id: int, mod_name: str, uploader_name: str):
        """
        Crea notificaciones para TODOS los EDITORS/OWNERS cuando un mod requiere revisión
        
        Args:
            mod_id: ID del mod
            mod_name: Nombre del mod
            uploader_name: Nombre del uploader que creó el mod
        
        Returns:
            Lista de notificaciones creadas
        """
        from src.models.users import User
        
        # Obtener todos los usuarios que no sean UPLOADER (EDITOR y OWNER)
        editors_owners = self.__db.query(User).filter(
            User.role.in_([UserRolEnum.EDITOR, UserRolEnum.OWNER])
        ).all()
        
        notifications = []
        for user in editors_owners:
            notification = self.create_notification(
                id_user=user.id,
                id_mod=mod_id,
                notification_type=NotificationTypeEnum.MOD_PENDING_REVIEW,
                title=f"Nuevo Mod pendiente de revisión: {mod_name}",
                message=f"El usuario {uploader_name} ha creado un nuevo mod que requiere tu revisión.",
                action_by=uploader_name,
                mod_name=mod_name
            )
            notifications.append(notification)
        
        return notifications
    
    def notify_mod_approved(self, mod_id: int, mod_name: str, mod_creator_id: int, approved_by: str):
        """
        Crea una notificación para el UPLOADER cuando su mod es aprobado
        
        Args:
            mod_id: ID del mod
            mod_name: Nombre del mod
            mod_creator_id: ID del usuario que creó el mod
            approved_by: Nombre del usuario que aprobó
        
        Returns:
            Notification creada
        """
        notification = self.create_notification(
            id_user=mod_creator_id,
            id_mod=mod_id,
            notification_type=NotificationTypeEnum.MOD_APPROVED,
            title=f"¡Tu mod ha sido aprobado! {mod_name}",
            message=f"Tu mod '{mod_name}' ha sido aprobado por {approved_by} y ahora es visible públicamente.",
            action_by=approved_by,
            mod_name=mod_name
        )
        
        return notification
    
    def notify_mod_rejected(self, mod_id: int, mod_name: str, mod_creator_id: int, rejected_by: str):
        """
        Crea una notificación para el UPLOADER cuando su mod es rechazado
        
        Args:
            mod_id: ID del mod
            mod_name: Nombre del mod
            mod_creator_id: ID del usuario que creó el mod
            rejected_by: Nombre del usuario que rechazó
        
        Returns:
            Notification creada
        """
        notification = self.create_notification(
            id_user=mod_creator_id,
            id_mod=mod_id,
            notification_type=NotificationTypeEnum.MOD_REJECTED,
            title=f"Tu mod ha sido rechazado: {mod_name}",
            message=f"Tu mod '{mod_name}' ha sido rechazado por {rejected_by}. Por favor revisa los comentarios para más detalles.",
            action_by=rejected_by,
            mod_name=mod_name
        )
        
        return notification

    def notify_mod_deleted(self, mod_id: int, mod_name: str, mod_creator_id: int, deleted_by: str):
        """
        Crea una notificación para el UPLOADER cuando su mod es eliminado
        
        Args:
            mod_id: ID del mod
            mod_name: Nombre del mod
            mod_creator_id: ID del usuario que creó el mod
            deleted_by: Nombre del usuario que eliminó
        
        Returns:
            Notification creada
        """
        notification = self.create_notification(
            id_user=mod_creator_id,
            id_mod=mod_id,
            notification_type=NotificationTypeEnum.MOD_DELETED,
            title=f"Tu mod ha sido eliminado: {mod_name}",
            message=f"Tu mod '{mod_name}' ha sido eliminado por {deleted_by}.",
            action_by=deleted_by,
            mod_name=mod_name
        )
        
        return notification

    def notify_mod_restored(self, mod_id: int, mod_name: str, mod_creator_id: int, restored_by: str):
        """
        Crea una notificación para el UPLOADER cuando su mod es restaurado
        
        Args:
            mod_id: ID del mod
            mod_name: Nombre del mod
            mod_creator_id: ID del usuario que creó el mod
            restored_by: Nombre del usuario que restauró
        
        Returns:
            Notification creada
        """
        notification = self.create_notification(
            id_user=mod_creator_id,
            id_mod=mod_id,
            notification_type=NotificationTypeEnum.MOD_RESTORED,
            title=f"Tu mod ha sido restaurado: {mod_name}",
            message=f"Tu mod '{mod_name}' ha sido restaurado por {restored_by} y vuelve a ser visible.",
            action_by=restored_by,
            mod_name=mod_name
        )
        
        return notification
