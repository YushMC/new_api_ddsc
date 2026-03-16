from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.generos import CRUD_GENRE
from src.middleware.jwt import get_current_user
from src.services.token import TokenUser
from src.models.enums import UserRolEnum
from src.schemas.generos import GenreCreate, GenreResponse
from src.schemas.response import ApiResponse, ApiListResponse
from src.utils.response_builder import ResponseBuilder
from pydantic import BaseModel

router = APIRouter()
db_init = DATABASE_INIT()

class GenreName(BaseModel):
    """Schema para actualizar nombre de género"""
    name: str

@router.get("")
def list_genres(user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Listar todos los géneros activos (requiere autenticación OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para listar géneros")
    
    crud = CRUD_GENRE(db)
    genres = crud.get_generos()
    return ResponseBuilder.list_response(
        data=[GenreResponse.model_validate(g) for g in genres],
        message="Géneros obtenidos exitosamente"
    )

@router.get("/{genre_id}")
def get_genre(genre_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Obtener un género específico (requiere autenticación OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para obtener géneros")
    
    crud = CRUD_GENRE(db)
    genre = crud.get_genero(genre_id)
    return ResponseBuilder.success(
        data=GenreResponse.model_validate(genre),
        message="Género obtenido exitosamente"
    )

@router.post("")
def create_genre(genre_data: GenreCreate, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Crear nuevo género (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para crear géneros")
    
    crud = CRUD_GENRE(db)
    genre = crud.create_genero(genre_data.name)
    return ResponseBuilder.created(
        data=GenreResponse.model_validate(genre),
        message="Género creado exitosamente"
    )

@router.put("/{genre_id}")
def update_genre(genre_id: int, genre_data: GenreName, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Actualizar un género (requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar géneros")
    
    crud = CRUD_GENRE(db)
    genre = crud.update_genero(genre_id, genre_data.name)
    return ResponseBuilder.updated(
        data=GenreResponse.model_validate(genre),
        message="Género actualizado exitosamente"
    )

@router.delete("/{genre_id}")
def delete_genre(genre_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Eliminar un género (soft delete, requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar géneros")
    
    crud = CRUD_GENRE(db)
    crud.delete_genero(genre_id)
    return ResponseBuilder.deleted(message="Género eliminado exitosamente")
