# DDLC Mods API - Guía de Uso

## Setup Inicial

### 1. Variables de Entorno
Copia el archivo `.env.example` a `.env` y completa con tus valores:

```bash
cp .env.example .env
```

**Variables requeridas:**

```env
# Base de Datos MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=ddsc_mods
DB_PORT=3306

# JWT
JWT_KEY=tu_clave_secreta_super_segura
ALGORITHM=HS256

# AWS S3
AWS_ACCESS_KEY_ID=tu_aws_access_key
AWS_SECRET_ACCESS_KEY=tu_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=tu-bucket-name
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la API

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

---

## Endpoints de la API

### 📚 Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 👤 Autenticación

### Login
```http
POST /users/login
Content-Type: application/json

{
  "username": "juan",
  "password": "tu_password_123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Usar el token:**
```http
GET /mod/all
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## 🎮 Mods

### Listar Mods (Público)
```http
GET /mod/all
```

### Obtener Mod Específico (Público)
```http
GET /mod/{mod_id}
```

### Crear Mod (Requiere Autenticación)
```http
POST /mod
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Mi Nuevo Mod",
  "description": "Descripción del mod",
  "slug": "mi-nuevo-mod",
  "status": "beta",
  "duration": "medium",
  "character": "monika",
  "dowload_pc": "https://...",
  "dowload_android": "https://..."
}
```

**Status válidos:** `under_development`, `beta`, `stable`, `legacy`, `abandoned`, `on_ice`, `archived`, `unknown`

**Duration válidos:** `very_short`, `short`, `medium`, `large`, `very_large`, `endless`, `unknown`

**Character válidos:** `sayori`, `monika`, `yuri`, `natsuki`, `mc`, `oc`

### Actualizar Mod (Requiere Autenticación EDITOR/OWNER)
```http
PUT /mod/{mod_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Nombre Actualizado",
  "description": "Nueva descripción",
  ...
}
```

### Eliminar Mod (Soft Delete, Requiere Autenticación EDITOR/OWNER)
```http
DELETE /mod/{mod_id}
Authorization: Bearer {token}
```

---

## 🖼️ Imágenes

### Obtener Imágenes de un Mod (Público)
```http
GET /images/mod/{mod_id}
```

### Obtener Imagen Específica (Público)
```http
GET /images/{image_id}
```

### Subir Imagen (Requiere Autenticación EDITOR/OWNER)
```http
POST /images
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- mod_id: 1
- image_type: logo
- file: [archivo de imagen]
```

**Image Types válidos:** `logo`, `main`, `screenshot`

**Características de procesamiento:**
- ✅ Validación de formato (JPEG, PNG, WebP, GIF)
- ✅ Validación de tamaño (máximo 10 MB)
- ✅ Redimensionamiento automático (máximo 2560x2560)
- ✅ Conversión automática a WebP
- ✅ Compresión (calidad 85)
- ✅ Subida a AWS S3
- ✅ URL pública retornada

**Response:**
```json
{
  "id": 1,
  "url": "https://tu-bucket.s3.us-east-1.amazonaws.com/mods/1/logo/...",
  "type": "logo",
  "mod_id": 1,
  "created_at": "2024-03-16T10:30:00",
  "updated_at": "2024-03-16T10:30:00",
  "created_by": "juan",
  "is_active": true
}
```

### Actualizar Imagen (Requiere Autenticación EDITOR/OWNER)
```http
PUT /images/{image_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://nueva-url.com",
  "type": "main"
}
```

### Eliminar Imagen (Soft Delete, Requiere Autenticación EDITOR/OWNER)
```http
DELETE /images/{image_id}
Authorization: Bearer {token}
```

---

## 🏷️ Géneros

### Listar Géneros (Público)
```http
GET /genres
```

### Obtener Género Específico (Público)
```http
GET /genres/{genre_id}
```

### Crear Género (Requiere Autenticación EDITOR/OWNER)
```http
POST /genres
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Psychological Horror"
}
```

### Actualizar Género (Requiere Autenticación EDITOR/OWNER)
```http
PUT /genres/{genre_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Horror"
}
```

### Eliminar Género (Soft Delete, Requiere Autenticación EDITOR/OWNER)
```http
DELETE /genres/{genre_id}
Authorization: Bearer {token}
```

---

## 👥 Usuarios

### Listar Usuarios (Requiere Autenticación)
```http
GET /users
Authorization: Bearer {token}
```

### Crear Usuario (Requiere Autenticación EDITOR/OWNER)
```http
POST /users
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "nuevo_usuario",
  "password": "password_segura",
  "role": "EDITOR",
  "logo": "https://...",
  "contact": "email@example.com"
}
```

**Roles válidos:** `OWNER`, `EDITOR`, `UPLOADER`

**Restricciones:**
- Solo OWNER/EDITOR pueden crear usuarios
- No se pueden crear usuarios con rol OWNER
- UPLOADER no puede crear otros usuarios

---

## 🔐 Roles y Permisos

### UPLOADER
- ✅ Ver mods (GET /mod/all)
- ✅ Ver imágenes (GET /images/mod/{id})
- ✅ Ver géneros (GET /genres)
- ✅ Crear mods (pero requieren aprobación, `is_active=False`)
- ❌ Editar mods
- ❌ Eliminar mods
- ❌ Crear usuarios
- ❌ Crear géneros

### EDITOR
- ✅ Ver todo (públicos)
- ✅ Crear mods (automáticamente aprobados, `is_active=True`)
- ✅ Editar mods
- ✅ Eliminar mods
- ✅ Crear/editar/eliminar imágenes
- ✅ Crear/editar/eliminar géneros
- ✅ Crear usuarios (solo EDITOR/UPLOADER, no OWNER)

### OWNER
- ✅ Acceso total

---

## 📊 Auditoría Automática

Todos los modelos que heredan de `TimestampMixin` tienen:

```json
{
  "id": 1,
  "name": "...",
  "created_at": "2024-03-16T10:30:00",
  "created_by": "juan",
  "updated_at": "2024-03-16T10:30:00",
  "updated_by": "juan",
  "deleted_at": null,
  "deleted_by": null,
  "is_active": true
}
```

**Notas:**
- `created_by` y `updated_by` se capturan automáticamente del token JWT
- Los registros nunca se borran (soft delete), solo se marcan como `is_active=False`
- Se registra quién hizo cada operación

---

## 🚀 Flujo Típico de Creación de Mod

```
1. Usuario hace login
   POST /users/login

2. Usuario crea un mod
   POST /mod
   → Si UPLOADER: is_active=False (requiere aprobación)
   → Si EDITOR: is_active=True

3. Usuario sube imágenes al mod
   POST /images (3 veces, para logo, main, screenshot)
   → Las imágenes se convierten a WebP automáticamente
   → Se suben a S3
   → Se retorna URL pública

4. Usuario actualiza el mod con info de géneros
   PUT /mod/{id}

5. Otros usuarios ven el mod público
   GET /mod/all
   GET /mod/{id}
   GET /images/mod/{id}
```

---

## 🐛 Códigos de Error Comunes

| Código | Significado |
|--------|-------------|
| 400 | Solicitud inválida (validación falló) |
| 401 | No autenticado (falta token) |
| 403 | No autorizado (permisos insuficientes) |
| 404 | Recurso no encontrado |
| 500 | Error del servidor |

---

## 📝 Notas Importantes

1. **Conversión de imágenes**: Automática a WebP (no es necesario procesarlas antes)
2. **URLs S3**: Públicas de lectura (ACL public-read)
3. **Soft delete**: Los registros se marcan como inactivos, no se borran realmente
4. **ContextVar**: Se usa para capturar automáticamente quién hace cada operación
5. **JWT**: Token válido por 48 horas

---

## 🔗 Recursos Útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [boto3 (AWS SDK)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Pillow (Image Processing)](https://pillow.readthedocs.io/)
