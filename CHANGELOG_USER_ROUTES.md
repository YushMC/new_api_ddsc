# Registro de Cambios - Rutas de Perfil de Usuario

Fecha: 16 de Marzo de 2025

## ✨ Nuevas Características

### 3 Nuevas Rutas para Gestionar Perfiles de Usuario

#### 1. Upload/Actualizar Logo (POST /users/{user_id}/logo)

**Descripción:** Permite a los usuarios subir o actualizar su logo a AWS S3.

**Características:**
- Conversión automática a WebP
- Redimensionamiento automático (máx 2560x2560px)
- Compresión automática (calidad 85)
- Eliminación automática del logo anterior
- Almacenamiento en AWS S3 con ACL public-read

**Formatos Soportados:** JPEG, PNG, WebP, GIF
**Tamaño Máximo:** 10 MB

**Autorización:**
- ✅ Usuario puede actualizar su propio logo
- ✅ OWNER puede actualizar logo de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden actualizar logos ajenos

---

#### 2. Actualizar Contraseña (PATCH /users/{user_id}/password)

**Descripción:** Permite cambiar la contraseña del usuario.

**Características:**
- Validación de contraseña actual
- Hash automático con bcrypt
- Límite de 72 bytes (especificación de bcrypt)
- Mínimo 6 caracteres

**Autorización:**
- ✅ Usuario puede cambiar su propia contraseña
- ✅ OWNER puede cambiar contraseña de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden cambiar contraseñas ajenas

---

#### 3. Actualizar Contacto (PATCH /users/{user_id}/contact)

**Descripción:** Permite actualizar el contacto/email del usuario.

**Características:**
- Validación de longitud (1-500 caracteres)
- Actualización instantánea en BD
- Sin validación específica de email (acepta cualquier contacto)

**Autorización:**
- ✅ Usuario puede actualizar su propio contacto
- ✅ OWNER puede actualizar contacto de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden actualizar contactos ajenos

---

## 📦 Cambios de Código

### Nuevos Esquemas (schemas/users.py)
- `UpdatePasswordRequest` - Validación de actualización de contraseña
- `UpdateContactRequest` - Validación de actualización de contacto
- `UpdateUserLogoResponse` - Respuesta de actualización de logo

### Nuevos Métodos en CRUD_USERS (services/users.py)
- `get_user_by_id(user_id)` - Obtener usuario por ID
- `update_user_logo(user_id, logo_url)` - Actualizar logo en BD
- `update_user_password(user_id, current_password, new_password)` - Actualizar contraseña
- `update_user_contact(user_id, contact)` - Actualizar contacto

### Nuevos Métodos en S3Manager (utils/s3_manager.py)
- `generate_user_logo_s3_key(user_id, filename)` - Generar clave única para logos
- `upload_user_logo(file_content, user_id, filename)` - Subir logo a S3

### Nuevas Rutas (routes/users.py)
- `POST /users/{user_id}/logo` - Subir/actualizar logo
- `PATCH /users/{user_id}/password` - Actualizar contraseña
- `PATCH /users/{user_id}/contact` - Actualizar contacto

---

## 📚 Documentación

### Archivos Actualizados
- **API_GUIDE.md** - Documentación de nuevas rutas
- **USER_ROUTES_EXAMPLES.md** - Ejemplos prácticos con curl, Python y JavaScript

### Ejemplos Incluidos
- ✅ Ejemplos con curl
- ✅ Ejemplos con Python (requests)
- ✅ Ejemplos con JavaScript (Fetch API)
- ✅ Solución de problemas
- ✅ Códigos de error

---

## 🔐 Normas de Seguridad

1. **Validación de Autorización:** Cada ruta verifica que el usuario tenga permisos
2. **Hash de Contraseñas:** Usando bcrypt (no plaintext)
3. **URLs Públicas:** ACL public-read solo para lectura en S3
4. **Eliminación Automática:** Logos anteriores se eliminan de S3
5. **Auditoría:** Se registra automáticamente quién hizo cada cambio

---

## 🧪 Pruebas Realizadas

✅ Compilación de archivos Python sin errores
✅ Rutas registradas correctamente en FastAPI
✅ Esquemas Pydantic validan correctamente
✅ Procesamiento de imágenes funciona
✅ Integración con AWS S3 testada
✅ Autorización y permisos verificados

---

## 📊 Commits Relacionados

```
a62627c docs: add comprehensive examples for new user profile routes
98bfef2 docs: update API_GUIDE with new user profile update routes
a1ce8e0 feat: add user profile update routes for logo, password, and contact
```

---

## 💡 Ejemplos de Uso Rápido

### Subir Logo
```bash
curl -X POST "http://localhost:8000/users/1/logo" \
  -H "Authorization: Bearer <token>" \
  -F "file=@logo.png"
```

### Actualizar Contraseña
```bash
curl -X PATCH "http://localhost:8000/users/1/password" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"old","new_password":"new"}'
```

### Actualizar Contacto
```bash
curl -X PATCH "http://localhost:8000/users/1/contact" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"contact":"nuevo@example.com"}'
```

---

## 🔄 Flujo Típico para Usuario

```
1. Login → Obtener token JWT
2. Subir logo → POST /users/{id}/logo
3. Actualizar contacto → PATCH /users/{id}/contact
4. Cambiar contraseña → PATCH /users/{id}/password (opcional)
```

---

## 🚀 Próximas Mejoras Opcionales

1. Agregar validación de email estricta (EmailStr)
2. Agregar endpoint para eliminar cuenta
3. Agregar endpoint para cambiar rol (solo OWNER)
4. Agregar rate limiting en uploads
5. Agregar compresión gzip en S3

---

## ⚙️ Requisitos de Ambiente

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=tu_aws_access_key
AWS_SECRET_ACCESS_KEY=tu_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=tu-bucket-name

# JWT
JWT_KEY=tu_clave_secreta
ALGORITHM=HS256
```

---

## 📝 Notas Finales

- Todas las rutas requieren autenticación JWT válida
- Los tokens expiran después de 48 horas
- Los logos se eliminan automáticamente de S3 al actualizar
- Las contraseñas son sensibles a mayúsculas/minúsculas
- Los usuarios no se eliminan (soft delete), solo se marcan como inactivos

---

**Versión:** 1.0
**API Version:** 1.0.0
**Fecha de Implementación:** 16 de Marzo de 2025
