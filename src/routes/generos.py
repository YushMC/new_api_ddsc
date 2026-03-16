from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.generos import CRUD_GENRE
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.models.enums import UserRolEnum
from src.schemas.generos import GenreCreate, GenreResponse
from pydantic import BaseModel

router = APIRouter()
get_db = DATABASE_INIT().get_db

class GenreName(BaseModel):
    """Schema para actualizar nombre de género"""
    name: str

@router.get("", response_model=list[GenreResponse])
def list_genres(db: Session = Depends(get_db)):
    """Listar todos los géneros activos"""
    crud = CRUD_GENRE(db)
    return crud.get_generos()

@router.get("/{genre_id}", response_model=GenreResponse)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    """Obtener un género específico"""
    crud = CRUD_GENRE(db)
    return crud.get_genero(genre_id)

@router.post("", response_model=GenreResponse)
def create_genre(genre_data: GenreCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Crear nuevo género (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear géneros")
    
    crud = CRUD_GENRE(db)
    return crud.create_genero(genre_data.name)

@router.put("/{genre_id}", response_model=GenreResponse)
def update_genre(genre_id: int, genre_data: GenreName, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualizar un género (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar géneros")
    
    crud = CRUD_GENRE(db)
    return crud.update_genero(genre_id, genre_data.name)

@router.delete("/{genre_id}")
def delete_genre(genre_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar un género (soft delete, requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar géneros")
    
    crud = CRUD_GENRE(db)
    crud.delete_genero(genre_id)
    return {"message": "Género eliminado"}
