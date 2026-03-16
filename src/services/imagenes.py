from sqlalchemy.orm import Session
from src.models.imagen import Image
from src.models.mods import Mod
from src.models.enums import ImageTypeEnum
from fastapi import HTTPException

class CRUD_IMAGE:
    def __init__(self, db: Session) -> None:
        self.__db = db

    def create_imagen(self, data: dict):
        """Crear nueva imagen"""
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == data["mod_id"]).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        imagen = Image(**data)

        self.__db.add(imagen)
        self.__db.commit()
        self.__db.refresh(imagen)

        return imagen

    def get_imagenes_mod(self, mod_id: int):
        """Obtener todas las imágenes de un mod"""
        # Verificar que el mod existe
        mod = self.__db.query(Mod).filter(Mod.id == mod_id).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Mod no encontrado")

        return self.__db.query(Image).filter(
            Image.mod_id == mod_id, 
            Image.is_active == True
        ).all()
    
    def get_imagen(self, imagen_id: int):
        """Obtener una imagen específica"""
        imagen = self.__db.query(Image).filter(
            Image.id == imagen_id,
            Image.is_active == True
        ).first()

        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")

        return imagen

    def get_imagen_by_mod_and_type(self, mod_id: int, image_type: ImageTypeEnum):
        """Obtener una imagen específica de un mod por tipo (logo o main)"""
        return self.__db.query(Image).filter(
            Image.mod_id == mod_id,
            Image.type == image_type,
            Image.is_active == True
        ).first()

    def count_imagenes_by_mod_and_type(self, mod_id: int, image_type: ImageTypeEnum):
        """Contar imágenes por mod y tipo"""
        return self.__db.query(Image).filter(
            Image.mod_id == mod_id,
            Image.type == image_type,
            Image.is_active == True
        ).count()

    def update_imagen(self, imagen_id: int, data: dict):
        """Actualizar una imagen"""
        imagen = self.__db.query(Image).filter(
            Image.id == imagen_id,
            Image.is_active == True
        ).first()

        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")

        for key, value in data.items():
            if value is not None and hasattr(imagen, key):
                setattr(imagen, key, value)

        self.__db.commit()
        self.__db.refresh(imagen)

        return imagen

    def delete_imagen(self, imagen_id: int):
        """Eliminar una imagen (soft delete)"""
        imagen = self.__db.query(Image).filter(
            Image.id == imagen_id
        ).first()

        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")

        imagen.is_active = False
        self.__db.commit()
        self.__db.refresh(imagen)

        return imagen