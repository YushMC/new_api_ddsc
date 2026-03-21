# Índice de Documentación: Colecciones e Imágenes

Documentación completa sobre las rutas, modelos, servicios y notificaciones para colecciones e imágenes en la API DDSC.

## Documentos Disponibles

### 1. **RESUMEN_EJECUTIVO_COLECCIONES_IMAGENES.md** (11 KB)
**Mejor para**: Consulta rápida, inicio rápido, referencia de endpoints

Contiene:
- Tabla rápida de endpoints (GET, POST, PUT, DELETE)
- Esquema visual de base de datos
- Flujos de operación (diagramas ASCII)
- Tabla de validaciones por rol
- Límites de imágenes por tipo
- Códigos HTTP y errores
- Archivos clave del proyecto

**Ideal para**: Conocer rápidamente qué rutas existen y cómo funcionan

---

### 2. **ANALISIS_COLECCIONES_IMAGENES.md** (18 KB)
**Mejor para**: Análisis profundo, documentación técnica completa

Contiene:
- Detalle completo de cada ruta (headers, body, validaciones, respuestas)
- Definición completa de modelos SQLAlchemy
- Schemas Pydantic completos
- Estructura de respuestas (ResponseBuilder)
- Métodos CRUD de cada servicio
- Notificaciones existentes (solo para MODS)
- Resumen de puntos clave (soft deletes, roles, timestamps)

**Ideal para**: Entender la implementación, modificar código, documentar cambios

---

### 3. **EJEMPLOS_PRACTICOS_COLECCIONES_IMAGENES.md** (16 KB)
**Mejor para**: Implementación, testing, integración

Contiene:
- Ejemplos reales de cURL para cada endpoint
- Respuestas JSON de éxito y error
- Código Python con clase Cliente (requests)
- Manejo de errores en Python
- Ejemplos de uso práctico
- Casos de error comunes

**Ideal para**: Hacer requests, testear API, integrar en otros proyectos

---

## Matriz de Selección Rápida

| Necesidad | Documento | Sección |
|-----------|-----------|---------|
| Ver todos los endpoints | Ejecutivo | "TABLA RÁPIDA DE REFERENCIA" |
| Crear colección | Ejemplos | "EJEMPLOS COLECCIONES - 1" |
| Subir imagen | Ejemplos | "EJEMPLOS IMÁGENES - 1" |
| Entender flujo completo | Análisis | "1. RUTAS POST/PUT/PATCH/DELETE" |
| Ver estructura respuesta | Análisis | "6. CÓMO SE RETORNAN CAMBIOS" |
| Validaciones por rol | Ejecutivo | "VALIDACIONES Y LIMITES" |
| Códigos HTTP | Ejecutivo | "RESPUESTAS Y CÓDIGOS HTTP" |
| Modelos BD | Análisis | "4. DEFINICIÓN DE MODELOS" |
| Notificaciones | Análisis | "7. NOTIFICACIONES EXISTENTES" |
| Ejemplos Python | Ejemplos | "CÓDIGO PYTHON" |

---

## Resumen Rápido

### Recursos Principales

#### Collections
- Tabla: `collections`
- Campos: `id`, `name` (único), `description`
- Timestamps: `created_at`, `updated_at`, `created_by`, `updated_by`, `is_active`
- Endpoints: 8 (GET, POST, PUT, DELETE, admin variants, reactivate)

#### Mods-Collections (relación)
- Tabla: `mods_collections` (junction table)
- Campos: `id`, `mod_id`, `collection_id`
- Timestamps: mismos que Collections
- Endpoints: 7 (GET, POST, DELETE, admin variants, reactivate)

#### Images
- Tabla: `imagenes`
- Campos: `id`, `url`, `type` (logo/main/screenshot), `mod_id`
- Timestamps: mismos que Collections
- Endpoints: 13 (GET, POST logo/main/screenshots, PUT logo/main/screenshots, DELETE, admin variants)

### Operaciones Soportadas

| Operación | OWNER | EDITOR | UPLOADER |
|-----------|-------|--------|----------|
| GET (activos) | ✓ | ✓ | ✓ |
| GET admin | ✓ | ✓ | ✗ |
| POST (crear) | ✓ | ✓ | ✗ |
| PUT (actualizar) | ✓ | ✓ | ✗ |
| DELETE (soft) | ✓ | ✓ | ✗ |
| POST reactivate | ✓ | ✓ | ✗ |

### Límites de Imágenes

- **Logo**: 1 máximo por mod
- **Main**: 1 máximo por mod
- **Screenshots**: 4 máximo por mod

### Soft Deletes

Todas las operaciones DELETE marcan `is_active = False`:
- Datos se mantienen en BD
- Se ocultan en GET normales
- Visible en GET admin
- Recuperable con `/reactivate`

### Timestamps Automáticos

```json
"info": {
  "created_at": "2026-03-20T15:30:45.123456Z",
  "created_by": "username",
  "updated_at": "2026-03-20T15:30:45.123456Z",
  "updated_by": "username",
  "is_active": true
}
```

### Notificaciones Actuales

**Disponibles para MODS:**
- `MOD_PENDING_REVIEW` - Cuando UPLOADER crea
- `MOD_APPROVED` - Cuando se aprueba
- `MOD_REJECTED` - Cuando se rechaza

**FALTA para COLECCIONES e IMÁGENES:**
- Crear, actualizar, eliminar
- Agregar/remover de colecciones

---

## Archivos del Proyecto Relacionados

### Rutas (API)
```
/src/routes/collections.py           - 150 líneas
/src/routes/mods_collections.py      - 159 líneas
/src/routes/imagenes.py              - 512 líneas
```

### Servicios (CRUD)
```
/src/services/collections.py         - 110 líneas
/src/services/mods_collections.py    - 125 líneas
/src/services/imagenes.py            - 116 líneas
```

### Modelos (BD)
```
/src/models/collection.py            - 16 líneas
/src/models/mods_collection.py       - 20 líneas
/src/models/imagen.py                - 24 líneas
```

### Schemas (Validación)
```
/src/schemas/collections.py          - 24 líneas
/src/schemas/mods_collections.py     - 18 líneas
/src/schemas/imagenes.py             - 31 líneas
```

### Utilidades
```
/src/utils/response_builder.py       - Constructor de respuestas
/src/utils/image_processor.py        - Procesamiento a WebP
/src/utils/s3_manager.py             - Gestión de S3
/src/models/timestamp.py             - TimestampMixin
/src/models/enums.py                 - Enums (ImageTypeEnum, etc)
```

### Notificaciones
```
/src/models/notifications.py         - Modelo notificaciones
/src/services/notifications.py       - Servicios (CRUD)
/src/routes/notifications.py         - Endpoints
```

---

## Casos de Uso Comunes

### 1. Crear colección de mods
```
POST /collections
├─ Input: name, description
├─ Validación: Rol (solo OWNER/EDITOR)
└─ Output: 201 Created con datos + timestamps
```

### 2. Agregar mods a colección
```
POST /mods-collections
├─ Input: mod_id, collection_id
├─ Validación: Ambos existen, sin duplicados
└─ Output: 201 Created
```

### 3. Subir imagen (logo, main, screenshot)
```
POST /images/{type}/{mod_id}
├─ Input: FormData con file
├─ Proceso: Validar → WebP → S3 → BD
├─ Validación: Límites por tipo
└─ Output: 201 Created con URL
```

### 4. Actualizar imagen
```
PUT /images/{type}/{mod_id}
├─ Input: FormData con file (nueva)
├─ Proceso: Validar → WebP → Delete vieja en S3 → Upload → BD
└─ Output: 200 OK
```

### 5. Eliminar (soft delete)
```
DELETE /collections|/mods-collections|/images/{id}
├─ Proceso: is_active = False
└─ Output: 200 OK (data: null)
```

### 6. Recuperar (reactivate)
```
POST /{resource}/{id}/reactivate
├─ Proceso: is_active = True
└─ Output: 200 OK con datos
```

---

## Próximos Pasos

### Corto Plazo
- [ ] Revisar implementación actual
- [ ] Hacer pruebas de endpoints
- [ ] Validar manejo de errores

### Mediano Plazo
- [ ] Implementar notificaciones para colecciones
- [ ] Implementar notificaciones para imágenes
- [ ] Agregar pruebas unitarias
- [ ] Agregar pruebas de integración

### Largo Plazo
- [ ] Considerar PATCH para actualizaciones parciales
- [ ] Considerar bulk operations
- [ ] Considerar soft restore (deshacer eliminación)
- [ ] Optimizar queries con índices

---

## Contacto y Preguntas

Esta documentación fue generada el **20/03/2026**.

Para preguntas específicas, consulta:
1. El análisis completo (sección más relevante)
2. Los ejemplos prácticos (código ejecutable)
3. El código fuente en `/src`

---

**Última actualización**: 20/03/2026
**Versión de API**: 1.0.0
**Estado**: Completamente funcional
