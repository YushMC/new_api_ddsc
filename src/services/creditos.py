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
    
    def get_credits_by_user(self, user_id: int):
        """Obtener todos los créditos de un usuario específico con información del mod"""
        # Verificar que el usuario existe
        user = self.__db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return self.__db.query(Credit).filter(
            Credit.id_user == user_id,
            Credit.is_active == True
        ).all()
    
    def get_credits_admin(self, skip: int = 0, limit: int = 20):
        """Obtener todos los créditos (incluyendo inactivos) - Solo para administradores"""
        return self.__db.query(Credit).offset(skip).limit(limit).all()
    
    def get_credits_admin_all(self):
        """Obtener TODOS los créditos sin paginación (incluyendo inactivos) - Solo para administradores"""
        return self.__db.query(Credit).all()
    
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
        if credit_type == CreditsTypeEnum.PORTER and credit.type != CreditsTypeEnum.PORTER:  # type: ignore
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
    
    def create_credits_batch(self, id_mod: int, credits_data: list[dict]):
        """Crear múltiples créditos para un mod en una sola operación
        
        Args:
            id_mod: ID del mod
            credits_data: Lista de diccionarios con {id_user, name, type}
        
        Returns:
            Lista de créditos creados
        """
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == id_mod).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")
        
        created_credits = []
        porter_count = 0
        
        # Validar y procesar cada crédito antes de crear
        for credit_data in credits_data:
            id_user = credit_data.get("id_user")
            name = credit_data.get("name")
            credit_type = credit_data.get("type")
            
            # Validar que al menos id_user o name esté presente
            if id_user is None and name is None:
                raise HTTPException(status_code=400, detail="Cada crédito debe tener id_user o name")
            
            # Si id_user está presente, verificar que el usuario existe
            if id_user is not None:
                user = self.__db.query(User).filter(User.id == id_user).first()
                if not user:
                    raise HTTPException(status_code=404, detail=f"Usuario {id_user} no encontrado")
            
            # Contar porters
            if credit_type == CreditsTypeEnum.PORTER:
                porter_count += 1
        
        # Verificar que no haya múltiples porters
        if porter_count > 1:
            raise HTTPException(status_code=400, detail="No se pueden crear múltiples porters en un lote")
        
        # Si hay un porter, verificar que no exista otro en el mod
        if porter_count == 1:
            existing_porter = self.__db.query(Credit).filter(
                Credit.id_mod == id_mod,
                Credit.type == CreditsTypeEnum.PORTER,
                Credit.is_active == True
            ).first()
            
            if existing_porter:
                raise HTTPException(status_code=400, detail="Este mod ya tiene un porteador")
        
        # Crear todos los créditos
        for credit_data in credits_data:
            credit = Credit(
                id_mod=id_mod,
                id_user=credit_data.get("id_user"),
                name=credit_data.get("name"),
                type=credit_data.get("type")
            )
            
            self.__db.add(credit)
            created_credits.append(credit)
        
        # Hacer commit una sola vez
        self.__db.commit()
        
        # Refresh all credits
        for credit in created_credits:
            self.__db.refresh(credit)
        
        return created_credits
    
