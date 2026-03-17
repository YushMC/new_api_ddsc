from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.mod_statistic import ModStatistic
from src.models.mods import Mod


class CRUD_MOD_STATISTIC:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def get_statistic(self, statistic_id: int):
        """Obtener una estadística específica (activa)"""
        return self.__db.query(ModStatistic).filter(
            ModStatistic.id == statistic_id,
            ModStatistic.is_active == True
        ).first()
    
    def get_statistic_admin(self, statistic_id: int):
        """Obtener una estadística específica (incluyendo inactivas)"""
        return self.__db.query(ModStatistic).filter(
            ModStatistic.id == statistic_id
        ).first()
    
    def get_statistic_by_mod(self, mod_id: int):
        """Obtener estadística de un mod específico (activa)"""
        return self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id,
            ModStatistic.is_active == True
        ).first()
    
    def get_statistics(self, skip: int = 0, limit: int = 20):
        """Obtener todas las estadísticas activas (paginado)"""
        return self.__db.query(ModStatistic).filter(
            ModStatistic.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_statistics_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todas las estadísticas incluyendo inactivas (paginado)"""
        return self.__db.query(ModStatistic).offset(skip).limit(limit).all()
    
    def create_statistic(self, mod_id: int):
        """Crear estadística para un mod"""
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Verificar que no existe una estadística para este mod
        existing = self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una estadística para este mod")
        
        # Crear nueva estadística
        statistic = ModStatistic(
            mod_id=mod_id,
            download_pc=0,
            download_android=0,
            searchs=0
        )
        self.__db.add(statistic)
        self.__db.commit()
        self.__db.refresh(statistic)
        
        return statistic
    
    def increment_statistic(self, mod_id: int, download_pc: int = 0, download_android: int = 0, searchs: int = 0):
        """Incrementar valores de estadística (público)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id,
            ModStatistic.is_active == True
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        # Incrementar valores
        statistic.download_pc = (statistic.download_pc or 0) + download_pc
        statistic.download_android = (statistic.download_android or 0) + download_android
        statistic.searchs = (statistic.searchs or 0) + searchs
        
        self.__db.commit()
        self.__db.refresh(statistic)
        
        return statistic
    
    def increment_download_pc(self, mod_id: int):
        """Incrementar descargas PC en 1 (público)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id,
            ModStatistic.is_active == True
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        statistic.download_pc = (statistic.download_pc or 0) + 1
        self.__db.commit()
        self.__db.refresh(statistic)
        return statistic
    
    def increment_download_android(self, mod_id: int):
        """Incrementar descargas Android en 1 (público)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id,
            ModStatistic.is_active == True
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        statistic.download_android = (statistic.download_android or 0) + 1
        self.__db.commit()
        self.__db.refresh(statistic)
        return statistic
    
    def increment_searchs(self, mod_id: int):
        """Incrementar búsquedas en 1 (público)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.mod_id == mod_id,
            ModStatistic.is_active == True
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        statistic.searchs = (statistic.searchs or 0) + 1
        self.__db.commit()
        self.__db.refresh(statistic)
        return statistic
    
    def delete_statistic(self, statistic_id: int):
        """Soft delete de estadística (solo OWNER/EDITOR)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.id == statistic_id
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        statistic.is_active = False
        self.__db.commit()
        self.__db.refresh(statistic)
        
        return statistic
    
    def reactivate_statistic(self, statistic_id: int):
        """Reactivar estadística (solo OWNER/EDITOR)"""
        statistic = self.__db.query(ModStatistic).filter(
            ModStatistic.id == statistic_id
        ).first()
        
        if not statistic:
            raise HTTPException(status_code=404, detail="Estadística no encontrada")
        
        statistic.is_active = True
        self.__db.commit()
        self.__db.refresh(statistic)
        
        return statistic
