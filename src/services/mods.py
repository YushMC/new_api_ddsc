from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas.mods import ModBase
from src.models.mods import Mod
from src.models.enums import UserRolEnum
from src.services.token import TokenUser

class CRUD_MOD:
    def __init__(self, db:Session) -> None:
        self.__db =  db

    def create_mod(self, data:ModBase, user:TokenUser):
        if not user.id and user.id == 0:
            raise HTTPException(status_code=403, detail="Sin autorización")
        
        mod = Mod(**data.model_dump())

        mod.required_revision = True if user.rol == UserRolEnum.UPLOADER else False
        mod.is_active = False if user.rol == UserRolEnum.UPLOADER else True
        mod.created_by = str(user.name)
        mod.updated_by = str(user.name)

        self.__db.add(mod)
        self.__db.commit()
        self.__db.refresh(mod)

        return mod
    
    def get_mod(self, mod_id: int):
        return self.__db.query(Mod).filter(Mod.id == mod_id, Mod.is_active == True).first()

    def get_mods(self, skip: int = 0, limit: int = 20):
        return self.__db.query(Mod).filter(Mod.is_active == True).offset(skip).limit(limit).all()
    
    def update_mod(self, mod_id: int, data: ModBase, user:TokenUser):
        if user.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="Sin autorización")
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()

        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        for key, value in data.model_dump().items():
            if hasattr(mod, key):
                setattr(mod, key, value)
        
        mod.updated_by = str(user.name)

        self.__db.commit()
        self.__db.refresh(mod)

        return mod
    
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