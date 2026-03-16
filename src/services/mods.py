from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas.mods import ModBase
from src.models.mods import Mod
from src.models.enums import UserRolEnum
from src.services.token import TokenUser
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


class CRUD_MOD:
    def __init__(self, db: Session) -> None:
        self.__db = db

    def create_mod(self, data: ModBase, user: TokenUser):
        if not user.id and user.id == 0:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        # Check for duplicate slug
        existing_mod = self.__db.query(Mod).filter(Mod.slug == data.slug).first()
        if existing_mod:
            raise HTTPException(status_code=400, detail=f"Mod con slug '{data.slug}' ya existe")
        
        mod = Mod(**data.model_dump())

        mod.required_revision = user.rol == UserRolEnum.UPLOADER
        mod.is_active = user.rol != UserRolEnum.UPLOADER
        mod.created_by = str(user.name)
        mod.updated_by = str(user.name)

        self.__db.add(mod)
        self.__db.commit()
        self.__db.refresh(mod)

        # Retornar el mod (la ruta lo pasará a BackgroundTasks)
        return mod
    
    def get_mod(self, mod_id: int):
        return self.__db.query(Mod).filter(Mod.id == mod_id, Mod.is_active == True).first()

    def get_mods(self, skip: int = 0, limit: int = 20):
        return self.__db.query(Mod).filter(Mod.is_active == True).offset(skip).limit(limit).all()
    
    def update_mod(self, mod_id: int, data: ModBase, user: TokenUser):
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()

        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        # Guardar valores anteriores para detectar cambios
        changes = {}
        for key, value in data.model_dump().items():
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
                mod.approved_at = datetime.now(UTC)
        
        mod.updated_by = str(user.name)

        self.__db.commit()
        self.__db.refresh(mod)

        # Retornar tuple (mod, changes) para que la ruta lo pase a BackgroundTasks
        return (mod, changes)
    
    def delete_mod(self, mod_id: int, user: TokenUser):
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()

        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        mod.is_active = False
        mod.deleted_by = str(user.name)
        self.__db.commit()
        self.__db.refresh(mod)

        return mod
