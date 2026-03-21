from fastapi import HTTPException
from sqlalchemy.orm import Session
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
    
    def update_collection(self, collection_id: int, name: str | None = None, description: str | None = None):
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
        
        self.__db.commit()
        self.__db.refresh(collection)
        
        return (collection, changes)
    
    def delete_collection(self, collection_id: int):
        """Soft delete de colección (solo OWNER/EDITOR)"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        collection.is_active = False
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
    
    def reactivate_collection(self, collection_id: int):
        """Reactivar colección (solo OWNER/EDITOR)"""
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        collection.is_active = True
        self.__db.commit()
        self.__db.refresh(collection)
        
        return collection
