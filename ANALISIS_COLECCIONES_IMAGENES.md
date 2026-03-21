# Análisis Completo: Colecciones e Imágenes en la API DDSC

## 1. RUTAS POST/PUT/PATCH/DELETE PARA COLECCIONES

### Archivo: `/src/routes/collections.py`

#### POST - Crear colección
- **Ruta**: `POST /collections`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Body esperado**: 
  ```json
  {
    "name": "string (requerido, único)",
    "description": "string (opcional)"
  }
  ```
- **Respuesta exitosa**: 201 Created
  ```json
  {
    "response": "created",
    "message": "Colección creada exitosamente",
    "data": {
      "resource": {
        "id": 1,
        "name": "Mi Colección",
        "description": "Descripción"
      },
      "info": {
        "created_at": "2026-03-20T...",
        "created_by": "username",
        "updated_at": "2026-03-20T...",
        "updated_by": "username",
        "is_active": true
      }
    }
  }
  ```

#### PUT - Actualizar colección
- **Ruta**: `PUT /collections/{collection_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Body esperado**:
  ```json
  {
    "name": "string (opcional)",
    "description": "string (opcional)"
  }
  ```
- **Validación**: El nombre actualizado no debe existir en otra colección
- **Respuesta exitosa**: 200 OK (misma estructura que POST)

#### DELETE - Eliminar colección (soft delete)
- **Ruta**: `DELETE /collections/{collection_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Nota**: Soft delete → Marca `is_active = False`
- **Respuesta exitosa**: 200 OK
  ```json
  {
    "response": "deleted",
    "message": "Colección eliminada exitosamente",
    "data": null
  }
  ```

#### POST - Reactivar colección
- **Ruta**: `POST /collections/{collection_id}/reactivate`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Nota**: Marca `is_active = True`
- **Respuesta exitosa**: 200 OK (misma estructura que PUT)

#### GET - Listar colecciones (públicas)
- **Ruta**: `GET /collections?skip=0&limit=20`
- **Autenticación**: NO requerida
- **Filtro**: Solo colecciones activas (`is_active = True`)

#### GET - Listar colecciones (admin)
- **Ruta**: `GET /collections/admin/all?skip=0&limit=20`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Filtro**: Incluye colecciones inactivas

#### GET - Obtener colección específica (pública)
- **Ruta**: `GET /collections/{collection_id}`
- **Autenticación**: NO requerida
- **Filtro**: Solo si está activa

#### GET - Obtener colección específica (admin)
- **Ruta**: `GET /collections/admin/{collection_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Filtro**: Incluye inactivas

---

## 2. RUTAS POST/PUT/PATCH/DELETE PARA MODS-COLECCIONES (relación)

### Archivo: `/src/routes/mods_collections.py`

#### POST - Agregar mod a colección
- **Ruta**: `POST /mods-collections`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Body esperado**:
  ```json
  {
    "mod_id": integer (requerido),
    "collection_id": integer (requerido)
  }
  ```
- **Validaciones**:
  - Verifica que mod existe
  - Verifica que colección existe
  - No permite duplicados (mod + collection activos)
  - Si existe inactiva, la reactiva
- **Respuesta exitosa**: 201 Created
  ```json
  {
    "response": "created",
    "message": "Mod agregado a colección exitosamente",
    "data": {
      "resource": {
        "id": 1,
        "mod_id": 5,
        "collection_id": 2
      },
      "info": {
        "created_at": "2026-03-20T...",
        "created_by": "username",
        "updated_at": "2026-03-20T...",
        "updated_by": "username",
        "is_active": true
      }
    }
  }
  ```

#### DELETE - Remover mod de colección (soft delete)
- **Ruta**: `DELETE /mods-collections/{mods_collection_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Nota**: Marca `is_active = False`
- **Respuesta exitosa**: 200 OK
  ```json
  {
    "response": "deleted",
    "message": "Mod removido de colección exitosamente",
    "data": null
  }
  ```

#### POST - Reactivar mod en colección
- **Ruta**: `POST /mods-collections/{mods_collection_id}/reactivate`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Nota**: Marca `is_active = True`
- **Respuesta exitosa**: 200 OK (misma estructura que POST crear)

#### GET - Listar relaciones (públicas)
- **Ruta**: `GET /mods-collections?skip=0&limit=20`
- **Autenticación**: NO requerida
- **Filtro**: Solo activas

#### GET - Listar relaciones (admin)
- **Ruta**: `GET /mods-collections/admin/all?skip=0&limit=20`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Filtro**: Incluye inactivas

#### GET - Obtener colecciones de un mod
- **Ruta**: `GET /mods-collections/mod/{mod_id}`
- **Autenticación**: NO requerida
- **Filtro**: Solo activas

#### GET - Obtener mods de una colección
- **Ruta**: `GET /mods-collections/collection/{collection_id}`
- **Autenticación**: NO requerida
- **Filtro**: Solo activos

---

## 3. RUTAS POST/PUT/DELETE PARA IMÁGENES

### Archivo: `/src/routes/imagenes.py`

#### POST - Subir LOGO (máximo 1 por mod)
- **Ruta**: `POST /images/logo/{mod_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Content-Type**: multipart/form-data
- **Archivo esperado**: file (image)
- **Validaciones**:
  - Solo 1 logo por mod (error 409 si existe)
  - Valida que sea imagen válida
  - Procesa a WebP
- **Sube a**: S3
- **Respuesta exitosa**: 201 Created
  ```json
  {
    "response": "created",
    "message": "Logo subido exitosamente",
    "data": {
      "resource": {
        "id": 1,
        "url": "https://s3.../mod_1/logo/...",
        "type": "logo",
        "mod_id": 1
      },
      "info": {
        "created_at": "2026-03-20T...",
        "created_by": "username",
        "updated_at": "2026-03-20T...",
        "updated_by": "username",
        "is_active": true
      }
    }
  }
  ```

#### POST - Subir imagen MAIN (máximo 1 por mod)
- **Ruta**: `POST /images/main/{mod_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Validaciones**:
  - Solo 1 main image por mod (error 409 si existe)
  - Valida que sea imagen válida
  - Procesa a WebP
- **Sube a**: S3
- **Respuesta exitosa**: 201 Created (estructura similar a logo)

#### POST - Subir SCREENSHOT (máximo 4 por mod)
- **Ruta**: `POST /images/screenshots/{mod_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Validaciones**:
  - Máximo 4 screenshots por mod (error 409 si >= 4)
  - Valida que sea imagen válida
  - Procesa a WebP
- **Sube a**: S3
- **Respuesta exitosa**: 201 Created (estructura similar)

#### PUT - Actualizar LOGO (reemplazar)
- **Ruta**: `PUT /images/logo/{mod_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Content-Type**: multipart/form-data
- **Archivo esperado**: file (image)
- **Proceso**:
  1. Obtiene logo actual
  2. Si no existe → 404
  3. Elimina anterior de S3
  4. Procesa nuevo a WebP
  5. Sube a S3
  6. Actualiza BD (solo URL)
- **Respuesta exitosa**: 200 OK
  ```json
  {
    "response": "updated",
    "message": "Logo actualizado exitosamente",
    "data": {...}
  }
  ```

#### PUT - Actualizar imagen MAIN (reemplazar)
- **Ruta**: `PUT /images/main/{mod_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Proceso**: Igual a logo (obtiene, elimina, sube, actualiza)
- **Respuesta exitosa**: 200 OK

#### PUT - Actualizar SCREENSHOT específico (reemplazar)
- **Ruta**: `PUT /images/screenshots/{image_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Parámetro**: image_id (no mod_id)
- **Validaciones**:
  - Verifica que image_id es tipo SCREENSHOT
  - Verifica que está activa
- **Proceso**: Igual a logo
- **Respuesta exitosa**: 200 OK

#### DELETE - Eliminar imagen (soft delete)
- **Ruta**: `DELETE /images/{image_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Validación de rol**: Rechaza UPLOADER (403)
- **Nota**: 
  - Marca `is_active = False` en BD
  - NO elimina el archivo de S3
- **Respuesta exitosa**: 200 OK
  ```json
  {
    "response": "deleted",
    "message": "Imagen eliminada exitosamente",
    "data": null
  }
  ```

#### GET - Obtener imágenes de un mod
- **Ruta**: `GET /images/mod/{mod_id}`
- **Autenticación**: NO requerida
- **Filtro**: Solo activas (`is_active = True`)
- **Respuesta**: Array de imágenes

#### GET - Listar imágenes (admin)
- **Ruta**: `GET /images/admin/all?skip=0&limit=20`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Filtro**: Incluye inactivas

#### GET - Obtener imagen específica (pública)
- **Ruta**: `GET /images/{image_id}`
- **Autenticación**: NO requerida
- **Filtro**: Solo si está activa

#### GET - Obtener imagen específica (admin)
- **Ruta**: `GET /images/admin/{image_id}`
- **Autenticación**: Requerida (solo OWNER/EDITOR)
- **Filtro**: Incluye inactivas

---

## 4. DEFINICIÓN DE MODELOS

### Modelo Collection
**Archivo**: `/src/models/collection.py`
```python
class Collection(Base, TimestampMixin):
    __tablename__ = "collections"
    
    id: Integer (PK)
    name: String(255) - NOT NULL, UNIQUE, INDEXED
    description: String(500) - NULLABLE
    
    # Heredado de TimestampMixin:
    created_at: DateTime
    created_by: String(100)
    updated_at: DateTime
    updated_by: String(100)
    is_active: Boolean (default=True)
    
    # Relaciones:
    mods_collections: List[ModsCollection] (backref)
```

### Modelo ModsCollection (relación de junction)
**Archivo**: `/src/models/mods_collection.py`
```python
class ModsCollection(Base, TimestampMixin):
    __tablename__ = "mods_collections"
    
    id: Integer (PK)
    mod_id: Integer (FK -> mods.id) - NOT NULL, INDEXED
    collection_id: Integer (FK -> collections.id) - NOT NULL, INDEXED
    
    # Heredado de TimestampMixin:
    created_at: DateTime
    created_by: String(100)
    updated_at: DateTime
    updated_by: String(100)
    is_active: Boolean (default=True)
    
    # Relaciones:
    mod: Mod
    collection: Collection
```

### Modelo Image
**Archivo**: `/src/models/imagen.py`
```python
class Image(Base, TimestampMixin):
    __tablename__ = "imagenes"
    
    id: Integer (PK)
    url: String(500) - NOT NULL
    type: Enum(ImageTypeEnum) - NOT NULL
      - "logo" (máximo 1 por mod)
      - "main" (máximo 1 por mod)
      - "screenshot" (máximo 4 por mod)
    mod_id: Integer (FK -> mods.id) - NULLABLE
    
    # Heredado de TimestampMixin:
    created_at: DateTime
    created_by: String(100)
    updated_at: DateTime
    updated_by: String(100)
    is_active: Boolean (default=True)
    
    # Relaciones:
    mod: Mod (back_populates="imagenes")
```

### Enum ImageTypeEnum
**Archivo**: `/src/models/enums.py`
```python
class ImageTypeEnum(str, Enum):
    LOGO = "logo"
    MAIN = "main"
    SCREENSHOT = "screenshot"
```

---

## 5. SCHEMAS (Pydantic)

### CollectionCreate
```python
{
    "name": str,  # Requerido
    "description": str | None = None
}
```

### CollectionUpdate
```python
{
    "name": str | None = None,
    "description": str | None = None
}
```

### CollectionResponse
```python
{
    "id": int,
    "name": str,
    "description": str | None,
    # Timestamps (heredados de TimestampBase):
    "created_at": datetime,
    "created_by": str,
    "updated_at": datetime,
    "updated_by": str,
    "is_active": bool
}
```

### ModsCollectionCreate
```python
{
    "mod_id": int,  # Requerido
    "collection_id": int  # Requerido
}
```

### ModsCollectionResponse
```python
{
    "id": int,
    "mod_id": int,
    "collection_id": int,
    # Timestamps:
    "created_at": datetime,
    "created_by": str,
    "updated_at": datetime,
    "updated_by": str,
    "is_active": bool
}
```

### ImageCreate
```python
{
    "mod_id": int,  # Requerido
    "url": str,  # Requerido (max 500)
    "type": ImageTypeEnum  # Requerido (logo, main, screenshot)
}
```

### ImageResponse
```python
{
    "id": int,
    "url": str,
    "type": ImageTypeEnum,
    "mod_id": int,
    # Timestamps:
    "created_at": datetime,
    "created_by": str,
    "updated_at": datetime,
    "updated_by": str,
    "is_active": bool
}
```

---

## 6. CÓMO SE RETORNAN CAMBIOS EN ESTOS SERVICIOS

### Estructura de respuestas (ResponseBuilder)
**Archivo**: `/src/utils/response_builder.py`

Los servicios retornan respuestas estandarizadas usando `ResponseBuilder`:

#### Para recursos con timestamps (Collections, ModsCollections, Images)
**Formato**: Separado en `resource` e `info`
```json
{
    "response": "created|updated|success",
    "message": "Descripción de la acción",
    "data": {
        "resource": {
            "id": 1,
            "name": "Mi Colección",
            "description": "..."
        },
        "info": {
            "created_at": "2026-03-20T...",
            "created_by": "username",
            "updated_at": "2026-03-20T...",
            "updated_by": "username",
            "is_active": true
        }
    }
}
```

#### Para listas
```json
{
    "response": "success",
    "message": "Datos obtenidos exitosamente",
    "data": [
        { item1 },
        { item2 }
    ]
}
```

#### Para eliminaciones
```json
{
    "response": "deleted",
    "message": "Recurso eliminado exitosamente",
    "data": null
}
```

### Métodos del servicio CRUD_COLLECTION
- `get_collection(id)` - Obtiene colección activa
- `get_collection_admin(id)` - Obtiene incluyendo inactivas
- `get_collections(skip, limit)` - Lista colecciones activas (paginado)
- `get_collections_admin(skip, limit)` - Lista incluyendo inactivas
- `create_collection(name, description)` - Crea y retorna
- `update_collection(id, name, description)` - Actualiza y retorna
- `delete_collection(id)` - Soft delete y retorna
- `reactivate_collection(id)` - Reactiva y retorna

### Métodos del servicio CRUD_MODS_COLLECTION
- `get_mods_collection(id)` - Obtiene relación activa
- `get_mods_collection_admin(id)` - Obtiene incluyendo inactivas
- `get_mods_collections(skip, limit)` - Lista activas
- `get_mods_collections_admin(skip, limit)` - Lista incluyendo inactivas
- `get_mod_collections(mod_id)` - Obtiene colecciones de un mod
- `get_collection_mods(collection_id)` - Obtiene mods de una colección
- `add_mod_to_collection(mod_id, collection_id)` - Crea/reactiva relación
- `remove_mod_from_collection(id)` - Soft delete de relación
- `reactivate_mod_collection(id)` - Reactiva relación

### Métodos del servicio CRUD_IMAGE
- `create_imagen(data)` - Crea imagen con validaciones
- `get_imagenes_mod(mod_id)` - Obtiene imágenes activas de un mod
- `get_imagenes_admin(skip, limit)` - Lista incluyendo inactivas
- `get_imagen(id)` - Obtiene imagen activa
- `get_imagen_by_mod_and_type(mod_id, type)` - Obtiene logo/main
- `count_imagenes_by_mod_and_type(mod_id, type)` - Cuenta screenshots
- `update_imagen(id, data)` - Actualiza campos
- `delete_imagen(id)` - Soft delete

---

## 7. NOTIFICACIONES EXISTENTES

### NotificationTypeEnum actual (SOLO para MODS)
**Archivo**: `/src/models/enums.py`
```python
class NotificationTypeEnum(str, Enum):
    MOD_PENDING_REVIEW = "mod_pending_review"  # EDITORS/OWNERS cuando UPLOADER crea mod
    MOD_APPROVED = "mod_approved"              # UPLOADER cuando aprobado
    MOD_REJECTED = "mod_rejected"              # UPLOADER cuando rechazado
    MOD_DELETED = "mod_deleted"                # (Disponible pero no usado)
    MOD_RESTORED = "mod_restored"              # (Disponible pero no usado)
```

### Métodos de notificación para MODS
**Archivo**: `/src/services/notifications.py`

```python
# Notificación cuando se crea un mod
notify_mod_pending_review(mod_id, mod_name, uploader_name)
  -> Crea notificación para TODOS los EDITORS/OWNERS

# Notificación cuando se aprueba
notify_mod_approved(mod_id, mod_name, mod_creator_id, approved_by)
  -> Crea notificación para el UPLOADER

# Notificación cuando se rechaza
notify_mod_rejected(mod_id, mod_name, mod_creator_id, rejected_by)
  -> Crea notificación para el UPLOADER
```

### Estructura de Notification
**Archivo**: `/src/models/notifications.py`
```python
class Notification(Base, TimestampMixin):
    id: Integer (PK)
    id_user: Integer (FK -> users.id) - Usuario receptor
    id_mod: Integer (FK -> mods.id) - Mod relacionado
    type: Enum(NotificationTypeEnum)
    status: Enum(NotificationStatusEnum) - UNREAD | READ
    title: String(200)
    message: Text
    action_by: String(100) - Quién realizó la acción
    mod_name: String(200) - Copia del nombre (preserva si se elimina mod)
    read_at: DateTime - Timestamp de lectura
    is_active: Boolean
    
    # Timestamps:
    created_at, created_by, updated_at, updated_by
```

### NOTA IMPORTANTE
**Actualmente NO hay notificaciones para:**
- Creación de colecciones
- Actualización de colecciones
- Eliminación de colecciones
- Agregación de mods a colecciones
- Remoción de mods de colecciones
- Subida de imágenes
- Actualización de imágenes
- Eliminación de imágenes

**Esto debe ser implementado según requerimientos.**

---

## 8. RESUMEN DE PUNTOS CLAVE

### Soft Deletes
- Todas las operaciones DELETE son soft deletes
- Marcan `is_active = False`
- Los datos se mantienen en BD
- Tienen métodos `/reactivate` para recuperar

### Validaciones por rol
- OWNER/EDITOR: Acceso completo a POST/PUT/DELETE
- UPLOADER: Solo puede leer, NO puede crear/editar/eliminar
- Anónimo: Acceso a GET (públicas)

### Límites de imágenes por mod
- Logo: máximo 1
- Main image: máximo 1
- Screenshots: máximo 4

### Procesamiento de imágenes
- Convierte a WebP
- Sube a S3
- Almacena URL en BD

### Timestamps automáticos
- `created_at`: Auto-generado al crear
- `created_by`: Quién creó (del contexto de usuario)
- `updated_at`: Auto-actualizado cada cambio
- `updated_by`: Quién hizo el último cambio
- `is_active`: Por defecto True

### Registro de cambios
- El middleware context captura usuario actual
- TimestampMixin registra quién hizo cada cambio
- Útil para auditoría y rastrabilidad
