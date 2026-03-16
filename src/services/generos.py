from sqlalchemy.orm import Session
from src.models.generos import Genre
from fastapi import HTTPException
import re

class CRUD_GENRE:
    def __init__(self, db: Session) -> None:
        self.__db = db
    
    @staticmethod
    def _generate_identifier(name: str) -> str:
        """Genera un identifier a partir del nombre (minúsculas, sin espacios especiales)"""
        # Convertir a minúsculas
        identifier = name.lower()
        # Reemplazar espacios por guiones
        identifier = identifier.replace(" ", "-")
        # Remover caracteres especiales, mantener solo letras, números y guiones
        identifier = re.sub(r'[^a-z0-9\-]', '', identifier)
        # Remover guiones múltiples
        identifier = re.sub(r'-+', '-', identifier)
        # Remover guiones al inicio y final
        identifier = identifier.strip('-')
        return identifier

    def get_generos(self):
        """Obtener todos los géneros activos"""
        return self.__db.query(Genre).filter(Genre.is_active == True).all()

    def get_genero(self, genre_id: int):
        """Obtener un género específico"""
        genre = self.__db.query(Genre).filter(
            Genre.id == genre_id,
            Genre.is_active == True
        ).first()
        
        if not genre:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        
        return genre

    def create_genero(self, nombre: str):
        """Crear nuevo género"""
        # Verificar que no exista con el mismo nombre
        existing = self.__db.query(Genre).filter(
            Genre.name == nombre,
            Genre.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="El género ya existe")
        
        # Generar identifier
        identifier = self._generate_identifier(nombre)
        
        # Verificar que el identifier sea único
        existing_identifier = self.__db.query(Genre).filter(
            Genre.identifier == identifier
        ).first()
        
        if existing_identifier:
            raise HTTPException(status_code=400, detail=f"El identifier '{identifier}' ya existe")

        genero = Genre(name=nombre, identifier=identifier)

        self.__db.add(genero)
        self.__db.commit()
        self.__db.refresh(genero)

        return genero

    def update_genero(self, genre_id: int, nombre: str):
        """Actualizar un género"""
        genero = self.__db.query(Genre).filter(Genre.id == genre_id).first()
        
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        
        genero.name = nombre #type: ignore
        # Actualizar identifier basado en el nuevo nombre
        genero.identifier = self._generate_identifier(nombre) #type: ignore
        self.__db.commit() 
        self.__db.refresh(genero)
        
        return genero

    def delete_genero(self, genre_id: int):
        """Eliminar un género (soft delete)"""
        genero = self.__db.query(Genre).filter(Genre.id == genre_id).first()
        
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        
        genero.is_active = False
        self.__db.commit()
        self.__db.refresh(genero)
        
        return genero