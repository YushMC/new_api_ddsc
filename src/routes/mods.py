from src.schemas.mods import ModBase, ModCommplete, ModRejectRequest, ModDeleteRequest, ModGenreAdd, ModRequestStatusUpdate
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from src.middleware.jwt import get_current_user, verify_admin_role
from src.conf.database import DATABASE_INIT
from src.services.mods import CRUD_MOD
from src.services.token import TokenUser
from src.background_tasks import notify_mod_created, notify_mod_updated, notify_genres_added, notify_genres_removed
from src.utils.response_builder import ResponseBuilder
from src.utils.discord_notifier import DiscordNotifier
from src.models.enums import UserRolEnum
from src.models.mods import Mod
from sqlalchemy.orm import Session

router = APIRouter()
db_init = DATABASE_INIT()


def _prepare_mod_response(mod, db: Session):
    """Prepara un mod para la respuesta, incluendo créditos organizados, imágenes y géneros"""
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

@router.get("/all")
def list_mods(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados.")
):
    """Listar todos los mods activos (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mods = crud.get_mods(skip, limit)
    
    # Preparar respuesta con estructura individual para cada mod
    prepared_mods = []
    for m in mods:
        mod_dict = _prepare_mod_response(m, db)
        
        # Separar info y credits para estructura consistente con GET individual
        from src.utils.response_builder import ResponseBuilder
        response_structure = ResponseBuilder._create_response_with_info(
            mod_dict, 
            "success", 
            "",  # Sin mensaje individual, solo para estructura
            db=db
        )
        # Extraer solo la estructura de data
        prepared_mods.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Mods obtenidos exitosamente",
        "data": prepared_mods
    }

@router.get("/all-unpaginated")
def list_all_mods_unpaginated(db: Session = Depends(db_init.get_db)):
    """Listar todos los mods activos sin paginación (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mods = crud.get_all_mods()
    
    # Preparar respuesta con estructura individual para cada mod
    prepared_mods = []
    for m in mods:
        mod_dict = _prepare_mod_response(m, db)
        
        # Separar info y credits para estructura consistente con GET individual
        from src.utils.response_builder import ResponseBuilder
        response_structure = ResponseBuilder._create_response_with_info(
            mod_dict, 
            "success", 
            "",  # Sin mensaje individual, solo para estructura
            db=db
        )
        # Extraer solo la estructura de data
        prepared_mods.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Todos los mods obtenidos exitosamente",
        "data": prepared_mods
    }

@router.get("/my-mods")
def list_my_mods(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados.")
):
    """Listar todos los mods creados por el usuario autenticado (cualquier rol)"""
    crud = CRUD_MOD(db)
    mods = crud.get_mods_by_creator(user.id, skip, limit)
    
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
        "message": "Mods del usuario obtenidos exitosamente",
        "data": prepared_mods
    }

@router.get("/my-mods/revision")
def list_my_mods_in_revision(
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados.")
):
    """
    Listar todos los mods del usuario que requieren revisión (con paginación)
    
    Solo muestra los mods creados por el usuario autenticado que están en estado required_revision = True
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_MOD(db)
    mods = crud.get_user_mods_in_revision(user.id, skip, limit)
    
    if not mods:
        return {
            "response": "success",
            "message": "No hay mods en revisión",
            "data": []
        }
    
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
        "message": f"Se encontraron {len(prepared_mods)} mods en revisión",
        "data": prepared_mods
    }

@router.get("/my-mods/revision/{mod_id}")
def get_my_mod_in_revision(
    mod_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(get_current_user)
):
    """
    Obtener los detalles de un mod específico del usuario que requiere revisión
    
    Solo muestra si el mod pertenece al usuario autenticado y está en revisión
    """
    crud = CRUD_MOD(db)
    mod = crud.get_user_mod_in_revision_by_id(user.id, mod_id)
    
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado o no está en revisión")
    
    return ResponseBuilder.success(
        data=_prepare_mod_response(mod, db),
        message="Detalles del mod en revisión obtenidos exitosamente",
        db=db
    )

@router.get("/admin/all")
def list_mods_admin(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados."),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todos los mods excluyendo los que requieren revisión (solo para OWNER/EDITOR)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_MOD(db)
    mods = crud.get_mods_admin(skip, limit)
    
    # Preparar respuesta con estructura individual para cada mod
    prepared_mods = []
    for m in mods:
        mod_dict = _prepare_mod_response(m, db)
        
        # Separar info y credits para estructura consistente con GET individual
        from src.utils.response_builder import ResponseBuilder
        response_structure = ResponseBuilder._create_response_with_info(
            mod_dict, 
            "success", 
            "",  # Sin mensaje individual, solo para estructura
            db=db
        )
        # Extraer solo la estructura de data
        prepared_mods.append(response_structure["data"])
    
    return {
        "response": "success",
        "message": "Mods obtenidos exitosamente (incluyendo inactivos)",
        "data": prepared_mods
    }

@router.get("/admin/revision")
def list_mods_pending_revision(
    db: Session = Depends(db_init.get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir desde el inicio (para paginación). Ejemplo: skip=20 omite los primeros 20 resultados."),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros a retornar (default: 20, max: 100). Ejemplo: limit=10 retorna hasta 10 resultados."),
    user: TokenUser = Depends(verify_admin_role)
):
    """
    Listar todos los mods que requieren revisión (solo para OWNER/EDITOR)
    
    Soporta paginación mediante los parámetros `skip` y `limit`:
    - Página 1: skip=0, limit=20 (default)
    - Página 2: skip=20, limit=20
    - Página 3: skip=40, limit=20
    """
    crud = CRUD_MOD(db)
    mods = crud.get_mods_pending_revision(skip, limit)
    
    prepared_mods = []
    for m in mods:
        mod_dict = _prepare_mod_response(m, db)
        
        from src.utils.response_builder import ResponseBuilder
        response_structure = ResponseBuilder._create_response_with_info(
            mod_dict, 
            "success", 
            "",
            db=db
        )
        prepared_mods.append(response_structure["data"])
    
    return {
        "response": "success",
         "message": "Mods pendientes de revisión obtenidos exitosamente",
        "data": prepared_mods
    }

@router.get("/random")
def get_random_mod(db: Session = Depends(db_init.get_db)):
    """
    Obtener un mod aleatorio activo con su slug
    
    Retorna un mod random que no esté eliminado
    """
    crud = CRUD_MOD(db)
    mod = crud.get_random_mod()
    
    if not mod:
        raise HTTPException(status_code=404, detail="No hay mods disponibles")
    
    return ResponseBuilder.success(
        data={
            "slug": mod.slug,
            "id": mod.id,
            "name": mod.name
        },
        message="Mod aleatorio obtenido exitosamente"
    )

@router.get("/search")
def search_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener TODOS los mods activos con solo nombre, id y slug (sin paginación)
    
    Retorna lista completa de todos los mods que no estén eliminados
    """
    crud = CRUD_MOD(db)
    mods = crud.get_all_mods_basic()
    
    if not mods:
        return ResponseBuilder.success(
            data=[],
            message="No hay mods disponibles"
        )
    
    # Convertir tuplas a diccionarios
    mods_list = [
        {
            "id": mod[0],
            "name": mod[1],
            "slug": mod[2]
        }
        for mod in mods
    ]
    
    return ResponseBuilder.success(
        data=mods_list,
        message=f"Se obtuvieron {len(mods_list)} mods exitosamente"
    )

@router.get("/{mod_id}")
def get_mod(mod_id: int, db: Session = Depends(db_init.get_db)):
    """Obtener un mod específico por ID (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mod = crud.get_mod(mod_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    return ResponseBuilder.success(
        data=_prepare_mod_response(mod, db),
        message="Mod obtenido exitosamente",
        db=db
    )

@router.get("/by-slug/{slug}")
def get_mod_by_slug(slug: str, db: Session = Depends(db_init.get_db)):
    """Obtener un mod específico por slug (públicamente disponible)"""
    crud = CRUD_MOD(db)
    mod = crud.get_mod_by_slug(slug)
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    return ResponseBuilder.success(
        data=_prepare_mod_response(mod, db),
        message="Mod obtenido exitosamente",
        db=db
    )

@router.get("/admin/{mod_id}")
def get_mod_admin(
    mod_id: int,
    db: Session = Depends(db_init.get_db),
    user: TokenUser = Depends(verify_admin_role)
):
    """Obtener un mod específico por ID (incluyendo inactivos - solo OWNER/EDITOR)"""
    mod = db.query(Mod).filter(Mod.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    return ResponseBuilder.success(
        data=_prepare_mod_response(mod, db),
        message="Mod obtenido exitosamente",
        db=db
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
        message="Mod creado exitosamente",
        db=db
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
        message="Mod actualizado exitosamente",
        db=db
    )

@router.delete("/{mod_id}")
def delete_mod_route(
    mod_id: int,
    request: ModDeleteRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Eliminar un mod (soft delete, requiere autenticación EDITOR/OWNER)
    
    - reason: Razón de la eliminación (se guarda en comments)
    - Se crea notificación para el uploader
    - Se envía notificación a Discord
    """
    crud = CRUD_MOD(db)
    mod = crud.delete_mod(mod_id, user, request.reason)
    
    # Obtener creator del mod
    from src.models.users import User
    creator = db.query(User).filter(User.id == mod.created_by).first()
    
    if creator:
        # Crear notificación para el uploader
        from src.services.notifications import CRUD_NOTIFICATION
        crud_notif = CRUD_NOTIFICATION(db)
        crud_notif.notify_mod_deleted(
            mod_id=mod_id,
            mod_name=mod.name,
            mod_creator_id=creator.id,
            deleted_by=user.name
        )
    
    # Agregar notificación a Discord como background task
    background_tasks.add_task(DiscordNotifier.notify_mod_deleted, mod, user, creator.name if creator else None)
    
    return ResponseBuilder.deleted(message="Mod eliminado exitosamente")

@router.post("/{mod_id}/approve")
def approve_mod_route(
    mod_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Aprobar un mod que requiere revisión (requiere OWNER)
    
    - Solo aprueba si required_revision es True
    - Establece required_revision a False
    - Marca approved_at y approved_by
    - Crea notificación para el uploader
    - Envía notificación a Discord
    - Crea un banner automático
    """
    if user.rol != UserRolEnum.OWNER:
        raise HTTPException(status_code=403, detail="Solo administradores pueden aprobar mods")
    
    crud = CRUD_MOD(db)
    mod, changes = crud.approve_mod(mod_id, user)
    
    # Crear notificación para el uploader (creador del mod)
    from src.services.notifications import CRUD_NOTIFICATION
    notification_crud = CRUD_NOTIFICATION(db)
    
    # El mod tiene el id del usuario que lo creó en created_by
    from src.models.users import User
    creator = db.query(User).filter(User.id == mod.created_by).first()
    if creator:
        notification_crud.notify_mod_approved(
            mod_id=mod_id,
            mod_name=mod.name,
            mod_creator_id=creator.id,
            approved_by=user.name
        )
    
    # Agregar notificación a Discord como background task
    background_tasks.add_task(DiscordNotifier.notify_mod_approved, mod, user, creator.name if creator else None)
    
    # Crear banner automático cuando se aprueba un mod
    from src.background_tasks import create_banner_for_approved_mod
    background_tasks.add_task(create_banner_for_approved_mod, mod, user)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Mod aprobado exitosamente",
        db=db
    )


@router.post("/{mod_id}/rejected")
def reject_mod_route(
    mod_id: int,
    request: ModRejectRequest,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Rechazar un mod que requiere revisión (requiere OWNER)
    
    - Solo rechaza si required_revision es True
    - Establece required_revision a False
    - Marca rejected_at y rejected_by
    - Guarda los comentarios del rechazo
    - Crea notificación para el uploader
    - Envía notificación a Discord
    """
    if user.rol != UserRolEnum.OWNER:
        raise HTTPException(status_code=403, detail="Solo administradores pueden rechazar mods")
    
    crud = CRUD_MOD(db)
    mod, changes = crud.reject_mod(mod_id, user, request.comments)
    
    # Crear notificación para el uploader (creador del mod)
    from src.services.notifications import CRUD_NOTIFICATION
    notification_crud = CRUD_NOTIFICATION(db)
    
    # Obtener el usuario que creó el mod
    from src.models.users import User
    creator = db.query(User).filter(User.id == mod.created_by).first()
    if creator:
        notification_crud.notify_mod_rejected(
            mod_id=mod_id,
            mod_name=mod.name,
            mod_creator_id=creator.id,
            rejected_by=user.name
        )
    
    # Agregar notificación a Discord como background task
    background_tasks.add_task(DiscordNotifier.notify_mod_rejected, mod, user, creator.name if creator else None)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Mod rechazado exitosamente",
        db=db
    )


@router.put("/status/request/{mod_id}")
def update_mod_request_status(
    mod_id: int,
    request: ModRequestStatusUpdate,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Actualizar el estado de revisión de un mod (aprobar o rechazar)
    
    Endpoint unificado que reemplaza /approve y /rejected
    
    Request body:
    - status: "approve" o "reject"
    - comments: requerido si status es "reject"
    
    Ejemplo:
    - Aprobar: {"status": "approve"}
    - Rechazar: {"status": "reject", "comments": "Razón del rechazo"}
    
    Solo EDITOR/OWNER pueden acceder
    """
    if user.rol == UserRolEnum.UPLOADER:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar estado de mod")
    
    crud = CRUD_MOD(db)
    mod, changes = crud.update_mod_request_status(mod_id, user, request.status, request.comments)
    
    # Crear notificación para el uploader (creador del mod)
    from src.services.notifications import CRUD_NOTIFICATION
    notification_crud = CRUD_NOTIFICATION(db)
    
    # Obtener el usuario que creó el mod
    from src.models.users import User
    creator = db.query(User).filter(User.id == mod.created_by).first()
    
    # Enviar notificación según el estado
    if request.status == "approve":
        if creator:
            notification_crud.notify_mod_approved(
                mod_id=mod_id,
                mod_name=mod.name,
                mod_creator_id=creator.id,
                approved_by=user.name
            )
        # Agregar notificación a Discord como background task
        background_tasks.add_task(DiscordNotifier.notify_mod_approved, mod, user, creator.name if creator else None)
        message = "Mod aprobado exitosamente"
    else:  # reject
        if creator:
            notification_crud.notify_mod_rejected(
                mod_id=mod_id,
                mod_name=mod.name,
                mod_creator_id=creator.id,
                rejected_by=user.name
            )
        # Agregar notificación a Discord como background task
        background_tasks.add_task(DiscordNotifier.notify_mod_rejected, mod, user, creator.name if creator else None)
        message = "Mod rechazado exitosamente"
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message=message,
        db=db
    )


@router.post("/{mod_id}/restore")
def restore_mod_route(
    mod_id: int,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Restaurar un mod eliminado (requiere OWNER)
    
    - Cambio is_active a True
    - Limpia deleted_by y deleted_at
    - Crea notificación para el uploader
    - Envía notificación a Discord
    """
    if user.rol != UserRolEnum.OWNER:
        raise HTTPException(status_code=403, detail="Solo administradores pueden restaurar mods")
    
    crud = CRUD_MOD(db)
    mod = crud.restore_mod(mod_id, user)
    
    # Obtener creator del mod
    from src.models.users import User
    creator = db.query(User).filter(User.id == mod.created_by).first()
    
    if creator:
        # Crear notificación para el uploader
        from src.services.notifications import CRUD_NOTIFICATION
        crud_notif = CRUD_NOTIFICATION(db)
        crud_notif.notify_mod_restored(
            mod_id=mod_id,
            mod_name=mod.name,
            mod_creator_id=creator.id,
            restored_by=user.name
        )
    
    # Agregar notificación a Discord como background task
    background_tasks.add_task(DiscordNotifier.notify_mod_restored, mod, user, creator.name if creator else None)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Mod restaurado exitosamente",
        db=db
    )


@router.post("/{mod_id}/genres")
def add_genres_to_mod(
    mod_id: int,
    data: ModGenreAdd,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Agrega géneros a un mod
    
    Parámetros:
    - genre_ids: array de IDs de géneros a agregar
    
    Requiere autenticación:
    - OWNER/EDITOR: pueden agregar géneros a cualquier mod
    - UPLOADER: solo puede agregar géneros si es el creador del mod
    """
    # Verificar que el mod existe y obtener su creador
    mod = db.query(Mod).filter(Mod.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    
    # Verificar permisos
    if user.rol == UserRolEnum.UPLOADER and mod.created_by != user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar géneros a este mod")
    
    crud = CRUD_MOD(db)
    mod, genres_added = crud.add_genres_to_mod(mod_id, data.genre_ids)
    
    # Solo enviar notificación si se agregaron géneros
    if genres_added:
        background_tasks.add_task(notify_genres_added, mod, genres_added, user)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Géneros agregados al mod exitosamente",
        db=db
    )


@router.delete("/{mod_id}/genres")
def remove_genres_from_mod(
    mod_id: int,
    data: ModGenreAdd,
    user: TokenUser = Depends(get_current_user),
    db: Session = Depends(db_init.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Remueve géneros de un mod
    
    Parámetros:
    - genre_ids: array de IDs de géneros a remover
    
    Requiere autenticación:
    - OWNER/EDITOR: pueden remover géneros de cualquier mod
    - UPLOADER: solo puede remover géneros si es el creador del mod
    """
    # Verificar que el mod existe y obtener su creador
    mod = db.query(Mod).filter(Mod.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod no encontrado")
    
    # Verificar permisos
    if user.rol == UserRolEnum.UPLOADER and mod.created_by != user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para remover géneros de este mod")
    
    crud = CRUD_MOD(db)
    mod, genres_removed = crud.remove_genres_from_mod(mod_id, data.genre_ids)
    
    # Solo enviar notificación si se removieron géneros
    if genres_removed:
        background_tasks.add_task(notify_genres_removed, mod, genres_removed, user)
    
    return ResponseBuilder.updated(
        data=_prepare_mod_response(mod, db),
        message="Géneros removidos del mod exitosamente",
        db=db
    )


@router.get("/{mod_id}/genres")
def get_mod_genres(
    mod_id: int,
    db: Session = Depends(db_init.get_db)
):
    """
    Obtiene los géneros de un mod (públicamente disponible)
    """
    from src.schemas.generos import GenreResponse
    
    crud = CRUD_MOD(db)
    genres = crud.get_mod_genres(mod_id)
    
    # Preparar respuesta de géneros
    genre_list = [GenreResponse.model_validate(g).model_dump() for g in genres]
    
    return ResponseBuilder.success(
        data=genre_list,
        message="Géneros del mod obtenidos exitosamente"
    )


@router.get("/stats/total-active")
def get_total_active_mods(db: Session = Depends(db_init.get_db)):
    """
    Obtener el total de mods activos (públicamente disponible)
    
    Retorna:
    - total: número total de mods activos
    """
    try:
        from src.models.enums import StatusEnum
        
        total = db.query(Mod).filter(
            Mod.status != StatusEnum.ARCHIVED,
            Mod.deleted_at.is_(None)
        ).count()
        
        return ResponseBuilder.success(
            data={"total": total},
            message="Total de mods activos obtenido correctamente"
        )
    except Exception as e:
        return ResponseBuilder.error(str(e), 500)
