# DIAGRAMA DE FLUJO: Captura de Cambios y Notificaciones

## FLUJO COMPLETO: POST CREATE MOD

```
1. Cliente envía POST /api/mods
   ↓
2. create_mod_route(data, user, db, background_tasks)
   ↓
3. crud.create_mod(data, user)
   ├─ Genera slug normalizado
   ├─ Valida slug único
   ├─ Si UPLOADER: required_revision=True, is_active=False
   ├─ Si EDITOR/OWNER: required_revision=False, is_active=True
   ├─ Guarda: created_by, created_at (automático)
   └─ Retorna: mod (objeto persistido)
   ↓
4. Si user.rol == UPLOADER:
   ├─ CRUD_NOTIFICATION.notify_mod_pending_review()
   │  └─ Crea notificación BD para TODOS los EDITORS/OWNERS
   └─ background_tasks.add_task(notify_mod_created, mod, user)
   ↓
5. Si user.rol != UPLOADER:
   └─ background_tasks.add_task(notify_mod_created, mod, user)
   ↓
6. Retorna 201 + mod preparado
   
--- En thread background (asincrónico) ---
   
7. notify_mod_created(mod, user)
   └─ Background wrapper síncrono
      ├─ asyncio.new_event_loop() o get_running_loop()
      └─ loop.run_until_complete(DiscordNotifier.notify_mod_created())
         ↓
8. DiscordNotifier.notify_mod_created(mod, user)
   ├─ is_approved = (user.rol != UPLOADER)
   ├─ _format_embed_created(mod, user, is_approved)
   │  └─ Retorna dict embeds con COLOR_PENDING o COLOR_APPROVED
   └─ _send_webhook(payload)
      └─ aiohttp.post(WEBHOOK_URL) → Discord
```

## FLUJO COMPLETO: PUT UPDATE MOD

```
1. Cliente envía PUT /api/mods/{mod_id}
   ↓
2. update_mod_route(mod_id, data, user, db, background_tasks)
   ├─ Valida user.rol != UPLOADER
   └─ crud.update_mod(mod_id, data, user) → retorna (mod, changes)
   
3. update_mod(mod_id, data, user)
   ├─ Carga mod existente
   ├─ changes = {}
   ├─ mod_data = data.model_dump()
   ├─ Para cada campo en mod_data:
   │  ├─ Si value is None y campo requerido: RAISE ERROR
   │  ├─ Si value is None: continue (skip)
   │  ├─ Si field existe en mod:
   │  │  ├─ old_value = getattr(mod, field)
   │  │  ├─ Si old_value != value:
   │  │  │  └─ changes[field] = {"old": old_value, "new": value}
   │  │  └─ setattr(mod, field, value)
   ├─ Si required_revision cambió True→False: approved_at = NOW
   ├─ updated_by = user.name
   ├─ COMMIT
   └─ Retorna (mod, changes)
   
4. background_tasks.add_task(notify_mod_updated, mod, user, changes)
   ↓
5. Retorna 200 + mod preparado

--- En thread background (asincrónico) ---

6. notify_mod_updated(mod, user, changes)
   ├─ asyncio loop setup
   └─ DiscordNotifier.notify_mod_updated(mod, user, changes)
      ├─ Si "required_revision" en changes:
      │  ├─ old_val = changes["required_revision"]["old"]
      │  ├─ new_val = changes["required_revision"]["new"]
      │  └─ Si old_val=True y new_val=False:
      │     └─ _format_embed_approved() → RETURN
      ├─ Si otros cambios:
      │  └─ _format_embed_updated(mod, user, changes)
      │     ├─ Filtra cambios (excluye: created_by, updated_by, created_at, is_active)
      │     └─ Muestra campo: old → new
      └─ _send_webhook(payload) → Discord
```

## FLUJO COMPLETO: DELETE MOD

```
1. Cliente envía DELETE /api/mods/{mod_id} + ModDeleteRequest(reason)
   ↓
2. delete_mod_route(mod_id, request, user, db, background_tasks)
   ├─ Valida user.rol != UPLOADER
   ├─ crud.delete_mod(mod_id, user) → mod
   │  └─ is_active = False
   │  └─ deleted_by = user.name
   │  └─ Nota: NO guarda reason aquí
   ├─ creator = query User WHERE id == mod.created_by
   ├─ Si creator existe:
   │  └─ CRUD_NOTIFICATION.notify_mod_deleted(
   │        mod_id, mod.name, creator.id, user.name
   │      )
   │     └─ Crea notificación BD para uploader
   ├─ PERO: mod.comments = request.reason
   │  (Se sobrescribe en la RUTA, no en servicio)
   └─ background_tasks.add_task(
        DiscordNotifier.notify_mod_deleted, mod, user
      )
   ↓
3. Retorna 200 "Mod eliminado"

--- En thread background ---

4. DiscordNotifier.notify_mod_deleted(mod, deleted_by)
   ├─ _format_embed_deleted(mod, deleted_by)
   │  └─ Muestra: Mod, Creador, Eliminador, Descripción, Razón
   └─ _send_webhook(payload) → Discord
```

## FLUJO COMPLETO: POST APPROVE MOD

```
1. Cliente envía POST /api/mods/{mod_id}/approve
   ↓
2. approve_mod_route(mod_id, user, db, background_tasks)
   ├─ Valida user.rol != UPLOADER
   └─ crud.approve_mod(mod_id, user) → (mod, changes)
   
3. approve_mod(mod_id, user)
   ├─ Carga mod
   ├─ Valida: mod.required_revision == True
   ├─ changes = {"required_revision": {"old": True, "new": False}}
   ├─ required_revision = False
   ├─ approved_by = user.name
   ├─ approved_at = NOW
   ├─ updated_by = user.name
   ├─ COMMIT
   └─ Retorna (mod, changes)
   
4. creator = query User WHERE name == mod.created_by
   ├─ Si creator:
   │  └─ CRUD_NOTIFICATION.notify_mod_approved(
   │        mod_id, mod.name, creator.id, user.name
   │      )
   │     └─ Crea notificación BD para uploader
   └─ background_tasks.add_task(
        DiscordNotifier.notify_mod_approved, mod, user
      )
   ↓
5. Retorna 200 + mod

--- En thread background ---

6. DiscordNotifier.notify_mod_approved(mod, approved_by)
   ├─ _format_embed_approved(mod, approved_by)
   │  └─ Color: COLOR_APPROVED_ADMIN
   └─ _send_webhook(payload) → Discord
```

## TABLA COMPARATIVA: CAPTURA DE CAMBIOS

| Método | Cambios Capturados | Retorna |
|--------|-------------------|---------|
| `create_mod()` | Automático (created_by, created_at) | `Mod` |
| `update_mod()` | Dict comparando old vs new | `(Mod, Dict)` |
| `approve_mod()` | Dict manual: required_revision | `(Mod, Dict)` |
| `reject_mod()` | Dict manual: required_revision + rejected | `(Mod, Dict)` |
| `delete_mod()` | Automático (is_active, deleted_by) | `Mod` |
| `restore_mod()` | ❌ NO EXISTE | - |
| `add_genres_to_mod()` | Relación ModGenre (no dict) | `Mod` |
| `remove_genres_from_mod()` | Relación ModGenre (soft delete) | `Mod` |

## TABLA: NOTIFICACIONES DISCORD vs BD

| Acción | Discord | BD (Notificación) |
|--------|---------|------------------|
| POST create (UPLOADER) | ✅ notify_mod_created | ✅ notify_mod_pending_review |
| POST create (EDITOR/OWNER) | ✅ notify_mod_created | ❌ Ninguna |
| PUT update | ✅ notify_mod_updated | ❌ Ninguna |
| DELETE mod | ✅ notify_mod_deleted | ❌ notify_mod_deleted NO EXISTE |
| POST approve | ✅ notify_mod_approved | ✅ notify_mod_approved |
| POST reject | ✅ notify_mod_rejected | ✅ notify_mod_rejected |
| POST restore | ✅ notify_mod_restored | ❌ notify_mod_restored NO EXISTE |

## ESTRUCTURA DE CAMBIOS DICT

```python
# Ejemplo retornado por update_mod()
{
    "name": {
        "old": "Old Mod Name",
        "new": "New Mod Name"
    },
    "status": {
        "old": "active",
        "new": "pending"
    },
    "required_revision": {
        "old": True,
        "new": False
    }
    # Excluye: created_by, updated_by, created_at, is_active
}
```

## CAMPOS DE AUDITORÍA

```python
# Campos siempre guardados en modelo:
- created_by: str (nombre del usuario que creó)
- created_at: datetime (automático en BD)
- updated_by: str (último usuario que actualizó)
- updated_at: datetime (automático en BD)
- deleted_by: str (usuario que eliminó, si soft delete)
- deleted_at: datetime (NO se guarda explícitamente - revisar modelo)
- approved_by: str (usuario que aprobó)
- approved_at: datetime (cuando se aprobó)
- rejected_by: str (usuario que rechazó)
- rejected_at: datetime (cuando se rechazó)
- comments: str (razón rechazo O razón eliminación)
```

