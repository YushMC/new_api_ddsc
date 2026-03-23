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
        """Agregar un mod a una colección (solo OWNER/EDITOR)
        
        Retorna: Tuple (mod, collection, mods_collection)
        """
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
            return (mod, collection, existing_inactive)
        
        # Crear nueva relación
        mods_collection = ModsCollection(
            mod_id=mod_id,
            collection_id=collection_id
        )
        self.__db.add(mods_collection)
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return (mod, collection, mods_collection)
    
    def remove_mod_from_collection(self, mods_collection_id: int):
        """Remover un mod de una colección (soft delete - solo OWNER/EDITOR)
        
        Retorna: Tuple (mod, collection)
        """
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
        
        if not mods_collection:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        # Obtener mod y collection antes de marcar como inactivo
        mod = self.__db.query(Mod).filter(Mod.id == mods_collection.mod_id).first()
        collection = self.__db.query(Collection).filter(Collection.id == mods_collection.collection_id).first()
        
        mods_collection.is_active = False
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return (mod, collection)
    
    def update_mods_collection_status(self, mods_collection_id: int, is_active: bool):
        """Actualizar el estado is_active de una relación mods-colecciones (solo OWNER/EDITOR)"""
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
        
        if not mods_collection:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        mods_collection.is_active = is_active
        self.__db.commit()
        self.__db.refresh(mods_collection)
        
        return mods_collection
    
    def _build_response_with_collection_name(self, mods_collection):
        """Construir respuesta con collection_name en lugar de collection_id"""
        collection = self.__db.query(Collection).filter(
            Collection.id == mods_collection.collection_id
        ).first()
        
        resource = {
            "id": mods_collection.id,
            "mod_id": mods_collection.mod_id,
            "collection_name": collection.name if collection else "Desconocida"
        }
        
        info = {
            "is_active": mods_collection.is_active,
            "created_at": mods_collection.created_at,
            "updated_at": mods_collection.updated_at,
            "created_by": mods_collection.created_by,
            "updated_by": mods_collection.updated_by
        }
        
        return resource, info
    
    def get_mods_collections_with_collection_name(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones activas con collection_name (paginado)"""
        mods_collections = self.__db.query(ModsCollection).filter(
            ModsCollection.is_active == True
        ).offset(skip).limit(limit).all()
        
        return [self._build_response_with_collection_name(mc) for mc in mods_collections]
    
    def get_mods_collections_admin_with_collection_name(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones incluyendo inactivas con collection_name (paginado)"""
        mods_collections = self.__db.query(ModsCollection).offset(skip).limit(limit).all()
        
        return [self._build_response_with_collection_name(mc) for mc in mods_collections]
    
    def get_mods_collection_with_collection_name(self, mods_collection_id: int):
        """Obtener una relación específica (activa) con collection_name"""
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id,
            ModsCollection.is_active == True
        ).first()
        
        if not mods_collection:
            return None
        
        return self._build_response_with_collection_name(mods_collection)
    
    def get_mods_collection_admin_with_collection_name(self, mods_collection_id: int):
        """Obtener una relación específica (incluyendo inactivas) con collection_name"""
        mods_collection = self.__db.query(ModsCollection).filter(
            ModsCollection.id == mods_collection_id
        ).first()
        
        if not mods_collection:
            return None
        
        return self._build_response_with_collection_name(mods_collection)
    
    def get_mod_collections_with_collection_name(self, mod_id: int):
        """Obtener todas las colecciones de un mod (activas) con collection_name"""
        mods_collections = self.__db.query(ModsCollection).filter(
            ModsCollection.mod_id == mod_id,
            ModsCollection.is_active == True
        ).all()
        
        return [self._build_response_with_collection_name(mc) for mc in mods_collections]
    
    def get_collection_mods_with_collection_name(self, collection_id: int):
        """Obtener todos los mods de una colección (activos) con collection_name"""
        mods_collections = self.__db.query(ModsCollection).filter(
            ModsCollection.collection_id == collection_id,
            ModsCollection.is_active == True
        ).all()
        
        return [self._build_response_with_collection_name(mc) for mc in mods_collections]
