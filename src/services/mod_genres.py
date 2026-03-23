from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.mod_genre import ModGenre
from src.models.mods import Mod
from src.models.generos import Genre


class CRUD_MOD_GENRE:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def get_mod_genre(self, mod_genre_id: int):
        """Obtener una relación mod-género específica (activa)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id,
            ModGenre.is_active == True
        ).first()
    
    def get_mod_genre_admin(self, mod_genre_id: int):
        """Obtener una relación mod-género específica (incluyendo inactivas)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id
        ).first()
    
    def get_mod_genres(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones activas (paginado)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_mod_genres_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones incluyendo inactivas (paginado)"""
        return self.__db.query(ModGenre).offset(skip).limit(limit).all()
    
    def get_mod_all_genres(self, mod_id: int):
        """Obtener todos los géneros de un mod (activos)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id,
            ModGenre.is_active == True
        ).all()
    
    def get_mod_all_genres_admin(self, mod_id: int):
        """Obtener todos los géneros de un mod (incluyendo inactivos)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id
        ).all()
    
    def get_genre_all_mods(self, genre_id: int):
        """Obtener todos los mods de un género (activos)"""
        return self.__db.query(ModGenre).filter(
            ModGenre.genre_id == genre_id,
            ModGenre.is_active == True
        ).all()
    
    def add_genre_to_mod(self, mod_id: int, genre_id: int):
        """Agregar un género a un mod (solo OWNER/EDITOR)
        
        Retorna: Tuple (mod, genre, mod_genre)
        """
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Verificar que el género existe
        genre = self.__db.query(Genre).filter(
            Genre.id == genre_id
        ).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        
        # Verificar que no existe una relación activa entre este mod y este género
        existing = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id,
            ModGenre.genre_id == genre_id,
            ModGenre.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El mod ya tiene este género")
        
        # Verificar si existe una relación inactiva para reactivarla
        existing_inactive = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id,
            ModGenre.genre_id == genre_id,
            ModGenre.is_active == False
        ).first()
        
        if existing_inactive:
            # Reactivar la relación
            existing_inactive.is_active = True
            self.__db.commit()
            self.__db.refresh(existing_inactive)
            return (mod, genre, existing_inactive)
        
        # Crear nueva relación
        mod_genre = ModGenre(
            mod_id=mod_id,
            genre_id=genre_id
        )
        self.__db.add(mod_genre)
        self.__db.commit()
        self.__db.refresh(mod_genre)
        
        return (mod, genre, mod_genre)
    
    def update_mod_genre_status(self, mod_genre_id: int, is_active: bool):
        """Actualizar el estado is_active de una relación mod-género (solo OWNER/EDITOR)"""
        mod_genre = self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id
        ).first()
        
        if not mod_genre:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        mod_genre.is_active = is_active
        self.__db.commit()
        self.__db.refresh(mod_genre)
        
        return mod_genre
    
    def _build_response_with_genre(self, mod_genre):
        """Construir respuesta con objeto completo del género en lugar de genre_id"""
        genre = self.__db.query(Genre).filter(
            Genre.id == mod_genre.genre_id
        ).first()
        
        # Construir objeto de género sin metadata de usuario
        genre_data = None
        if genre:
            genre_data = {
                "id": genre.id,
                "name": genre.name,
                "identifier": genre.identifier,
                "is_active": genre.is_active
            }
        
        resource = {
            "id": mod_genre.id,
            "mod_id": mod_genre.mod_id,
            "genre": genre_data
        }
        
        info = {
            "is_active": mod_genre.is_active,
            "created_at": mod_genre.created_at,
            "updated_at": mod_genre.updated_at,
            "created_by": mod_genre.created_by,
            "updated_by": mod_genre.updated_by
        }
        
        return resource, info
    
    def get_mod_genres_with_genre(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones activas con género (paginado)"""
        mod_genres = self.__db.query(ModGenre).filter(
            ModGenre.is_active == True
        ).offset(skip).limit(limit).all()
        
        return [self._build_response_with_genre(mg) for mg in mod_genres]
    
    def get_mod_genres_admin_with_genre(self, skip: int = 0, limit: int = 20):
        """Obtener todas las relaciones incluyendo inactivas con género (paginado)"""
        mod_genres = self.__db.query(ModGenre).offset(skip).limit(limit).all()
        
        return [self._build_response_with_genre(mg) for mg in mod_genres]
    
    def get_mod_genre_with_genre(self, mod_genre_id: int):
        """Obtener una relación específica (activa) con género"""
        mod_genre = self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id,
            ModGenre.is_active == True
        ).first()
        
        if not mod_genre:
            return None
        
        return self._build_response_with_genre(mod_genre)
    
    def get_mod_genre_admin_with_genre(self, mod_genre_id: int):
        """Obtener una relación específica (incluyendo inactivas) con género"""
        mod_genre = self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id
        ).first()
        
        if not mod_genre:
            return None
        
        return self._build_response_with_genre(mod_genre)
    
    def get_mod_all_genres_with_genre(self, mod_id: int):
        """Obtener todos los géneros de un mod (activos) con género"""
        mod_genres = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id,
            ModGenre.is_active == True
        ).all()
        
        return [self._build_response_with_genre(mg) for mg in mod_genres]
    
    def get_mod_all_genres_admin_with_genre(self, mod_id: int):
        """Obtener todos los géneros de un mod (incluyendo inactivos) con género"""
        mod_genres = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id
        ).all()
        
        return [self._build_response_with_genre(mg) for mg in mod_genres]
    
    def get_genre_all_mods_with_genre(self, genre_id: int):
        """Obtener todos los mods de un género (activos) con género"""
        mod_genres = self.__db.query(ModGenre).filter(
            ModGenre.genre_id == genre_id,
            ModGenre.is_active == True
        ).all()
        
        return [self._build_response_with_genre(mg) for mg in mod_genres]
    
    def update_genre_id(self, mod_genre_id: int, new_genre_id: int):
        """Actualizar el id_genre de una relación mod-género (solo OWNER/EDITOR)"""
        # Obtener la relación actual
        mod_genre = self.__db.query(ModGenre).filter(
            ModGenre.id == mod_genre_id
        ).first()
        
        if not mod_genre:
            raise HTTPException(status_code=404, detail="Relación mod-género no encontrada")
        
        # Verificar que el nuevo género existe
        new_genre = self.__db.query(Genre).filter(
            Genre.id == new_genre_id
        ).first()
        if not new_genre:
            raise HTTPException(status_code=404, detail="Nuevo género no encontrado")
        
        # Verificar que no existe una relación activa entre este mod y el nuevo género
        existing = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_genre.mod_id,
            ModGenre.genre_id == new_genre_id,
            ModGenre.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El mod ya tiene este nuevo género asignado")
        
        # Actualizar el género
        mod_genre.genre_id = new_genre_id
        self.__db.commit()
        self.__db.refresh(mod_genre)
        
        return mod_genre
