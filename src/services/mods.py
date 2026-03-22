from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas.mods import ModBase
from src.models.mods import Mod
from src.models.mod_genre import ModGenre
from src.models.enums import UserRolEnum, CreditsTypeEnum
from src.services.token import TokenUser
from src.utils.slug_normalizer import normalize_slug
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


class CRUD_MOD:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    @staticmethod
    def _enrich_credit_with_user(credit, db: Session):
        """
        Enriquece un crédito con la información del usuario si existe.
        - Si tiene id_user: solo retorna {id, type, user}
        - Si no tiene id_user: retorna {id, id_mod, id_user, name, type, is_active}
        """
        from src.models.users import User
        
        # Si tiene id_user, solo retornar user object
        if credit.id_user:
            user = db.query(User).filter(User.id == credit.id_user).first()
            if user:
                return {
                    "id": credit.id,
                    "type": credit.type,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "contact": user.contact,
                        "logo": user.logo
                    }
                }
        
        # Si no tiene id_user, retornar datos del crédito
        return {
            "id": credit.id,
            "id_mod": credit.id_mod,
            "id_user": credit.id_user,
            "name": credit.name,
            "type": credit.type,
            "is_active": credit.is_active
        }
    
    @staticmethod
    def _organize_credits(mod, db: Session):
        """
        Organiza los créditos del mod por tipo
        """
        organized = {
            "creators": [],
            "translators": [],
            "porters": []
        }
        
        if not hasattr(mod, 'credits') or not mod.credits:
            return organized
        
        for credit in mod.credits:
            enriched = CRUD_MOD._enrich_credit_with_user(credit, db)
            
            if credit.type == CreditsTypeEnum.ORIGINAL_CREATOR:
                organized["creators"].append(enriched)
            elif credit.type == CreditsTypeEnum.TRANSLATOR:
                organized["translators"].append(enriched)
            elif credit.type == CreditsTypeEnum.PORTER:
                organized["porters"].append(enriched)
        
        return organized

    def create_mod(self, data: ModBase, user: TokenUser):
        if not user.id and user.id == 0:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        # Generar slug del nombre si no se proporciona
        if not data.slug:
            normalized_slug = normalize_slug(data.name)
        else:
            normalized_slug = normalize_slug(data.slug)
        
        # Check for duplicate slug
        existing_mod = self.__db.query(Mod).filter(Mod.slug == normalized_slug).first()
        if existing_mod:
            raise HTTPException(status_code=400, detail=f"Mod con slug '{normalized_slug}' ya existe")
        
        # Crear mod con datos normalizados
        mod_data = data.model_dump()
        mod_data['slug'] = normalized_slug
        
        # Si no se proporciona created_at, dejarlo None (será automático en la BD)
        # Si se proporciona, usarlo
        if mod_data.get('created_at') is None:
            del mod_data['created_at']
        
        mod = Mod(**mod_data)

        mod.required_revision = user.rol == UserRolEnum.UPLOADER
        mod.is_active = user.rol != UserRolEnum.UPLOADER
        mod.created_by = user.id
        mod.updated_by = user.id

        self.__db.add(mod)
        self.__db.commit()
        self.__db.refresh(mod)

        # Retornar el mod (la ruta lo pasará a BackgroundTasks)
        return mod
    
    def get_mod(self, mod_id: int):
        return self.__db.query(Mod).filter(Mod.id == mod_id, Mod.is_active == True).first()

    def get_mods(self, skip: int = 0, limit: int = 20):
        return self.__db.query(Mod).filter(Mod.is_active == True).offset(skip).limit(limit).all()
    
    def get_mods_by_creator(self, user_id: int, skip: int = 0, limit: int = 20):
        """Obtener todos los mods creados por un usuario específico"""
        return self.__db.query(Mod).filter(Mod.created_by == user_id).offset(skip).limit(limit).all()
    
    def get_mods_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todos los mods (incluyendo inactivos) excluyendo los que requieren revisión - Solo para administradores"""
        return self.__db.query(Mod).filter(Mod.required_revision == False).offset(skip).limit(limit).all()
    
    def get_mods_pending_revision(self, skip: int = 0, limit: int = 20):
        """Obtener todos los mods que requieren revisión - Solo para administradores"""
        return self.__db.query(Mod).filter(Mod.required_revision == True).offset(skip).limit(limit).all()
    
    def update_mod(self, mod_id: int, data: ModBase, user: TokenUser):
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()

        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        # Guardar valores anteriores para detectar cambios
        changes = {}
        mod_data = data.model_dump()
        
        # Normalizar slug si se proporciona y no es None
        if 'slug' in mod_data and mod_data['slug'] is not None:
            mod_data['slug'] = normalize_slug(mod_data['slug'])
            # Verificar que el nuevo slug no exista en otro mod
            if mod_data['slug'] != mod.slug:
                existing_slug = self.__db.query(Mod).filter(
                    Mod.slug == mod_data['slug'],
                    Mod.id != mod_id
                ).first()
                if existing_slug:
                    raise HTTPException(status_code=400, detail=f"Mod con slug '{mod_data['slug']}' ya existe")
        
        # Campos que NO pueden ser None (requeridos)
        required_fields = {'name', 'status', 'duration', 'character'}
        
        for key, value in mod_data.items():
            # Saltar campos None para campos no requeridos, pero rechazar None para campos requeridos
            if value is None and key in required_fields:
                raise HTTPException(status_code=400, detail=f"Campo requerido '{key}' no puede ser None")
            
            # Saltar si el valor es None (para campos opcionales)
            if value is None:
                continue
            
            if hasattr(mod, key):
                old_value = getattr(mod, key)
                if old_value != value:
                    changes[key] = {
                        "old": old_value,
                        "new": value
                    }
                setattr(mod, key, value)
        
        # Si se aprueba (required_revision cambia de True a False), marcar approved_at
        if "required_revision" in changes:
            old_val = changes["required_revision"]["old"]
            new_val = changes["required_revision"]["new"]
            if old_val == True and new_val == False:
                mod.approved_at = datetime.now(UTC) # type: ignore
        
        mod.updated_by = user.id

        self.__db.commit()
        self.__db.refresh(mod)

        # Retornar tuple (mod, changes) para que la ruta lo pase a BackgroundTasks
        return (mod, changes)
    
    def delete_mod(self, mod_id: int, user: TokenUser, reason: str = ""):
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()

        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        mod.is_active = False
        mod.deleted_by = user.id # type: ignore
        mod.deleted_at = datetime.now(UTC)  # type: ignore
        if reason:
            mod.comments = reason  # type: ignore
        self.__db.commit()
        self.__db.refresh(mod)

        return mod
    
    def is_mod_complete(self, mod_id: int) -> bool:
        """
        Verifica si un mod está completo (tiene imágenes Y al menos un crédito activo)
        
        Args:
            mod_id: ID del mod
        
        Returns:
            True si tiene imágenes y créditos, False en caso contrario
        """
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        
        if not mod:
            return False
        
        # Verificar que tiene al menos una imagen
        has_images = len([img for img in mod.images if img.is_active]) > 0 if hasattr(mod, 'images') and mod.images else False
        
        # Verificar que tiene al menos un crédito
        has_credits = len([c for c in mod.credits if c.is_active]) > 0 if hasattr(mod, 'credits') and mod.credits else False
        
        return has_images and has_credits
    
    def approve_mod(self, mod_id: int, user: TokenUser):
        """
        Aprueba un mod (solo si required_revision es True)
        
        Args:
            mod_id: ID del mod a aprobar
            user: Usuario que aprueba (debe ser EDITOR/OWNER)
        
        Returns:
            Tuple (mod, changes) con el mod actualizado y los cambios
        """
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización para aprobar mods")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        if not mod.required_revision: #type: ignore
            raise HTTPException(status_code=400, detail="Este mod no requiere revisión")
        
        changes = {
            "required_revision": {
                "old": True,
                "new": False
            }
        }
        
        mod.required_revision = False #type: ignore
        mod.approved_by = user.id # type: ignore
        mod.approved_at = datetime.now(UTC)  # type: ignore
        mod.updated_by = user.id
        
        self.__db.commit()
        self.__db.refresh(mod)
        
        return (mod, changes)
    
    def reject_mod(self, mod_id: int, user: TokenUser, comments: str):
        """
        Rechaza un mod (solo si required_revision es True)
        
        Args:
            mod_id: ID del mod a rechazar
            user: Usuario que rechaza (debe ser EDITOR/OWNER)
            comments: Comentarios/razón del rechazo
        
        Returns:
            Tuple (mod, changes) con el mod actualizado y los cambios
        """
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización para rechazar mods")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        if not mod.required_revision: #type: ignore
            raise HTTPException(status_code=400, detail="Este mod no requiere revisión")
        
        changes = {
            "required_revision": {
                "old": True,
                "new": False
            },
            "rejected": {
                "old": False,
                "new": True
            }
        }
        
        mod.required_revision = False #type: ignore
        mod.rejected_by = user.id # type: ignore
        mod.rejected_at = datetime.now(UTC)  # type: ignore
        mod.comments = comments  # type: ignore
        mod.updated_by = user.id
        
        self.__db.commit()
        self.__db.refresh(mod)
        
        return (mod, changes)
    
    def add_genres_to_mod(self, mod_id: int, genre_ids: list[int]):
        """
        Agrega géneros a un mod
        - Si el genre ya existe y está activo: no hace nada
        - Si el genre existe pero está soft-deleted: lo reactiva
        - Si el genre no existe: crea una nueva asociación
        
        Args:
            mod_id: ID del mod
            genre_ids: Lista de IDs de géneros a agregar
        
        Returns:
            Tuple (mod, genres_added) con el mod y lista de géneros agregados
        """
        from src.models.generos import Genre
        
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Verificar que todos los géneros existen
        genres = self.__db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        if len(genres) != len(genre_ids):
            raise HTTPException(status_code=400, detail="Algunos géneros no existen")
        
        # Crear un diccionario {id: genre} para acceso rápido
        genre_dict = {g.id: g for g in genres}
        genres_added = []
        
        # Agregar géneros al mod (evitar duplicados activos)
        for genre_id in genre_ids:
            # Verificar si existe una asociación (activa o inactiva)
            existing = self.__db.query(ModGenre).filter(
                ModGenre.mod_id == mod_id,
                ModGenre.genre_id == genre_id
            ).first()
            
            if existing:
                # Si existe pero está inactivo, reactivarlo
                if not existing.is_active:
                    existing.is_active = True
                    self.__db.commit()
                    genres_added.append(genre_dict[genre_id])
                # Si ya está activo, no hacer nada
            else:
                # Crear nueva asociación
                new_association = ModGenre(
                    mod_id=mod_id,
                    genre_id=genre_id,
                    is_active=True
                )
                self.__db.add(new_association)
                self.__db.commit()
                genres_added.append(genre_dict[genre_id])
        
        self.__db.refresh(mod)
        
        return (mod, genres_added)
    
    def remove_genres_from_mod(self, mod_id: int, genre_ids: list[int]):
        """
        Remueve géneros de un mod (soft delete - marca como inactivo)
        
        Args:
            mod_id: ID del mod
            genre_ids: Lista de IDs de géneros a remover
        
        Returns:
            Tuple (mod, genres_removed) con el mod y lista de géneros removidos
        """
        from src.models.generos import Genre
        
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Obtener la información de los géneros a remover
        genres_to_remove = self.__db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        
        # Soft delete: marcar las asociaciones como inactivas
        mod_genres = self.__db.query(ModGenre).filter(
            ModGenre.mod_id == mod_id,
            ModGenre.genre_id.in_(genre_ids)
        ).all()
        
        for mod_genre in mod_genres:
            mod_genre.is_active = False
        
        self.__db.commit()
        self.__db.refresh(mod)
        
        return (mod, genres_to_remove)
    
    def get_mod_genres(self, mod_id: int):
        """
        Obtiene los géneros activos de un mod
        
        Args:
            mod_id: ID del mod
        
        Returns:
            Lista de géneros activos del mod
        """
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Retornar solo los géneros activos
        if hasattr(mod, 'mod_genres') and mod.mod_genres:
            return [mg.genre for mg in mod.mod_genres if mg.is_active]
        
        return []

