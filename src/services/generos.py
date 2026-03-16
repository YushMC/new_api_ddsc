from sqlalchemy.orm import Session
from src.models.generos import Genre
from fastapi import HTTPException

class CRUD_GENRE:
    def __init__(self, db: Session) -> None:
        self.__db = db

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

        genero = Genre(name=nombre)

        self.__db.add(genero)
        self.__db.commit()
        self.__db.refresh(genero)

        return genero

    def update_genero(self, genre_id: int, nombre: str):
        """Actualizar un género"""
        genero = self.__db.query(Genre).filter(Genre.id == genre_id).first()
        
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        
        genero.name = nombre
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