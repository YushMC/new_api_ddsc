from sqlalchemy.orm import Session
from src.models.banners import Banner
from src.models.enums import BannerTypeEnum
from fastapi import HTTPException
from datetime import datetime, UTC


class CRUD_BANNER:
    def __init__(self, db: Session) -> None:
        self.__db = db

    def get_banners(self, skip: int = 0, limit: int = 20):
        """Obtener todos los banners activos"""
        return self.__db.query(Banner).filter(
            Banner.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_banners_all(self):
        """Obtener TODOS los banners activos sin paginación"""
        return self.__db.query(Banner).filter(
            Banner.is_active == True
        ).all()

    def get_banners_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todos los banners (incluyendo inactivos) - Solo para administradores"""
        return self.__db.query(Banner).offset(skip).limit(limit).all()
    
    def get_banners_admin_all(self):
        """Obtener TODOS los banners sin paginación (incluyendo inactivos) - Solo para administradores"""
        return self.__db.query(Banner).all()

    def get_banner(self, banner_id: int):
        """Obtener un banner específico"""
        banner = self.__db.query(Banner).filter(Banner.id == banner_id).first()
        
        if not banner:
            raise HTTPException(status_code=404, detail="Banner no encontrado")
        
        return banner

    def get_active_banners(self):
        """Obtener todos los banners activos y vigentes (sin filtro de paginación)"""
        now = datetime.now(UTC)
        return self.__db.query(Banner).filter(
            Banner.is_active == True,
            (Banner.start_date.is_(None) | (Banner.start_date <= now)),
            (Banner.end_date.is_(None) | (Banner.end_date >= now))
        ).all()

    def create_banner(self, title: str, message: str, type: BannerTypeEnum, 
                     created_by: int, style: str = "info", url: str = None,
                     id_mod: int = None, start_date: datetime = None, 
                     end_date: datetime = None):
        """Crear nuevo banner"""
        banner = Banner(
            title=title,
            message=message,
            type=type,
            created_by=created_by,
            style=style,
            url=url,
            id_mod=id_mod,
            start_date=start_date,
            end_date=end_date
        )
        
        self.__db.add(banner)
        self.__db.commit()
        self.__db.refresh(banner)
        
        return banner

    def create_banner_for_approved_mod(self, mod_id: int, mod_name: str, created_by: int):
        """Crear banner automático cuando se aprueba un mod"""
        title = f"¡Nuevo mod aprobado: {mod_name}!"
        message = f"Un nuevo mod '{mod_name}' ha sido aprobado y está disponible para descargar."
        
        return self.create_banner(
            title=title,
            message=message,
            type=BannerTypeEnum.MOD_APPROVED,
            created_by=created_by,
            style="success",
            id_mod=mod_id,
            url=f"/mod/{mod_id}"
        )

    def update_banner(self, banner_id: int, **kwargs):
        """Actualizar un banner"""
        banner = self.__db.query(Banner).filter(Banner.id == banner_id).first()
        
        if not banner:
            raise HTTPException(status_code=404, detail="Banner no encontrado")
        
        for key, value in kwargs.items():
            if value is not None and hasattr(banner, key):
                setattr(banner, key, value)
        
        self.__db.commit()
        self.__db.refresh(banner)
        
        return banner

    def delete_banner(self, banner_id: int):
        """Eliminar un banner (soft delete)"""
        banner = self.__db.query(Banner).filter(Banner.id == banner_id).first()
        
        if not banner:
            raise HTTPException(status_code=404, detail="Banner no encontrado")
        
        banner.is_active = False
        self.__db.commit()
        self.__db.refresh(banner)
        
        return banner

    def restore_banner(self, banner_id: int):
        """Restaurar un banner"""
        banner = self.__db.query(Banner).filter(Banner.id == banner_id).first()
        
        if not banner:
            raise HTTPException(status_code=404, detail="Banner no encontrado")
        
        banner.is_active = True
        self.__db.commit()
        self.__db.refresh(banner)
        
        return banner

    def get_banners_by_mod(self, mod_id: int):
        """Obtener todos los banners asociados a un mod"""
        return self.__db.query(Banner).filter(
            Banner.id_mod == mod_id,
            Banner.is_active == True
        ).all()
