from src.schemas.mods import ModBase, ModCommplete
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from src.middleware.jwt import get_current_user
from src.conf.database import DATABASE_INIT
from src.services.mods import CRUD_MOD
from src.services.token import TokenUser
from src.background_tasks import notify_mod_created, notify_mod_updated
from src.utils.response_builder import ResponseBuilder
from src.utils.discord_notifier import DiscordNotifier
from src.models.enums import UserRolEnum
from sqlalchemy.orm import Session

router = APIRouter()
db_init = DATABASE_INIT()


def _prepare_mod_response(mod, db: Session):
    """Prepara un mod para la respuesta, incluendo créditos organizados e imágenes"""
    from src.schemas.imagenes import ImageResponse
    
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
    
    return mod_dict

@router.get("/all")
def list_mods(db: Session = Depends(db_init.get_db)):
    """Listar todos los mods activos (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mods = crud.get_mods()
    
    # Preparar respuesta con estructura individual para cada mod
    prepared_mods = []
    for m in mods:
        mod_dict = _prepare_mod_response(m, db)
        
        # Separar info y credits para estructura consistente con GET individual
        from src.utils.response_builder import ResponseBuilder
        response_structure = ResponseBuilder._create_response_with_info(
            mod_dict, 
            "success", 
            ""  # Sin mensaje individual, solo para estructura
        )
        # Extraer solo la estructura de data
        prepared_mods.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Mods obtenidos exitosamente",
        "data": prepared_mods
    }

@router.get("/{mod_id}")
def get_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un mod específico por ID (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mod = crud.get_mod(mod_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    return ResponseBuilder.success(
        data=_prepare_mod_response(mod, db),
        message="Mod obtenido exitosamente"
    )

@router.post("")
def create_mod_route(
    data: ModBase,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Crear un nuevo mod (requiere autenticación)"""
    crud = CRUD_MOD(db)
    mod = crud.create_mod(data, user)
    
    # Si es UPLOADER, crear notificaciones para EDITORS/OWNERS
    if user.rol == UserRolEnum.UPLOADER:
        from src.services.notifications import CRUD_NOTIFICATION
        notification_crud = CRUD_NOTIFICATION(db)
        background_tasks.add_task(
            notification_crud.notify_mod_pending_review,
            mod_id=mod.id,
            mod_name=mod.name,
            uploader_name=user.name
        )
    
    # Agregar notificación a Discord como background task (no bloquea respuesta)
    background_tasks.add_task(notify_mod_created, mod, user)
    
    return ResponseBuilder.created(
        data=_prepare_mod_response(mod, db),
        message="Mod creado exitosamente"
    )

@router.put("/{mod_id}")
def update_mod_route(
    mod_id: int,
    data: ModBase,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Actualizar un mod existente (requiere autenticación)"""
    crud = CRUD_MOD(db)
    mod, changes = crud.update_mod(mod_id, data, user)
    
    # Agregar notificación a Discord como background task (no bloquea respuesta)
    background_tasks.add_task(notify_mod_updated, mod, user, changes)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Mod actualizado exitosamente"
    )

@router.delete("/{mod_id}")
def delete_mod_route(
    mod_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db)
):
    """Eliminar un mod (soft delete, requiere autenticación)"""
    crud = CRUD_MOD(db)
    mod = crud.delete_mod(mod_id, user)
    return ResponseBuilder.deleted(message="Mod eliminado exitosamente")

@router.post("/{mod_id}/approve")
def approve_mod_route(
    mod_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Aprobar un mod que requiere revisión (requiere EDITOR/OWNER)
    
    - Solo aprueba si required_revision es True
    - Establece required_revision a False
    - Marca approved_at y approved_by
    - Crea notificación para el uploader
    - Envía notificación a Discord
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para aprobar mods")
    
    crud = CRUD_MOD(db)
    mod, changes = crud.approve_mod(mod_id, user)
    
    # Crear notificación para el uploader (creador del mod)
    from src.services.notifications import CRUD_NOTIFICATION
    notification_crud = CRUD_NOTIFICATION(db)
    
    # El mod tiene el id del usuario que lo creó en created_by, pero necesitamos el user_id
    # Debemos obtener el usuario que creó el mod
    from src.models.users import User
    creator = db.query(User).filter(User.name == mod.created_by).first()
    if creator:
        notification_crud.notify_mod_approved(
            mod_id=mod_id,
            mod_name=mod.name,
            mod_creator_id=creator.id,
            approved_by=user.name
        )
    
    # Agregar notificación a Discord como background task
    background_tasks.add_task(DiscordNotifier.notify_mod_approved, mod, user)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Mod aprobado exitosamente"
    )