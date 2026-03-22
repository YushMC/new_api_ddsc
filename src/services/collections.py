from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date as date_type
from src.models.collection import Collection


class CRUD_COLLECTION:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def get_collection(self, collection_id: int):
        """Obtener una colección específica (activa)"""
        return self.__db.query(Collection).filter(
            Collection.id == collection_id,
            Collection.is_active == True
        ).first()
    
    def get_collection_admin(self, collection_id: int):
        """Obtener una colección específica (incluyendo inactivas)"""
        return self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
    
    def get_collections(self, skip: int = 0, limit: int = 20):
        """Obtener todas las colecciones activas (paginado)"""
        return self.__db.query(Collection).filter(
            Collection.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_collections_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todas las colecciones incluyendo inactivas (paginado)"""
        return self.__db.query(Collection).offset(skip).limit(limit).all()
    
    def create_collection(self, name: str, description: str | None = None):
        """Crear nueva colección (solo OWNER/EDITOR)"""
        # Verificar que no existe una colección con el mismo nombre
        existing = self.__db.query(Collection).filter(
            Collection.name == name
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una colección con este nombre")
        
        # Crear nueva colección
        collection = Collection(
            name=name,
            description=description
        )
        self.__db.add(collection)
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
    
    def update_collection(self, collection_id: int, name: str | None = None, description: str | None = None, is_seasonal: bool | None = None, start_date: date_type | None = None, end_date: date_type | None = None):
        """Actualizar colección (solo OWNER/EDITOR)"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        changes = {}
        
        # Verificar que el nuevo nombre no existe en otra colección
        if name and name != collection.name:
            existing = self.__db.query(Collection).filter(
                Collection.name == name,
                Collection.id != collection_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Ya existe una colección con este nombre")
            
            changes["name"] = {"old": collection.name, "new": name}
            collection.name = name
            
        if description is not None and description != collection.description:
            changes["description"] = {"old": collection.description, "new": description}
            collection.description = description
        
        if is_seasonal is not None and is_seasonal != collection.is_seasonal:
            changes["is_seasonal"] = {"old": collection.is_seasonal, "new": is_seasonal}
            collection.is_seasonal = is_seasonal
        
        if start_date is not None and start_date != collection.start_date:
            changes["start_date"] = {"old": str(collection.start_date), "new": str(start_date)}
            collection.start_date = start_date
        
        if end_date is not None and end_date != collection.end_date:
            changes["end_date"] = {"old": str(collection.end_date), "new": str(end_date)}
            collection.end_date = end_date
        
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha final")
        
        self.__db.commit()
        self.__db.refresh(collection)
        
        return (collection, changes)
    
    def update_collection_status(self, collection_id: int, is_active: bool):
        """Activar/desactivar colección (solo OWNER/EDITOR)"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        if collection.is_active == is_active:
            status_text = "activa" if is_active else "inactiva"
            raise HTTPException(status_code=400, detail=f"La colección ya se encuentra {status_text}")
        
        collection.is_active = is_active
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
    
    def update_seasonal(self, collection_id: int, is_seasonal: bool):
        """Actualizar si la colección es por temporada"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        collection.is_seasonal = is_seasonal
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
    
    def update_dates(self, collection_id: int, start_date: date_type | None, end_date: date_type | None):
        """Actualizar fechas de temporada de la colección"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha final")
        
        collection.start_date = start_date
        collection.end_date = end_date
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
