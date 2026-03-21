# REFERENCIA RÁPIDA: Rutas, Servicios y Notificaciones

## Tabla Rápida: Rutas POST/PUT/DELETE

| # | HTTP | Ruta | Servicio | Notif. BD | Notif. Discord | Status | Linea |
|---|------|------|----------|-----------|----------------|--------|-------|
| 1 | POST | /api/mods | create_mod | pending_review | created | ✅ | 137 |
| 2 | PUT | /api/mods/{id} | update_mod | ❌ | updated | ✅ | 167 |
| 3 | DEL | /api/mods/{id} | delete_mod | ❌ FALTA | deleted | ✅ | 187 |
| 4 | POST | /api/mods/{id}/approve | approve_mod | approved | approved | ✅ | 225 |
| 5 | POST | /api/mods/{id}/rejected | reject_mod | rejected | rejected | ✅ | 272 |
| 6 | POST | /api/mods/{id}/restore | restore_mod | ❌ FALTA | restored | ❌ FALTA | 320 |
| 7 | POST | /api/mods/{id}/genres | add_genres | ❌ | ❌ | ✅ | 365 |
| 8 | DEL | /api/mods/{id}/genres | remove_genres | ❌ | ❌ | ✅ | 389 |

## Métodos CRUD Disponibles

| Método | Entrada | Salida | Retorna Cambios |
|--------|---------|--------|-----------------|
| create_mod | ModBase, user | Mod | ❌ |
| get_mod | id | Mod \| None | - |
| get_mods | skip, limit | List[Mod] | - |
| get_mods_admin | skip, limit | List[Mod] | - |
| update_mod | id, ModBase, user | Mod, Dict | ✅ |
| delete_mod | id, user | Mod | ❌ |
| **restore_mod** | id, user | Mod | ❌ **FALTA** |
| approve_mod | id, user | Mod, Dict | ✅ |
| reject_mod | id, user, comments | Mod, Dict | ✅ |
| add_genres_to_mod | id, [genre_ids] | Mod | ❌ |
| remove_genres_from_mod | id, [genre_ids] | Mod | ❌ |
| get_mod_genres | id | List[Genre] | - |

## Métodos DiscordNotifier (7 total)

```python
# Async methods - todos retornan bool
async def notify_mod_created(mod, user) → bool
async def notify_mod_updated(mod, user, changes) → bool
async def notify_mod_approved(mod, approved_by) → bool
async def notify_mod_rejected(mod, rejected_by) → bool
async def notify_mod_deleted(mod, deleted_by) → bool
async def notify_mod_restored(mod, restored_by) → bool
async def notify_mod_completed(mod) → bool
```

## Métodos CRUD_NOTIFICATION (Incompletos)

```python
# Existen:
def notify_mod_pending_review(mod_id, mod_name, uploader_name)
def notify_mod_approved(mod_id, mod_name, mod_creator_id, approved_by)
def notify_mod_rejected(mod_id, mod_name, mod_creator_id, rejected_by)

# FALTAN:
def notify_mod_deleted(...)  ❌ LLAMADO en ruta línea 213
def notify_mod_restored(...) ❌ LLAMADO en ruta línea 349
```

## Estructura de Cambios Retornada

```python
# Ejemplo de dict retornado por update_mod(), approve_mod(), reject_mod()
{
    "field_name": {
        "old": old_value,
        "new": new_value
    }
}

# Campos excluidos de cambios:
# - created_by, updated_by (auditoría)
# - created_at (marcado de tiempo)
# - is_active (estado)
```

## Flujo: Creación a Discord

```
cliente → POST /api/mods
    ↓
route: create_mod_route()
    ↓
service: crud.create_mod(data, user) → Mod
    ↓
if UPLOADER:
    → CRUD_NOTIFICATION.notify_mod_pending_review() [BD]
    
↓
background_tasks.add_task(notify_mod_created, mod, user)
    ↓
threads: notify_mod_created() [wrapper]
    ↓
async: DiscordNotifier.notify_mod_created()
    ↓
format: _format_embed_created() + _send_webhook()
    ↓
Discord webhook POST → Canal Discord
```

## Flujo: Actualización a Discord

```
cliente → PUT /api/mods/{id}
    ↓
route: update_mod_route()
    ↓
service: crud.update_mod(data, user) → (Mod, changes_dict)
    ↓
background_tasks.add_task(notify_mod_updated, mod, user, changes)
    ↓
threads: notify_mod_updated() [wrapper]
    ↓
async: DiscordNotifier.notify_mod_updated()
    ├─ Si cambio en required_revision (True→False):
    │  └─ _format_embed_approved()
    └─ Si otros cambios:
       └─ _format_embed_updated() con detalles
    ↓
_send_webhook() → Discord
```

## Campos de Auditoría Capturados

| Campo | Tipo | Cuándo se guarda | Quién actualiza |
|-------|------|------------------|-----------------|
| created_by | str | En create | Usuario que crea |
| created_at | datetime | En create | Auto (BD) |
| updated_by | str | En cualquier update | Usuario que actualiza |
| updated_at | datetime | En cualquier update | Auto (BD) |
| deleted_by | str | En delete (soft) | Usuario que elimina |
| deleted_at | datetime | ❌ NO GUARDADO | - |
| approved_by | str | En approve_mod | Usuario que aprueba |
| approved_at | datetime | En approve_mod | Auto (NOW) |
| rejected_by | str | En reject_mod | Usuario que rechaza |
| rejected_at | datetime | En reject_mod | Auto (NOW) |
| comments | str | En reject/delete | Razón rechazo/eliminación |

## Autenticación por Ruta

| Ruta | Requiere Auth | Solo Rol | Descripción |
|------|---------------|----------|-------------|
| POST /api/mods | ✅ Sí | - | Cualquiera autenticado |
| PUT /api/mods/{id} | ✅ Sí | EDITOR/OWNER | No UPLOADER |
| DEL /api/mods/{id} | ✅ Sí | EDITOR/OWNER | No UPLOADER |
| POST /api/mods/{id}/approve | ✅ Sí | EDITOR/OWNER | Solo admin |
| POST /api/mods/{id}/rejected | ✅ Sí | EDITOR/OWNER | Solo admin |
| POST /api/mods/{id}/restore | ✅ Sí | EDITOR/OWNER | Solo admin |
| POST /api/mods/{id}/genres | ✅ Sí | - | Cualquiera autenticado |
| DEL /api/mods/{id}/genres | ✅ Sí | - | Cualquiera autenticado |
| GET /api/mods/{id}/genres | ❌ No | - | Público |

## Colores Discord (Decimales)

```python
COLOR_PENDING = 0xFF0000          # Rojo - Pendiente aprobación
COLOR_APPROVED = 0x00FF00         # Verde - Aprobado automáticamente
COLOR_UPDATED = 0xFFA500          # Naranja - Actualizado
COLOR_APPROVED_ADMIN = 0x00DD00   # Verde oscuro - Aprobado por admin
COLOR_REJECTED = 0xFF0000         # Rojo - Rechazado
COLOR_DELETED = 0x808080          # Gris - Eliminado
COLOR_RESTORED = 0x00DD00         # Verde - Restaurado
```

## Problemas en Código (Estado Actual)

```
✅ = Funcionando
❌ = Falta implementación
⚠️ = Inconsistencia

restore_mod() en CRUD_MOD         ❌ FALTA
notify_mod_deleted() en CRUD_NOT  ❌ FALTA
notify_mod_restored() en CRUD_NOT ❌ FALTA
delete_mod() con reason param     ⚠️ Guardado en ruta, no servicio
```

## Búsqueda de Cambios por Patrón

En rutas se reciben cambios así:
```python
mod, changes = crud.update_mod(...)  # Si retorna tuple
changes = crud.update_mod(...)       # Si retorna solo cambios
```

Patrón de notificación:
```python
background_tasks.add_task(DiscordNotifier.método_async, mod, ...)
```

Para obtener cambios:
- ✅ Métodos que retornan tuple: update_mod, approve_mod, reject_mod
- ❌ Métodos que NO retornan cambios: create_mod, delete_mod, restore_mod (falta)

