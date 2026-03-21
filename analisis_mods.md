# ANÁLISIS COMPLETO: Rutas POST/PUT/PATCH/DELETE en src/routes/mods.py

## 1. TODAS LAS RUTAS POST/PUT/PATCH/DELETE

### RUTAS POST (Creación/Acciones):

1. **POST /api/mods** (línea 137-165)
   - Ruta: `create_mod_route()`
   - Autenticación: Requiere usuario autenticado
   - Descripción: Crear un nuevo mod
   - Cambios capturados: Automático al crear (created_by, created_at)
   - Notificaciones: 
     - Si UPLOADER: Crea notificación para EDITORS/OWNERS
     - Siempre: Envía a Discord (BackgroundTask)

2. **POST /api/mods/{mod_id}/approve** (línea 225-269)
   - Ruta: `approve_mod_route()`
   - Autenticación: Solo EDITOR/OWNER
   - Descripción: Aprobar un mod que requiere revisión
   - Cambios capturados: required_revision (True→False), approved_at, approved_by
   - Notificaciones:
     - Crea notificación para el creador del mod (UPLOADER)
     - Envía a Discord (BackgroundTask)

3. **POST /api/mods/{mod_id}/rejected** (línea 272-317)
   - Ruta: `reject_mod_route()`
   - Autenticación: Solo EDITOR/OWNER
   - Descripción: Rechazar un mod que requiere revisión
   - Cambios capturados: required_revision (True→False), rejected_at, rejected_by, comments
   - Notificaciones:
     - Crea notificación para el creador del mod
     - Envía a Discord (BackgroundTask)

4. **POST /api/mods/{mod_id}/restore** (línea 320-362)
   - Ruta: `restore_mod_route()`
   - Autenticación: Solo EDITOR/OWNER
   - Descripción: Restaurar un mod eliminado (revertir soft delete)
   - Cambios capturados: is_active (False→True), limpia deleted_by y deleted_at
   - Notificaciones:
     - Crea notificación para el creador del mod
     - Envía a Discord (BackgroundTask)

5. **POST /api/mods/{mod_id}/genres** (línea 365-386)
   - Ruta: `add_genres_to_mod()`
   - Autenticación: Cualquier usuario autenticado
   - Descripción: Agregar géneros a un mod
   - Cambios capturados: Modificación en relación ModGenre
   - Notificaciones: NINGUNA

### RUTAS PUT (Actualización completa):

1. **PUT /api/mods/{mod_id}** (línea 167-185)
   - Ruta: `update_mod_route()`
   - Autenticación: Solo EDITOR/OWNER (no UPLOADER)
   - Descripción: Actualizar los datos de un mod existente
   - Cambios capturados: Compara valores anteriores vs nuevos, retorna dict con cambios
   - Notificaciones:
     - Envía a Discord (BackgroundTask) con detalles de cambios
     - Detecta si hubo aprobación (required_revision: True→False)

### RUTAS DELETE (Eliminación lógica):

1. **DELETE /api/mods/{mod_id}** (línea 187-223)
   - Ruta: `delete_mod_route()`
   - Autenticación: Solo EDITOR/OWNER
   - Descripción: Soft delete de un mod
   - Request body: ModDeleteRequest (contiene reason)
   - Cambios capturados: is_active (True→False), deleted_by, comments (reason)
   - Notificaciones:
     - Crea notificación para el creador del mod
     - Envía a Discord (BackgroundTask)

2. **DELETE /api/mods/{mod_id}/genres** (línea 389-410)
   - Ruta: `remove_genres_from_mod()`
   - Autenticación: Cualquier usuario autenticado
   - Descripción: Remover (soft delete) géneros de un mod
   - Cambios capturados: Marca ModGenre como is_active=False
   - Notificaciones: NINGUNA

---

## 2. IMPLEMENTACIÓN ACTUAL DE NOTIFICACIONES DISCORD

### Archivos involucrados:
- `src/utils/discord_notifier.py` - Clase DiscordNotifier (métodos async)
- `src/background_tasks.py` - Wrapper síncrono para ejecutar en BackgroundTasks

### Métodos en DiscordNotifier (async):

1. **notify_mod_created(mod, user)** → True/False
   - Detecta si es UPLOADER (pendiente) o no (aprobado automáticamente)
   - Formatea embed con COLOR_PENDING (rojo) o COLOR_APPROVED (verde)
   - Incluye: Creador, Nombre, Personaje, Duración, Estado, Revisión, Géneros

2. **notify_mod_updated(mod, user, changes)** → True/False
   - Detecta cambios en required_revision
   - Si cambio: True→False = Llama a notify_mod_approved
   - Si otros cambios = Formatea embed con detalles de cambios (COLOR_UPDATED - naranja)

3. **notify_mod_approved(mod, approved_by)** → True/False
   - Color: COLOR_APPROVED_ADMIN (verde oscuro)
   - Muestra: Mod, Creador, Aprobador, Descripción, Link al mod

4. **notify_mod_rejected(mod, rejected_by)** → True/False
   - Color: 0xFF0000 (Rojo)
   - Muestra: Mod, Creador, Rechazador, Descripción, Comentarios, Link

5. **notify_mod_deleted(mod, deleted_by)** → True/False
   - Color: 0x808080 (Gris)
   - Muestra: Mod, Creador, Eliminador, Descripción, Razón, Link

6. **notify_mod_restored(mod, restored_by)** → True/False
   - Color: 0x00DD00 (Verde oscuro)
   - Muestra: Mod, Creador, Restaurador, Descripción, Link

7. **notify_mod_completed(mod)** → True/False
   - Color: COLOR_APPROVED (verde)
   - Muestra: Mod, Personaje, Duración, Conteo de imágenes, Créditos por tipo, Géneros, Link

### Estructura de Embeds Discord:
Todos los embeds incluyen:
- **title**: Acción + icono emoji
- **color**: Código hexadecimal (decimal)
- **description**: Texto principal o resumen
- **fields**: Array de campos inline/no-inline
- **footer**: ID del mod + timestamp

### Manejo de errores:
- Try-catch en cada método async
- Retorna False si falla (NO interrumpe API)
- Logs ERROR si hay excepciones
- Valida si Discord está configurado (`is_configured()`)

---

## 3. DÓNDE SE LLAMAN NOTIFICACIONES DISCORD

### En src/routes/mods.py:

| Línea | Acción | Método Discord | Tipo Background |
|-------|--------|-----------------|-----------------|
| 160 | POST create | `notify_mod_created` | BackgroundTasks |
| 180 | PUT update | `notify_mod_updated` | BackgroundTasks |
| 221 | DELETE mod | `notify_mod_deleted` | BackgroundTasks |
| 264 | POST approve | `notify_mod_approved` | BackgroundTasks |
| 312 | POST reject | `notify_mod_rejected` | BackgroundTasks |
| 357 | POST restore | `notify_mod_restored` | BackgroundTasks |

### Flujo de ejecución:

```
Ruta HTTP → CRUD (servicio) → background_tasks.add_task() 
→ src/background_tasks.py (wrapper síncrono) 
→ Crea event loop → DiscordNotifier.método_async() 
→ DiscordNotifier._send_webhook() 
→ aiohttp.post(WEBHOOK_URL)
```

### En src/routes/creditos.py (importado):
- Llama a `notify_mod_completed` cuando se agrega un crédito completo

---

## 4. PATRÓN CONSISTENTE DE CAPTURA DE CAMBIOS

### En CRUD_MOD.update_mod() (líneas 127-186):

```python
changes = {}
mod_data = data.model_dump()

for key, value in mod_data.items():
    if value is None and key in required_fields:
        raise error
    
    if value is None:
        continue
    
    if hasattr(mod, key):
        old_value = getattr(mod, key)
        if old_value != value:
            changes[key] = {
                "old": old_value,
                "new": value
            }
        setattr(mod, key, value)
```

**Estructura de cambios retornados:**
```python
{
    "field_name": {
        "old": old_value,
        "new": new_value
    },
    ...
}
```

### En CRUD_MOD.approve_mod() (líneas 227-264):

```python
changes = {
    "required_revision": {
        "old": True,
        "new": False
    }
}
```

### En CRUD_MOD.reject_mod() (líneas 266-309):

```python
changes = {
    "required_revision": {
        "old": True,
        "new": False
    },
    "rejected": {
        "old": False,
        "new": True
    }
}
```

### Campos NO capturados en cambios:
- `created_by`, `updated_by` (auditoría)
- `created_at` (ignorado)
- `is_active` (cambios de estado)

### Campos especiales con lógica:
- Si `required_revision` cambia de True→False: Se establece `approved_at`
- En `reject_mod()`: Se guardan comentarios en `comments`
- En `delete_mod()`: Se guardan razón en `comments`

---

## 5. MÉTODOS CRUD EN src/services/mods.py

### CREAR:
- `create_mod(data: ModBase, user: TokenUser) → Mod`
  - Genera slug normalizado
  - Verifica slug único
  - Si UPLOADER: required_revision=True, is_active=False
  - Si EDITOR/OWNER: required_revision=False, is_active=True

### LEER:
- `get_mod(mod_id: int) → Mod | None`
  - Solo activos (is_active=True)
  
- `get_mods(skip: int, limit: int) → List[Mod]`
  - Solo activos (público)
  
- `get_mods_admin(skip: int, limit: int) → List[Mod]`
  - Incluyendo inactivos (admin)
  
- `get_mod_genres(mod_id: int) → List[Genre]`
  - Solo géneros activos del mod

### ACTUALIZAR:
- `update_mod(mod_id: int, data: ModBase, user: TokenUser) → Tuple[Mod, Dict]`
  - Solo EDITOR/OWNER
  - Retorna (mod, cambios_dict)
  - Valida campos requeridos: {name, status, duration, character}
  - Normaliza slug si se proporciona
  
- `approve_mod(mod_id: int, user: TokenUser) → Tuple[Mod, Dict]`
  - Solo EDITOR/OWNER
  - Solo si required_revision=True
  - Establece: required_revision=False, approved_by, approved_at
  - Retorna (mod, cambios_dict)
  
- `reject_mod(mod_id: int, user: TokenUser, comments: str) → Tuple[Mod, Dict]`
  - Solo EDITOR/OWNER
  - Solo si required_revision=True
  - Establece: required_revision=False, rejected_by, rejected_at, comments
  - Retorna (mod, cambios_dict)
  
- `add_genres_to_mod(mod_id: int, genre_ids: List[int]) → Mod`
  - Evita duplicados
  - Reactiva géneros inactivos
  
- `remove_genres_from_mod(mod_id: int, genre_ids: List[int]) → Mod`
  - Soft delete: marca is_active=False

### ELIMINAR:
- `delete_mod(mod_id: int, user: TokenUser) → Mod`
  - Solo EDITOR/OWNER
  - Soft delete: is_active=False
  - Establece: deleted_by
  - NO toma razón (se guarda en comments en ruta)
  
- `restore_mod(mod_id: int, user: TokenUser) → Mod`
  - **PROBLEMA**: Método NO existe en CRUD_MOD pero se llama en ruta (línea 339)
  - Debería revertir: is_active=True, limpiar deleted_by, deleted_at

### UTILIDADES:
- `_organize_credits(mod, db: Session) → Dict`
  - Agrupa créditos por tipo: creators, translators, porters
  
- `_enrich_credit_with_user(credit, db) → Dict`
  - Si tiene id_user: retorna {id, type, user}
  - Si no: retorna datos completos del crédito
  
- `is_mod_complete(mod_id: int) → bool`
  - True si tiene imágenes Y créditos activos

---

## 6. PROBLEMAS IDENTIFICADOS

### Métodos faltantes en CRUD_MOD:
1. ❌ `restore_mod()` - Llamado en ruta pero NO definido (línea 339)

### Métodos no implementados en CRUD_NOTIFICATION:
1. ❌ `notify_mod_deleted()` - Llamado en ruta (línea 213) pero NO existe
2. ❌ `notify_mod_restored()` - Llamado en ruta (línea 349) pero NO existe

### Incosistencias:
- `delete_mod()` en CRUD no toma razón, pero ruta pasa `request.reason`
- `delete_mod()` retorna solo `Mod`, pero ruta lo llama con razón
- La razón se guarda en `mod.comments` en la ruta (línea 203), no en el servicio

### Falta sincronización:
- Background tasks usan `DiscordNotifier.notify_mod_deleted` directamente
- Pero `CRUD_NOTIFICATION.notify_mod_deleted` no existe
- Hay inconsistencia en dónde se crea la notificación de BD

