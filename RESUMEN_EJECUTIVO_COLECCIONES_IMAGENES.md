# Resumen Ejecutivo: Colecciones e Imágenes

## TABLA RÁPIDA DE REFERENCIA

### ENDPOINTS DE COLECCIONES
```
GET    /collections                     - Listar (públicas, activas)
GET    /collections/{id}                - Obtener (pública)
GET    /collections/admin/all           - Listar admin (todas)
GET    /collections/admin/{id}          - Obtener admin

POST   /collections                     - Crear (solo OWNER/EDITOR)
PUT    /collections/{id}                - Actualizar (solo OWNER/EDITOR)
DELETE /collections/{id}                - Soft delete (solo OWNER/EDITOR)
POST   /collections/{id}/reactivate     - Reactivar (solo OWNER/EDITOR)
```

### ENDPOINTS DE MODS-COLECCIONES
```
GET    /mods-collections                - Listar (públicas, activas)
GET    /mods-collections/{id}           - Obtener (pública)
GET    /mods-collections/admin/all      - Listar admin (todas)
GET    /mods-collections/mod/{mod_id}   - Colecciones de un mod
GET    /mods-collections/collection/{col_id} - Mods de una colección

POST   /mods-collections                - Agregar mod (solo OWNER/EDITOR)
DELETE /mods-collections/{id}           - Remover mod (soft delete)
POST   /mods-collections/{id}/reactivate - Reactivar
```

### ENDPOINTS DE IMÁGENES
```
GET    /images/mod/{mod_id}             - Imágenes activas de un mod
GET    /images/{id}                     - Obtener imagen (pública)
GET    /images/admin/all                - Listar admin (todas)
GET    /images/admin/{id}               - Obtener admin

POST   /images/logo/{mod_id}            - Subir logo (FormData, max 1)
POST   /images/main/{mod_id}            - Subir main (FormData, max 1)
POST   /images/screenshots/{mod_id}     - Subir screenshot (FormData, max 4)

PUT    /images/logo/{mod_id}            - Reemplazar logo
PUT    /images/main/{mod_id}            - Reemplazar main
PUT    /images/screenshots/{image_id}   - Reemplazar screenshot

DELETE /images/{id}                     - Soft delete (solo OWNER/EDITOR)
```

---

## ESQUEMA DE BASE DE DATOS

```
┌─────────────────────────────┐
│      Collections            │
├─────────────────────────────┤
│ id (PK)                     │
│ name (VARCHAR 255, UNIQUE)  │
│ description (VARCHAR 500)   │
│ created_at, updated_at      │
│ created_by, updated_by      │
│ is_active (BOOL)            │
└────────────┬────────────────┘
             │ 1-to-N
             │
         ┌───┴───────────────────┐
         │                       │
┌────────▼─────────────────┐  ┌──┴──────────────────────────┐
│  Mods_Collections (JT)   │  │  Imagenes                  │
├──────────────────────────┤  ├────────────────────────────┤
│ id (PK)                  │  │ id (PK)                    │
│ mod_id (FK -> mods.id)   │  │ url (VARCHAR 500)          │
│ collection_id (FK)       │  │ type (ENUM: logo/main...)  │
│ is_active                │  │ mod_id (FK -> mods.id)     │
│ created_at, updated_at   │  │ created_at, updated_at     │
│ created_by, updated_by   │  │ created_by, updated_by     │
└──────────────────────────┘  │ is_active                  │
         │                     └────────────────────────────┘
         │ N-to-1
         │
    ┌────▼─────────────┐
    │      Mods        │
    └──────────────────┘
```

---

## FLUJOS DE OPERACIÓN

### Crear Colección
```
Cliente (OWNER/EDITOR autenticado)
    ↓
POST /collections {"name": "Mi Colección", ...}
    ↓
[Validación] Solo OWNER/EDITOR
[Validación] Nombre único
    ↓
CRUD_COLLECTION.create_collection()
    ↓
INSERT Collection
    ↓
ResponseBuilder.created(Collection)
    ↓
201 Created con estructura {resource, info}
```

### Agregar Mod a Colección
```
Cliente (OWNER/EDITOR autenticado)
    ↓
POST /mods-collections {"mod_id": 5, "collection_id": 2}
    ↓
[Validación] Mod existe
[Validación] Colección existe
[Validación] No existe relación activa (error 400 si existe)
    ↓
¿Existe relación INACTIVA?
    ├─ SÍ → UPDATE is_active = True (reactiva)
    └─ NO → INSERT nueva relación
    ↓
ResponseBuilder.created(ModsCollection)
    ↓
201 Created
```

### Subir Logo
```
Cliente (OWNER/EDITOR autenticado) + Archivo
    ↓
POST /images/logo/{mod_id} (FormData con file)
    ↓
[Validación] Rol OWNER/EDITOR
[Validación] Mod existe
[Validación] No existe logo (error 409 si existe)
    ↓
ImageProcessor.validate_image(file_content)
    ↓
ImageProcessor.process_to_webp(file_content)
    ↓
S3Manager.upload_file(webp_content) → URL
    ↓
INSERT Image {url, type: "logo", mod_id}
    ↓
ResponseBuilder.created(Image)
    ↓
201 Created
```

### Actualizar Logo (reemplazar)
```
Cliente (OWNER/EDITOR autenticado) + Archivo
    ↓
PUT /images/logo/{mod_id} (FormData con file)
    ↓
[Validación] Rol OWNER/EDITOR
    ↓
OBTENER logo actual
    ├─ Existe → Continuar
    └─ NO existe → 404 Error
    ↓
ImageProcessor.validate_image(file_content)
    ↓
ImageProcessor.process_to_webp(file_content)
    ↓
S3Manager.delete_file(old_url)
    ↓
S3Manager.upload_file(webp_content) → NEW_URL
    ↓
UPDATE Image SET url = NEW_URL
    ↓
ResponseBuilder.updated(Image)
    ↓
200 OK
```

### Eliminar Colección (Soft Delete)
```
Cliente (OWNER/EDITOR autenticado)
    ↓
DELETE /collections/{id}
    ↓
[Validación] Rol OWNER/EDITOR
    ↓
UPDATE Collection SET is_active = False
    ↓
ResponseBuilder.deleted()
    ↓
200 OK (data: null)
```

### Reactivar Colección
```
Cliente (OWNER/EDITOR autenticado)
    ↓
POST /collections/{id}/reactivate
    ↓
[Validación] Rol OWNER/EDITOR
    ↓
UPDATE Collection SET is_active = True
    ↓
ResponseBuilder.updated(Collection)
    ↓
200 OK
```

---

## VALIDACIONES Y LIMITES

### Validaciones de Rol
| Operación | OWNER | EDITOR | UPLOADER | Anónimo |
|-----------|-------|--------|----------|---------|
| GET (activos) | ✓ | ✓ | ✓ | ✓ |
| GET admin (todos) | ✓ | ✓ | ✗ | ✗ |
| POST crear | ✓ | ✓ | ✗ | ✗ |
| PUT actualizar | ✓ | ✓ | ✗ | ✗ |
| DELETE soft | ✓ | ✓ | ✗ | ✗ |
| POST reactivate | ✓ | ✓ | ✗ | ✗ |

### Limites de Imágenes por Mod
- **Logo**: 1 máximo (error 409 si intenta crear segundo)
- **Main**: 1 máximo (error 409 si intenta crear segundo)
- **Screenshot**: 4 máximo (error 409 si intenta crear quinto)

### Validaciones de Datos
- **Collection.name**: Único en BD (error 400 si ya existe)
- **Collection.name**: Max 255 caracteres
- **Collection.description**: Max 500 caracteres
- **Image.url**: Max 500 caracteres
- **Image.type**: Debe ser "logo", "main" o "screenshot"

### Validaciones de Imagen
- Formato: Validación de imagen válida
- Procesamiento: Conversión obligatoria a WebP
- Almacenamiento: S3
- Referencia: URL guardada en BD

---

## RESPUESTAS Y CÓDIGOS HTTP

### Éxito
- **201 Created**: POST create* (colecciones, relaciones, imágenes)
- **200 OK**: GET, PUT, POST reactivate, DELETE
- **204 No Content**: (No usado en esta API)

### Errores
- **400 Bad Request**:
  - Nombre de colección duplicado
  - Mod ya existe en colección
  - Campos faltantes o inválidos
  - Tipo de imagen inválido
  
- **403 Forbidden**:
  - Rol UPLOADER intentando operación POST/PUT/DELETE
  
- **404 Not Found**:
  - Colección no existe
  - Mod no existe
  - Imagen no existe
  - Logo/main no existe (para actualizar)
  
- **409 Conflict**:
  - Logo ya existe para este mod
  - Main image ya existe para este mod
  - Ya tiene 4 screenshots

### Estructura de Error
```json
{
  "response": "error",
  "message": "Descripción del error",
  "data": null
}
```

---

## TIMESTAMPS AUTOMÁTICOS

Todos los registros tienen:
```
created_at: DateTime (auto-asignado al crear)
created_by: String (usuario que creó, del contexto)
updated_at: DateTime (auto-actualizado cada cambio)
updated_by: String (usuario del último cambio)
is_active: Boolean (default=True)
```

Ejemplo de respuesta con timestamps:
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
      "created_at": "2026-03-20T15:30:45.123456Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:30:45.123456Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  }
}
```

---

## NOTIFICACIONES

### Actual (Solo para MODS)
- `MOD_PENDING_REVIEW`: EDITORS/OWNERS cuando UPLOADER crea
- `MOD_APPROVED`: UPLOADER cuando aprobado
- `MOD_REJECTED`: UPLOADER cuando rechazado
- `MOD_DELETED`: Disponible pero no usado
- `MOD_RESTORED`: Disponible pero no usado

### FALTA implementar para COLECCIONES e IMÁGENES
- Notificaciones de creación
- Notificaciones de actualización
- Notificaciones de eliminación
- Notificaciones de agregación/remoción de mods

---

## ARCHIVOS CLAVE

### Rutas (API)
- `/src/routes/collections.py` - Endpoints colecciones
- `/src/routes/mods_collections.py` - Endpoints relaciones
- `/src/routes/imagenes.py` - Endpoints imágenes

### Servicios (CRUD)
- `/src/services/collections.py` - Lógica colecciones
- `/src/services/mods_collections.py` - Lógica relaciones
- `/src/services/imagenes.py` - Lógica imágenes

### Modelos (BD)
- `/src/models/collection.py` - Modelo colecciones
- `/src/models/mods_collection.py` - Modelo relaciones
- `/src/models/imagen.py` - Modelo imágenes

### Schemas (Validación)
- `/src/schemas/collections.py` - Schemas colecciones
- `/src/schemas/mods_collections.py` - Schemas relaciones
- `/src/schemas/imagenes.py` - Schemas imágenes

### Utilidades
- `/src/utils/response_builder.py` - Constructor respuestas (timestamps en "info")
- `/src/utils/image_processor.py` - Procesamiento WebP
- `/src/utils/s3_manager.py` - Gestión S3

---

## PRÓXIMOS PASOS SUGERIDOS

1. **Implementar notificaciones** para colecciones e imágenes
2. **Agregar PATCH** si se necesita actualización parcial
3. **Crear índices** en campos frequently queried
4. **Documentar permisos** por granularidad (si es necesario)
5. **Agregar pruebas** unitarias e integración
6. **Considerar soft restore** para datos eliminados

