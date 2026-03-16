from sqlalchemy.orm import Session
from src.models.users import User
from src.services.token import TokenUser
from src.utils.hash import HASH_DATA
from src.utils.jwt import JWT_TOKEN
from fastapi import HTTPException
from typing import cast
from src.models.enums import UserRolEnum

class CRUD_USERS:
    def __init__(self, db:Session) -> None:
        self.__db= db

    def get_users(self):
        return self.__db.query(User).filter(User.is_active == True).all()

    def get_user_by_id(self, user_id: int):
        """Obtener usuario por ID"""
        return self.__db.query(User).filter(User.id == user_id, User.is_active == True).first()

    def count_usuarios(self):
        """Contar total de usuarios en la BD"""
        return self.__db.query(User).count()

    def create_user(self, data: dict, token: TokenUser):
        """Crear nuevo usuario (solo EDITOR/OWNER)"""
        if token.rol == UserRolEnum.UPLOADER:
            raise HTTPException(status_code=403, detail="No autorizado para crear usuarios")
        
        if data["role"] == UserRolEnum.OWNER:
            raise HTTPException(status_code=400, detail="No se pueden crear usuarios con rol OWNER")
        
        # Verificar que el usuario no exista
        existing_user = self.__db.query(User).filter(User.name == data["name"]).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        hash_handler = HASH_DATA()
        data["password"] = hash_handler.hash_string(data["password"])

        user = User(**data)
        
        self.__db.add(user)
        self.__db.commit()
        self.__db.refresh(user)

        return user

    def create_first_owner(self, data: dict):
        """Crear primer usuario como OWNER (sin validar token) - Solo funciona si BD vacía"""
        # Verificar que no existan usuarios
        user_count = self.count_usuarios()
        if user_count > 0:
            raise HTTPException(status_code=403, detail="Ya existen usuarios en el sistema")
        
        # Verificar que el usuario no exista
        existing_user = self.__db.query(User).filter(User.name == data["name"]).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        # Hash de contraseña
        hash_handler = HASH_DATA()
        data["password"] = hash_handler.hash_string(data["password"])
        
        # Forzar role a OWNER
        data["role"] = UserRolEnum.OWNER

        user = User(**data)
        
        self.__db.add(user)
        self.__db.commit()
        self.__db.refresh(user)

        return user
    
    def login(self, username: str, password: str):
        """Autenticar usuario y retornar token"""
        user = self.__db.query(User).filter(
            User.name == username,
            User.is_active == True
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        hash_handler = HASH_DATA()
        jwt_handler = JWT_TOKEN()

        if not hash_handler.verify_password(password, cast(str, user.password)):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        token = jwt_handler.create_token(user=user)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    def update_user_logo(self, user_id: int, logo_url: str):
        """Actualizar logo del usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        setattr(user, "logo", logo_url)
        self.__db.commit()
        self.__db.refresh(user)
        return user

    def update_user_password(self, user_id: int, current_password: str, new_password: str):
        """Actualizar contraseña del usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        hash_handler = HASH_DATA()
        
        # Verificar contraseña actual
        if not hash_handler.verify_password(current_password, cast(str, user.password)):
            raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
        
        # Hash de nueva contraseña
        setattr(user, "password", hash_handler.hash_string(new_password))
        self.__db.commit()
        self.__db.refresh(user)
        return user

    def update_user_contact(self, user_id: int, contact: str):
        """Actualizar contacto del usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        setattr(user, "contact", contact)
        self.__db.commit()
        self.__db.refresh(user)
        return user