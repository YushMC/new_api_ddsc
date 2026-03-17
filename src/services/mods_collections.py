from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.mods_collection import ModsCollection
from src.models.mods import Mod
from src.models.collection import Collection


class CRUD_MODS_COLLECTION:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def get_mods_collection(self, mods_collection_id: int):
        """Obtener una relación mods-colecciones específica (activa)"""
        return self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id,
            ModsCollection.is_active == True
        ).first()
    
    def get_mods_collection_admin(self, mods_collection_id: int):
        """Obtener una relación mods-colecciones específica (incluyendo inactivas)"""
        return self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
    
    def get_mods_collections(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones activas (paginado)"""
        return self.__db.query(ModsCollection).filter(
            ModsCollection.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_mods_collections_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones incluyendo inactivas (paginado)"""
        return self.__db.query(ModsCollection).offset(skip).limit(limit).all()
    
    def get_mod_collections(self, mod_id: int):
        """Obtener todas las colecciones de un mod (activas)"""
        return self.__db.query(ModsCollection).filter(
            ModsCollection.mod_id == mod_id,
            ModsCollection.is_active == True
        ).all()
    
    def get_collection_mods(self, collection_id: int):
        """Obtener todos los mods de una colección (activos)"""
        return self.__db.query(ModsCollection).filter(
            ModsCollection.collection_id == collection_id,
            ModsCollection.is_active == True
        ).all()
    
    def add_mod_to_collection(self, mod_id: int, collection_id: int):
        """Agregar un mod a una colección (solo OWNER/EDITOR)"""
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Verificar que la colección existe
        collection = self.__db.query(Collection).filter(
            Collection.id == collection_id
        ).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Colección no encontrada")
        
        # Verificar que no existe una relación activa entre este mod y esta colección
        existing = self.__db.query(ModsCollection).filter(
            ModsCollection.mod_id == mod_id,
            ModsCollection.collection_id == collection_id,
            ModsCollection.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El mod ya está en esta colección")
        
        # Verificar si existe una relación inactiva para reactivarla
        existing_inactive = self.__db.query(ModsCollection).filter(
            ModsCollection.mod_id == mod_id,
            ModsCollection.collection_id == collection_id,
            ModsCollection.is_active == False
        ).first()
        
        if existing_inactive:
            # Reactivar la relación
            existing_inactive.is_active = True
            self.__db.commit()
            self.__db.refresh(existing_inactive)
            return existing_inactive
        
        # Crear nueva relación
        mods_collection = ModsCollection(
            mod_id=mod_id,
            collection_id=collection_id
        )
        self.__db.add(mods_collection)
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return mods_collection
    
    def remove_mod_from_collection(self, mods_collection_id: int):
        """Remover un mod de una colección (soft delete - solo OWNER/EDITOR)"""
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
        
        if not mods_collection:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        mods_collection.is_active = False
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return mods_collection
    
    def reactivate_mod_collection(self, mods_collection_id: int):
        """Reactivar mod en colección (solo OWNER/EDITOR)"""
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
        
        if not mods_collection:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        mods_collection.is_active = True
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return mods_collection
