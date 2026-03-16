# Ejemplos de Uso - Nuevas Rutas de Usuarios

Este documento contiene ejemplos prácticos para usar las nuevas rutas de perfil de usuario.

## 🚀 Flujo Típico

### 1. Bootstrap - Crear Primer Usuario OWNER

```bash
curl -X POST "http://localhost:8000/users/bootstrap" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin",
    "password": "password123",
    "contact": "admin@example.com"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "admin",
    "role": "OWNER",
    "logo": null,
    "contact": "admin@example.com",
    "is_active": true
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "Usuario OWNER 'admin' creado exitosamente",
  "warning": "Esta ruta (POST /users/bootstrap) ya no estará disponible para futuras solicitudes..."
}
```

Guarda el `access_token` para usarlo en las siguientes solicitudes.

---

### 2. Login - Obtener Token

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. Crear Nuevo Usuario

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "editor_user",
    "password": "securepass456",
    "role": "EDITOR",
    "contact": "editor@example.com"
  }'
```

**Response:**
```json
{
  "id": 2,
  "name": "editor_user",
  "role": "EDITOR",
  "logo": null,
  "contact": "editor@example.com",
  "is_active": true
}
```

---

### 4. Subir/Actualizar Logo de Usuario

#### Opción A: Usando curl

```bash
curl -X POST "http://localhost:8000/users/1/logo" \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@/path/to/logo.png"
```

#### Opción B: Usando Python

```python
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {token}"}

with open("logo.png", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/users/1/logo",
        headers=headers,
        files=files
    )

print(response.json())
```

**Response:**
```json
{
  "id": 1,
  "name": "admin",
  "logo": "https://tu-bucket.s3.us-east-1.amazonaws.com/users/1/logo/20240316_120530_a1b2c3d4_logo.webp",
  "message": "Logo actualizado exitosamente"
}
```

#### Opción C: Usando JavaScript/Fetch

```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
const fileInput = document.getElementById("logoInput");
const file = fileInput.files[0];

const formData = new FormData();
formData.append("file", file);

fetch("http://localhost:8000/users/1/logo", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`
  },
  body: formData
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

---

### 5. Actualizar Contraseña

```bash
curl -X PATCH "http://localhost:8000/users/1/password" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "password123",
    "new_password": "newpassword456"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "admin",
  "role": "OWNER",
  "logo": "https://tu-bucket.s3.us-east-1.amazonaws.com/users/1/logo/...",
  "contact": "admin@example.com",
  "is_active": true
}
```

**Posibles Errores:**

```json
{
  "detail": "Contraseña actual incorrecta"
}
```

---

### 6. Actualizar Contacto

```bash
curl -X PATCH "http://localhost:8000/users/1/contact" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "nuevo_email@example.com"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "admin",
  "role": "OWNER",
  "logo": "https://tu-bucket.s3.us-east-1.amazonaws.com/users/1/logo/...",
  "contact": "nuevo_email@example.com",
  "is_active": true
}
```

---

### 7. Listar Todos los Usuarios

```bash
curl -X GET "http://localhost:8000/users" \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "admin",
    "role": "OWNER",
    "logo": "https://...",
    "contact": "admin@example.com",
    "is_active": true
  },
  {
    "id": 2,
    "name": "editor_user",
    "role": "EDITOR",
    "logo": null,
    "contact": "editor@example.com",
    "is_active": true
  }
]
```

---

## 🔐 Reglas de Autorización

### Logo Upload (POST /users/{user_id}/logo)
- ✅ El usuario puede subir/actualizar su propio logo
- ✅ OWNER puede subir/actualizar el logo de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden actualizar logos de otros usuarios

### Password Update (PATCH /users/{user_id}/password)
- ✅ El usuario puede cambiar su propia contraseña
- ✅ OWNER puede cambiar la contraseña de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden cambiar contraseñas de otros usuarios
- ⚠️ Se requiere la contraseña actual para validación

### Contact Update (PATCH /users/{user_id}/contact)
- ✅ El usuario puede actualizar su propio contacto
- ✅ OWNER puede actualizar el contacto de cualquier usuario
- ❌ EDITOR/UPLOADER no pueden actualizar contactos de otros usuarios

---

## 📋 Validaciones

### Logo Upload
- ✅ Formatos soportados: JPEG, PNG, WebP, GIF
- ✅ Tamaño máximo: 10 MB
- ✅ Procesamiento automático:
  - Redimensionamiento a máx 2560x2560 píxeles
  - Conversión a WebP
  - Compresión (calidad 85)
  - Almacenamiento en AWS S3

### Password Update
- ✅ Mínimo 6 caracteres
- ✅ Se valida contraseña actual
- ✅ Hash con bcrypt (automático)

### Contact Update
- ✅ Máximo 500 caracteres
- ✅ Mínimo 1 carácter

---

## 🔧 Variables de Entorno Requeridas

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=tu_aws_access_key
AWS_SECRET_ACCESS_KEY=tu_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=tu-bucket-name

# JWT
JWT_KEY=tu_clave_secreta_super_segura
ALGORITHM=HS256
```

---

## 💡 Notas Importantes

1. **Expiración del Token**: Los tokens JWT tienen validez de 48 horas
2. **Eliminación de Logo Anterior**: Al actualizar el logo, se elimina automáticamente el archivo anterior de S3
3. **URLs Públicas**: Los logos se almacenan con ACL `public-read` en S3
4. **Soft Delete**: Los usuarios no se eliminan, solo se marcan como inactivos
5. **Auditoría Automática**: Se registra automáticamente quién hizo cada cambio

---

## 🐛 Solución de Problemas

### "Token inválido"
- Verifica que el token no haya expirado (48 horas)
- Comprueba que el encabezado sea: `Authorization: Bearer <token>`
- No incluyas comillas extras alrededor del token

### "No autorizado para actualizar este logo"
- Verifica que seas el dueño del perfil o OWNER
- Comprueba el `user_id` en la URL

### "Contraseña actual incorrecta"
- Asegúrate de escribir la contraseña actual correctamente
- Las contraseñas son sensibles a mayúsculas/minúsculas

### "Usuario no encontrado"
- Comprueba que el `user_id` existe en la base de datos
- Verifica que el usuario esté activo (`is_active=true`)

---

## 📊 Estructura de Respuesta Estándar

### Success Response
```json
{
  "id": 1,
  "name": "usuario",
  "role": "OWNER",
  "logo": "https://...",
  "contact": "email@example.com",
  "is_active": true
}
```

### Error Response
```json
{
  "detail": "Descripción del error"
}
```

Con código HTTP:
- `200 OK`: Éxito
- `400 Bad Request`: Validación fallida
- `401 Unauthorized`: Token inválido/expirado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no existe
- `500 Internal Server Error`: Error del servidor
