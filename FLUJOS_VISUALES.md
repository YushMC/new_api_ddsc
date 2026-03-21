# Flujos Visuales: Colecciones e Imágenes

## DIAGRAMA 1: Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Frontend)                       │
│                   (Autenticado o Anónimo)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP (REST API)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌────────────────┐
│  /collections   │ │/mods-collect │ │   /images      │
│  Routes         │ │   Routes     │ │    Routes      │
├─────────────────┤ ├──────────────┤ ├────────────────┤
│ 8 endpoints     │ │ 7 endpoints  │ │ 13 endpoints   │
│ CRUD Básico     │ │ Relaciones   │ │ Upload/Delete  │
└────────┬────────┘ └──────┬───────┘ └────────┬───────┘
         │                 │                  │
         └────────────┬────┴────────┬─────────┘
                      │            │
                      ▼            ▼
         ┌──────────────────────────────────────┐
         │  Servicios (CRUD)                    │
         │  - CRUD_COLLECTION                   │
         │  - CRUD_MODS_COLLECTION              │
         │  - CRUD_IMAGE                        │
         └────────────┬──────────────────────┬──┘
                      │                      │
                      ▼                      ▼
         ┌──────────────────────┐  ┌──────────────────┐
         │ SQLAlchemy Models    │  │ Utilidades       │
         │ - Collection         │  │ - ResponseBuilder│
         │ - ModsCollection     │  │ - ImageProcessor │
         │ - Image              │  │ - S3Manager      │
         └──────────────┬───────┘  └────────┬─────────┘
                        │                   │
                        │                   ▼
                        │          ┌──────────────────┐
                        │          │    AWS S3        │
                        │          │ (Almacenamiento) │
                        │          └──────────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │   PostgreSQL Database    │
         │ - collections            │
         │ - mods_collections       │
         │ - imagenes               │
         │ - users                  │
         │ - mods                   │
         │ - notifications          │
         └──────────────────────────┘
```

## DIAGRAMA 2: Flujo Crear Colección

```
┌─────────────────┐
│  Frontend POST  │
│ /collections    │
│ {name, desc}    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Route Handler: create_collection()  │
└────────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ [Validation - Middleware JWT]    │
    │ ✓ Token válido                   │
    │ ✓ Rol es OWNER/EDITOR            │
    └────────┬─────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼ (Error)         ▼ (OK)
┌─────────┐      ┌────────────────────┐
│  403    │      │CRUD_COLLECTION()   │
│Forbidden│      │create_collection() │
└─────────┘      └────────┬───────────┘
                          │
                          ▼
                  ┌───────────────────┐
                  │ Validaciones CRUD │
                  │ ✓ Nombre único    │
                  │ ✓ Max length 255  │
                  └────────┬──────────┘
                           │
                   ┌───────┴────────┐
                   │                │
          ▼ (Error)                 ▼ (OK)
      ┌──────────┐          ┌──────────────────┐
      │  400     │          │INSERT Collection │
      │Bad Req   │          │into Database     │
      └──────────┘          └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │ Auto-generated:  │
                            │ - created_at     │
                            │ - created_by     │
                            │ - updated_at     │
                            │ - updated_by     │
                            │ - is_active=True │
                            └────────┬─────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ResponseBuilder.created│
                         │Separar en:            │
                         │ - resource            │
                         │ - info (timestamps)   │
                         └────────┬──────────────┘
                                  │
                                  ▼
                         ┌─────────────────────┐
                         │  201 Created JSON   │
                         │{                    │
                         │ response: "created" │
                         │ data: {             │
                         │  resource: {...},   │
                         │  info: {...}        │
                         │ }                   │
                         │}                    │
                         └─────────────────────┘
```

## DIAGRAMA 3: Flujo Subir Imagen (Logo)

```
┌──────────────────────────┐
│  Frontend POST/upload    │
│ /images/logo/{mod_id}    │
│ FormData: file           │
└────────┬─────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Route Handler: upload_logo()   │
└────────┬─────────────────────┬─┘
         │                     │
         ▼                     ▼
    [Validation]      [Mod Exists Check]
    - JWT Token OK         ✓ Yes → OK
    - OWNER/EDITOR      ✗ No  → 404 Error
    ✓ OK
         │
         ▼
┌──────────────────────────────────────┐
│ Validar Logo no existe               │
│ SELECT * FROM imagenes               │
│ WHERE mod_id = {id}                  │
│ AND type = "logo"                    │
│ AND is_active = True                 │
└────────┬──────────────────┬──────────┘
         │                  │
    ▼ (Existe)          ▼ (No existe)
┌──────────┐      ┌──────────────────┐
│  409     │      │Procesar Imagen   │
│Conflict  │      └────────┬─────────┘
│(reuse)   │               │
└──────────┘               ▼
                ┌────────────────────────┐
                │ImageProcessor.validate │
                │_image(content)         │
                └────────┬───────────────┘
                         │
                 ┌───────┴────────┐
                 │                │
          ▼(Err)                  ▼(OK)
      ┌──────┐          ┌──────────────────┐
      │ 400  │          │ImageProcessor    │
      │Bad   │          │.process_to_webp()│
      └──────┘          └────────┬─────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │ S3Manager.upload_file│
                      │ (webp_content)       │
                      └────────┬─────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │Upload to S3      │
                      │Return: URL       │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │INSERT Image{     │
                      │  url: S3_URL,    │
                      │  type: "logo",   │
                      │  mod_id: id,     │
                      │  is_active: True │
                      │}                 │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ ResponseBuilder  │
                      │ .created()       │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ 201 Created      │
                      │{                 │
                      │ response:"created"
                      │ data:{           │
                      │  resource:{...}, │
                      │  info:{...}      │
                      │ }                │
                      │}                 │
                      └──────────────────┘
```

## DIAGRAMA 4: Flujo Soft Delete con Reactivate

```
┌──────────────────────┐
│  DELETE /resource/id │
└────────┬─────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Validar permisos (OWNER/ED)│
└────────┬───────────────────┘
         │
    ┌────┴────┐
    │          │
▼(No)         ▼(Sí)
[403]      ┌────────────────────┐
           │UPDATE resource     │
           │SET is_active=False │
           │WHERE id=?          │
           └────────┬───────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ 200 OK Deleted   │
           │ {                │
           │  response:"del"  │
           │  data: null      │
           │ }                │
           └────────┬─────────┘
                    │
         ┌──────────┴──────────┐
         │ (Recurso inactivo)  │
         │ - No aparece en GET │
         │ - Aparece en admin  │
         │ - No se elimina BD  │
         └─────────┬───────────┘
                   │
    (Usuario descubre que necesita recuperarlo)
                   │
                   ▼
     ┌──────────────────────┐
     │POST /resource/{id}   │
     │    /reactivate       │
     └────────┬─────────────┘
              │
              ▼
     ┌──────────────────────┐
     │ UPDATE resource      │
     │ SET is_active=True   │
     │ WHERE id=?           │
     └────────┬─────────────┘
              │
              ▼
     ┌──────────────────────┐
     │ 200 OK Updated       │
     │ Recurso activo nuevo │
     └──────────────────────┘
```

## DIAGRAMA 5: Flujo Actualizar Imagen (PUT Logo)

```
┌────────────────────────┐
│PUT /images/logo/{id}   │
│FormData: file          │
└────────┬───────────────┘
         │
         ▼
   [Validar permisos]
         │
         ▼
┌────────────────────────────────┐
│Obtener logo actual             │
│SELECT * FROM imagenes          │
│WHERE mod_id={id} AND type=logo │
└────────┬───────────────┬────────┘
         │               │
    ▼(No)                ▼(Sí)
  [404]          ┌──────────────────┐
                 │Validar imagen    │
                 └────────┬─────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │ImageProcessor       │
                │.process_to_webp()   │
                └────────┬─────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │S3Manager.delete_file() │
            │(old_url)               │
            └────────┬───────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │S3Manager.upload_file()   │
        │(webp_content)            │
        │Return: NEW_URL           │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │UPDATE imagenes           │
        │SET url = NEW_URL         │
        │WHERE id = old_id         │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │ResponseBuilder.updated() │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │200 OK Updated            │
        │{                          │
        │ response: "updated"      │
        │ data: {                  │
        │  resource: {...new...},  │
        │  info: {...updated...}   │
        │ }                        │
        │}                         │
        └──────────────────────────┘
```

## DIAGRAMA 6: Ciclo de Vida Completo de Colección

```
┌─────────────────┐
│  No Existe      │
│  (Inicio)       │
└────────┬────────┘
         │
         │ POST /collections
         ▼
┌────────────────────┐
│  CREADA            │
│  is_active = True  │
│  En BD             │
│  Visible (público) │
│  Editable (admin)  │
└────────┬───────────┘
         │
    ┌────┼────┬────┐
    │    │    │    │
    │    │    │    └──► PUT /collections/{id}
    │    │    │        Actualiza nombre/desc
    │    │    │        (Vuelve a CREADA)
    │    │    │
    │    │    └──► POST /mods-collections
    │    │        Agrega mods
    │    │
    │    └──► GET /collections/{id}
    │        (Acceso público)
    │
    │ DELETE /collections/{id}
    ▼
┌──────────────────────────┐
│  ELIMINADA (Soft)        │
│  is_active = False       │
│  En BD (no visible)      │
│  NO visible (público)    │
│  Visible solo (admin)    │
└──────────────┬───────────┘
               │
           ┌───┴───┐
           │       │
           │       └──► GET /collections  ──► No aparece
           │           GET /collections/admin/all ──► Sí aparece
           │
           │ POST /collections/{id}/reactivate
           ▼
    ┌─────────────────┐
    │  CREADA otra vez│
    │  Recuperada     │
    │  is_active=True │
    └─────────────────┘
```

## DIAGRAMA 7: Relación Mods-Collections

```
┌──────────────────────┐
│   COLECCIONES        │
│  (1 colección)       │
├──────────────────────┤
│ - id: 1              │
│ - name: "Classics"   │
│ - desc: "..."        │
└────────────┬─────────┘
             │ 1:N
             │
         ┌───▼──────────────────┐
         │ MODS_COLLECTIONS     │
         │ (Tabla Intermedia)   │
         ├──────────────────────┤
         │ - id: 10 ┬─┐         │
         │ - id: 11 ┼─┤ active  │
         │ - id: 12 ┼─┤         │
         │ - id: 13 ┴─┘ inactive│
         └───┬──────────────────┘
             │ N:1
             │
      ┌──────▼────────────────────┐
      │      MODS                 │
      │  (Múltiples mods)         │
      ├───────────────────────────┤
      │ - id: 5 (mod1)            │
      │ - id: 8 (mod2)            │
      │ - id: 12 (mod3)           │
      │ - id: 15 (mod4) [sin rel] │
      └───────────────────────────┘

Lectura:
- Colección 1 tiene relaciones con Mods: 5, 8, 12
- Relación 13 está inactiva (mod no en colección visual)
- Mod 15 no está en ninguna colección

Operaciones:
- Agregar: POST /mods-collections {mod_id, collection_id}
- Remover: DELETE /mods-collections/{id}
- Listar: GET /mods-collections/collection/1
```

## DIAGRAMA 8: Límites de Imágenes por Mod

```
┌────────────────────────────────┐
│  MOD ID: 5                     │
├────────────────────────────────┤
│                                │
│  Logo (Máx: 1)                 │
│  ┌──────────────┐              │
│  │ ✓ Existe 1   │ ← Límite OK  │
│  └──────────────┘              │
│  Acción: Subir = 409 Error     │
│          PUT = Reemplazar      │
│          DELETE = Eliminar     │
│                                │
│  Main (Máx: 1)                 │
│  ┌──────────────┐              │
│  │ ✓ Existe 1   │ ← Límite OK  │
│  └──────────────┘              │
│  Acción: Igual que Logo        │
│                                │
│  Screenshots (Máx: 4)          │
│  ┌──────────────┐              │
│  │ ✓ Existe 3   │ ← Puede +1   │
│  │ ✓ Existe 3   │              │
│  │ ✓ Existe 3   │              │
│  └──────────────┘              │
│  Acción: Subir = OK (+1 = 4)   │
│          Subir otra = 409       │
│          DELETE = -1            │
│                                │
└────────────────────────────────┘

Validaciones por tipo en count_imagenes_by_mod_and_type():
- LOGO:      count >= 1 → Error 409
- MAIN:      count >= 1 → Error 409
- SCREENSHOT:count >= 4 → Error 409
```

## DIAGRAMA 9: Respuesta Estándar (ResponseBuilder)

```
┌────────────────────────────────────────┐
│  Respuesta GET (Colección Pública)     │
├────────────────────────────────────────┤
│ {                                      │
│   "response": "success",               │
│   "message": "...",                    │
│   "data": [                            │
│     {                                  │
│       "id": 1,                         │
│       "name": "Horror",                │
│       "description": "...",            │
│       "created_at": "2026-03-20...",   │
│       "created_by": "admin",           │
│       "updated_at": "2026-03-20...",   │
│       "updated_by": "admin",           │
│       "is_active": true                │
│     }                                  │
│   ]                                    │
│ }                                      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Respuesta POST (Crear Recurso)        │
├────────────────────────────────────────┤
│ {                                      │
│   "response": "created",               │
│   "message": "... exitosamente",       │
│   "data": {                            │
│     "resource": {                      │
│       "id": 1,                         │
│       "name": "Horror",                │
│       "description": "..."             │
│     },                                 │
│     "info": {                          │
│       "created_at": "2026-03-20...",   │
│       "created_by": "admin",           │
│       "updated_at": "2026-03-20...",   │
│       "updated_by": "admin",           │
│       "is_active": true                │
│     }                                  │
│   }                                    │
│ }                                      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Respuesta DELETE (Eliminar)           │
├────────────────────────────────────────┤
│ {                                      │
│   "response": "deleted",               │
│   "message": "... eliminado...",       │
│   "data": null                         │
│ }                                      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Respuesta ERROR (Bad Request)         │
├────────────────────────────────────────┤
│ {                                      │
│   "detail": "Ya existe colección..."   │
│ }                                      │
│                                        │
│ Status: 400 Bad Request                │
└────────────────────────────────────────┘
```

