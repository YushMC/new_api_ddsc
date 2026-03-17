from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.generos import CRUD_GENRE
from src.middleware.jwt import get_current_user, verify_admin_role
from src.services.token import TokenUser
from src.models.enums import UserRolEnum
from src.models.generos import Genre
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
    
    # Preparar cada género con la estructura info
    prepared_genres = []
    for g in genres:
        genre_dict = ResponseBuilder._create_response_with_info(
            GenreResponse.model_validate(g),
            "success",
            "",
            force_info=True
        )
        prepared_genres.append(genre_dict["data"])
    
    return {
        "response": "success",
        "message": "Géneros obtenidos exitosamente",
        "data": prepared_genres
    }

@router.get("/admin/all")
def list_genres_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = 0,
    limit: int = 20,
    user: TokenUser = Depends(verify_admin_role)
):
    """Listar todos los géneros incluyendo inactivos (solo para OWNER/EDITOR)"""
    crud = CRUD_GENRE(db)
    genres = crud.get_generos_admin(skip, limit)
    
    # Preparar cada género con la estructura info
    prepared_genres = []
    for g in genres:
        genre_dict = ResponseBuilder._create_response_with_info(
            GenreResponse.model_validate(g),
            "success",
            "",
            force_info=True
        )
        prepared_genres.append(genre_dict["data"])
    
    return {
        "response": "success",
        "message": "Géneros obtenidos exitosamente (incluyendo inactivos)",
        "data": prepared_genres
    }

@router.get("/{genre_id}")
def get_genre(genre_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Obtener un género específico (requiere autenticación OWNER/EDITOR)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para obtener géneros")
    
    crud = CRUD_GENRE(db)
    genre = crud.get_genero(genre_id)
    return ResponseBuilder.success(
        data=GenreResponse.model_validate(genre),
        message="Género obtenido exitosamente",
        force_info=True
    )

@router.get("/admin/{genre_id}")
def get_genre_admin(
    genre_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener un género específico incluyendo inactivos (solo OWNER/EDITOR)"""
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return ResponseBuilder.success(
        data=GenreResponse.model_validate(genre),
        message="Género obtenido exitosamente",
        force_info=True
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
        message="Género creado exitosamente",
        force_info=True
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
        message="Género actualizado exitosamente",
        force_info=True
    )

@router.delete("/{genre_id}")
def delete_genre(genre_id: int, user: TokenUser = Depends(get_current_user), db: Session = Depends(db_init.get_db)):
    """Eliminar un género (soft delete, requiere autenticación EDITOR/OWNER)"""
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar géneros")
    
    crud = CRUD_GENRE(db)
    crud.delete_genero(genre_id)
    return ResponseBuilder.deleted(message="Género eliminado exitosamente")
