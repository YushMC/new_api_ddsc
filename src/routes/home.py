from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.conf.database import DATABASE_INIT
from src.services.mods import CRUD_MOD
from src.utils.response_builder import ResponseBuilder
from src.schemas.mods import ModCommplete
from src.models.mods import Mod

router = APIRouter()
db_init = DATABASE_INIT()


def _prepare_mod_response(mod, db: Session):
    """Prepara un mod para la respuesta, incluyendo créditos organizados, imágenes y géneros"""
    from src.schemas.imagenes import ImageResponse
    from src.schemas.generos import GenreResponse
    
    mod_dict = ModCommplete.model_validate(mod).model_dump()
    
    # Organizar créditos si existen
    credits = CRUD_MOD._organize_credits(mod, db)
    mod_dict['credits'] = credits
    
    # Agregar imágenes activas si existen
    images = []
    if hasattr(mod, 'images') and mod.images:
        images = [
            ImageResponse.model_validate(img).model_dump()
            for img in mod.images if img.is_active
        ]
    mod_dict['images'] = images
    
    # Agregar géneros activos si existen
    genres = []
    crud = CRUD_MOD(db)
    mod_genres = crud.get_mod_genres(mod.id)
    if mod_genres:
        genres = [
            GenreResponse.model_validate(g).model_dump()
            for g in mod_genres
        ]
    mod_dict['genres'] = genres
    
    return mod_dict


@router.get("/latest")
def get_latest_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener los 10 mods más recientes (públicamente disponible)
    
    Retorna:
    - Lista de los 10 mods más recientes ordenados por fecha de creación
    """
    try:
        crud = CRUD_MOD(db)
        mods = crud.get_latest_mods(limit=10)
        
        prepared_mods = []
        for m in mods:
            mod_dict = _prepare_mod_response(m, db)
            
            response_structure = ResponseBuilder._create_response_with_info(
                mod_dict,
                "success",
                "",
                db=db
            )
            prepared_mods.append(response_structure["data"])
        
        return {
            "response": "success",
            "message": "Mods más recientes obtenidos exitosamente",
            "data": prepared_mods
        }
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/most-searched")
def get_most_searched_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener los 10 mods más buscados (públicamente disponible)
    
    Retorna:
    - Lista de los 10 mods más buscados ordenados por búsquedas
    """
    try:
        crud = CRUD_MOD(db)
        mods = crud.get_most_searched_mods(limit=10)
        
        prepared_mods = []
        for m in mods:
            mod_dict = _prepare_mod_response(m, db)
            
            response_structure = ResponseBuilder._create_response_with_info(
                mod_dict,
                "success",
                "",
                db=db
            )
            prepared_mods.append(response_structure["data"])
        
        return {
            "response": "success",
            "message": "Mods más buscados obtenidos exitosamente",
            "data": prepared_mods
        }
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/most-downloaded-pc")
def get_most_downloaded_pc_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener los 10 mods más descargados para PC (públicamente disponible)
    
    Retorna:
    - Lista de los 10 mods más descargados para PC ordenados por descargas
    """
    try:
        crud = CRUD_MOD(db)
        mods = crud.get_most_downloaded_pc_mods(limit=10)
        
        prepared_mods = []
        for m in mods:
            mod_dict = _prepare_mod_response(m, db)
            
            response_structure = ResponseBuilder._create_response_with_info(
                mod_dict,
                "success",
                "",
                db=db
            )
            prepared_mods.append(response_structure["data"])
        
        return {
            "response": "success",
            "message": "Mods más descargados para PC obtenidos exitosamente",
            "data": prepared_mods
        }
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)


@router.get("/most-downloaded-android")
def get_most_downloaded_android_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener los 10 mods más descargados para Android (públicamente disponible)
    
    Retorna:
    - Lista de los 10 mods más descargados para Android ordenados por descargas
    """
    try:
        crud = CRUD_MOD(db)
        mods = crud.get_most_downloaded_android_mods(limit=10)
        
        prepared_mods = []
        for m in mods:
            mod_dict = _prepare_mod_response(m, db)
            
            response_structure = ResponseBuilder._create_response_with_info(
                mod_dict,
                "success",
                "",
                db=db
            )
            prepared_mods.append(response_structure["data"])
        
        return {
            "response": "success",
            "message": "Mods más descargados para Android obtenidos exitosamente",
            "data": prepared_mods
        }
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)
