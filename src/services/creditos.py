from sqlalchemy.orm import Session
from src.models.credits import Credit
from src.models.users import User
from src.models.mods import Mod
from fastapi import HTTPException
from src.models.enums import CreditsTypeEnum


class CRUD_CREDITS:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    def get_credits_by_mod(self, mod_id: int):
        """Obtener todos los créditos de un mod activos"""
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        return self.__db.query(Credit).filter(
            Credit.id_mod == mod_id,
            Credit.is_active == True
        ).all()
    
    def get_credit(self, credit_id: int):
        """Obtener un crédito específico"""
        credit = self.__db.query(Credit).filter(
            Credit.id == credit_id,
            Credit.is_active == True
        ).first()
        
        if not credit:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
        
        return credit
    
    def create_credit(self, id_mod: int, id_user: int | None, name: str | None, credit_type: CreditsTypeEnum):
        """Crear nuevo crédito"""
        # Verificar que al menos id_user o name esté presente
        if id_user is None and name is None:
            raise HTTPException(status_code=400, detail="Debe proporcionar id_user o name")
        
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == id_mod).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        # Si id_user está presente, verificar que el usuario existe
        if id_user is not None:
            user = self.__db.query(User).filter(User.id == id_user).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Si es porter, verificar que no exista otro porter para este mod
        if credit_type == CreditsTypeEnum.PORTER:
            existing_porter = self.__db.query(Credit).filter(
                Credit.id_mod == id_mod,
                Credit.type == CreditsTypeEnum.PORTER,
                Credit.is_active == True
            ).first()
            
            if existing_porter:
                raise HTTPException(status_code=400, detail="Este mod ya tiene un porteador")
        
        credit = Credit(
            id_mod=id_mod,
            id_user=id_user,
            name=name,
            type=credit_type
        )
        
        self.__db.add(credit)
        self.__db.commit()
        self.__db.refresh(credit)
        
        return credit
    
    def update_credit(self, credit_id: int, id_user: int | None = None, name: str | None = None, credit_type: CreditsTypeEnum | None = None):
        """Actualizar un crédito"""
        credit = self.__db.query(Credit).filter(Credit.id == credit_id).first()
        
        if not credit:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
        
        # Validar que al menos uno de los campos esté presente
        if id_user is None and name is None and credit_type is None:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un campo para actualizar")
        
        # Si se actualiza el tipo a porter, verificar que no exista otro
        if credit_type == CreditsTypeEnum.PORTER and credit.type != CreditsTypeEnum.PORTER:
            existing_porter = self.__db.query(Credit).filter(
                Credit.id_mod == credit.id_mod,
                Credit.type == CreditsTypeEnum.PORTER,
                Credit.is_active == True,
                Credit.id != credit_id
            ).first()
            
            if existing_porter:
                raise HTTPException(status_code=400, detail="Este mod ya tiene un porteador")
        
        # Si id_user está presente, verificar que el usuario existe
        if id_user is not None:
            user = self.__db.query(User).filter(User.id == id_user).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            credit.id_user = id_user #type: ignore
        
        if name is not None:
            credit.name = name #type: ignore
        
        if credit_type is not None:
            credit.type = credit_type #type: ignore
        
        self.__db.commit()
        self.__db.refresh(credit)
        
        return credit
    
    def delete_credit(self, credit_id: int):
        """Eliminar un crédito (soft delete)"""
        credit = self.__db.query(Credit).filter(Credit.id == credit_id).first()
        
        if not credit:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
        
        credit.is_active = False
        self.__db.commit()
        self.__db.refresh(credit)
        
        return credit
