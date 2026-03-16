# 🎮 DDLC Mods API

Una API REST completa y moderna para gestionar mods de **Doki Doki Literature Club (DDLC)** con características empresariales como autenticación JWT, control de roles, carga de imágenes a AWS S3 con conversión WebP, y notificaciones automáticas a Discord.

![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-009485?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-CC342D?style=flat-square)
![MySQL](https://img.shields.io/badge/MySQL-8.0-00758f?style=flat-square&logo=mysql)
![AWS S3](https://img.shields.io/badge/AWS-S3-FF9900?style=flat-square&logo=amazonaws)
![Discord](https://img.shields.io/badge/Discord-Webhooks-5865F2?style=flat-square&logo=discord)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Stack Tecnológico](#-stack-tecnológico)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Autenticación y Roles](#-autenticación-y-roles)
- [Características Avanzadas](#-características-avanzadas)
- [Documentación Adicional](#-documentación-adicional)

---

## ✨ Características

### 🔐 Seguridad
- ✅ **Autenticación JWT** con expiración de 48 horas
- ✅ **Control de Roles** (OWNER, EDITOR, UPLOADER)
- ✅ **Autorización por Endpoint** - Permisos granulares
- ✅ **Contexto de Usuario Automático** - Auditoría sin parámetros adicionales
- ✅ **Soft Delete** - Datos nunca se pierden, solo se marcan inactivos
- ✅ **Validación de Entrada** - Pydantic para todos los datos

### 📊 Auditoría y Trazabilidad
- ✅ **Timestamps Automáticos** - created_at, updated_at, deleted_at
- ✅ **Tracking de Usuario** - created_by, updated_by, deleted_by
- ✅ **ContextVar** - Aislamiento seguro de contexto por request
- ✅ **Historial Completo** - Todos los cambios registrados

### 🖼️ Gestión de Imágenes
- ✅ **Carga a AWS S3** - Almacenamiento escalable en la nube
- ✅ **Conversión Automática a WebP** - Optimización de tamaño
- ✅ **Redimensionamiento Inteligente** - Máximo 2560x2560
- ✅ **Compresión** - Calidad 85 para balance óptimo
- ✅ **URLs Públicas** - Acceso directo a imágenes

### 🤖 Notificaciones
- ✅ **Webhooks de Discord** - Notificaciones en tiempo real
- ✅ **Embeds Coloreados** - Rojo (pendiente), Verde (aprobado), Naranja (actualizado)
- ✅ **Detección Automática de Cambios** - Solo notifica si hay cambios
- ✅ **Aprobación de Mods** - Notificación especial cuando se aprueban
- ✅ **Sin Bloqueo** - Usa asyncio para no interrumpir la API

### 📱 API Moderna
- ✅ **Documentación Interactiva** - Swagger UI y ReDoc
- ✅ **CRUD Completo** - Mods, Usuarios, Géneros, Imágenes
- ✅ **Paginación** - Soporte para skip/limit
- ✅ **Filtrado** - Consultas optimizadas
- ✅ **Respuestas Consistentes** - Schemas validados

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI 0.135.1** - Framework web async
- **SQLAlchemy 2.0** - ORM para base de datos
- **Pydantic 2.12** - Validación de datos

### Base de Datos
- **MySQL 8.0** - Base de datos relacional
- **PyMySQL** - Driver para MySQL

### Autenticación
- **python-jose** - JWT tokens
- **passlib** - Hashing de contraseñas
- **bcrypt** - Algoritmo de hash seguro

### Cloud & Almacenamiento
- **boto3** - AWS SDK
- **AWS S3** - Almacenamiento de imágenes

### Procesamiento de Imágenes
- **Pillow 10.1** - Manipulación de imágenes

### Notificaciones
- **aiohttp** - HTTP asincrónico
- **Discord Webhooks** - Notificaciones en Discord

### Server & Utilities
- **Uvicorn 0.41** - ASGI server
- **python-dotenv** - Variables de entorno
- **uvloop** - Event loop optimizado

---

## 📦 Requisitos

- **Python 3.8+**
- **MySQL 8.0+**
- **AWS S3 Account** (opcional, para imágenes)
- **Discord Server** (opcional, para notificaciones)

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/ddlc-mods-api.git
cd ddlc-mods-api
```

### 2. Crear Entorno Virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=ddsc_mods
DB_PORT=3306

# JWT
JWT_KEY=tu_clave_secreta_super_segura_cambiar_en_produccion
ALGORITHM=HS256

# AWS S3 (opcional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Discord (opcional)
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...
FRONTEND_BASE_URL=https://tudominio.com
```

### 5. Ejecutar la API

```bash
uvicorn main:app --reload
```

La API estará disponible en: **http://localhost:8000**

Documentación interactiva:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚙️ Configuración

### Base de Datos MySQL

```bash
# Crear base de datos
CREATE DATABASE ddsc_mods;

# Las tablas se crean automáticamente al iniciar la API
```

### AWS S3 (Opcional)

1. Crear bucket en AWS S3
2. Configurar política de acceso público (read)
3. Obtener credenciales de acceso
4. Agregar a `.env`

Ver: [Documentación de AWS S3](https://docs.aws.amazon.com/s3/)

### Discord Webhooks (Opcional)

1. Crear webhook en tu servidor Discord
2. Copiar URL del webhook
3. Agregar a `.env`

Instrucciones completas en: [DISCORD_SETUP.md](./DISCORD_SETUP.md)

---

## 📖 Uso

### 1. Crear Usuario

```bash
# Primero necesitas un usuario OWNER para crear otros
# Crear manualmente en la BD o usar endpoint (con token existente)

curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nuevo_usuario",
    "password": "password_segura",
    "role": "EDITOR",
    "contact": "email@example.com"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "password": "password123"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer"
# }
```

### 3. Crear Mod

```bash
curl -X POST http://localhost:8000/mod \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Nuevo Mod",
    "description": "Una descripción completa",
    "slug": "mi-nuevo-mod",
    "status": "beta",
    "duration": "medium",
    "character": "monika",
    "dowload_pc": "https://link-descarga.com",
    "dowload_android": "https://link-descarga-mobile.com"
  }'
```

### 4. Subir Imágenes

#### 4.1 Subir Logo (1 imagen)
```bash
curl -X POST http://localhost:8000/images/logo/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@logo.jpg"
```

#### 4.2 Subir Imagen Main (1 imagen)
```bash
curl -X POST http://localhost:8000/images/main/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@main.jpg"
```

#### 4.3 Subir Screenshots (máximo 4 imágenes)
```bash
# Screenshot 1
curl -X POST http://localhost:8000/images/screenshots/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@screenshot1.jpg"

# Screenshot 2
curl -X POST http://localhost:8000/images/screenshots/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@screenshot2.jpg"

# ... máximo 4
```

### 5. Listar Mods (Público)

```bash
# Sin token requerido
curl http://localhost:8000/mod/all
```

### 6. Obtener Detalles de Mod (Público)

```bash
curl http://localhost:8000/mod/1
```

---

## 🏗️ Estructura del Proyecto

```
ddlc-mods-api/
├── main.py                          # Entrada principal de la API
├── requirements.txt                 # Dependencias Python
├── .env.example                     # Plantilla de variables de entorno
├── README.md                        # Este archivo
├── API_GUIDE.md                     # Guía completa de endpoints
├── DISCORD_SETUP.md                 # Configuración de Discord
│
├── src/
│   ├── __init__.py
│   │
│   ├── conf/                        # Configuración
│   │   ├── database.py              # SQLAlchemy, MySQL connection
│   │   ├── all_keys.py              # Constantes de env keys
│   │   ├── context.py               # ContextVar para auditoría
│   │   └── discord_config.py        # Configuración de Discord
│   │
│   ├── middleware/                  # Middlewares
│   │   ├── jwt.py                   # Extracción de token JWT
│   │   └── context.py               # Inyección de contexto de usuario
│   │
│   ├── models/                      # Modelos SQLAlchemy (ORM)
│   │   ├── mods.py                  # Mod model
│   │   ├── users.py                 # User model
│   │   ├── generos.py               # Genre model
│   │   ├── imagen.py                # Image model
│   │   ├── relations.py             # Relaciones M:M
│   │   ├── timestamp.py             # TimestampMixin para auditoría
│   │   └── enums.py                 # Enums de estados
│   │
│   ├── schemas/                     # Schemas Pydantic (validación)
│   │   ├── mods.py                  # ModBase, ModComplete
│   │   ├── users.py                 # UserCreate, UserLogin, UserResponse
│   │   ├── generos.py               # GenreCreate, GenreResponse
│   │   ├── imagenes.py              # ImageCreate, ImageResponse
│   │   └── timestamp.py             # TimestampBase
│   │
│   ├── routes/                      # Routers de FastAPI
│   │   ├── mods.py                  # GET /mod/*, POST/PUT/DELETE /mod
│   │   ├── users.py                 # POST /users/login, GET/POST /users
│   │   ├── generos.py               # GET/POST/PUT/DELETE /genres
│   │   └── imagenes.py              # GET/POST/PUT/DELETE /images
│   │
│   ├── services/                    # Lógica de negocio (CRUD)
│   │   ├── mods.py                  # CRUD_MOD service
│   │   ├── users.py                 # CRUD_USERS service
│   │   ├── generos.py               # CRUD_GENRE service
│   │   ├── imagenes.py              # CRUD_IMAGE service
│   │   └── token.py                 # TokenUser parser
│   │
│   └── utils/                       # Utilidades
│       ├── hash.py                  # Hash de contraseñas
│       ├── jwt.py                   # Creación/validación de JWT
│       ├── image_processor.py       # Procesamiento de imágenes
│       ├── s3_manager.py            # Gestión de AWS S3
│       └── discord_notifier.py      # Notificaciones a Discord
│
└── venv/                            # Entorno virtual (ignorado)
```

---

## 🔌 API Endpoints

### Autenticación (`/users`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/users/login` | Autenticar usuario | ❌ |
| GET | `/users` | Listar usuarios | ✅ |
| POST | `/users` | Crear usuario | ✅ (EDITOR/OWNER) |

### Mods (`/mod`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/mod/all` | Listar mods activos | ❌ |
| GET | `/mod/{id}` | Obtener mod específico | ❌ |
| POST | `/mod` | Crear nuevo mod | ✅ |
| PUT | `/mod/{id}` | Actualizar mod | ✅ (EDITOR/OWNER) |
| DELETE | `/mod/{id}` | Eliminar mod (soft delete) | ✅ (EDITOR/OWNER) |

### Imágenes (`/images`)

#### Rutas Genéricas
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/images/mod/{mod_id}` | Listar imágenes de mod | ❌ |
| GET | `/images/{id}` | Obtener imagen específica | ❌ |
| DELETE | `/images/{id}` | Eliminar imagen (soft delete) | ✅ (EDITOR/OWNER) |

#### Rutas Específicas por Tipo
| Método | Endpoint | Descripción | Límite | Auth |
|--------|----------|-------------|--------|------|
| POST | `/images/logo/{mod_id}` | Subir logo | 1 imagen | ✅ (EDITOR/OWNER) |
| POST | `/images/main/{mod_id}` | Subir imagen main | 1 imagen | ✅ (EDITOR/OWNER) |
| POST | `/images/screenshots/{mod_id}` | Subir screenshot | Máx 4 | ✅ (EDITOR/OWNER) |

### Géneros (`/genres`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/genres` | Listar géneros | ❌ |
| GET | `/genres/{id}` | Obtener género específico | ❌ |
| POST | `/genres` | Crear género | ✅ (EDITOR/OWNER) |
| PUT | `/genres/{id}` | Actualizar género | ✅ (EDITOR/OWNER) |
| DELETE | `/genres/{id}` | Eliminar género | ✅ (EDITOR/OWNER) |

---

## 🔐 Autenticación y Roles

### Obtener Token

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "juan", "password": "password123"}'
```

### Usar Token en Requests

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/mod
```

### Roles y Permisos

#### 👤 UPLOADER
- ✅ Ver mods (públicos)
- ✅ Ver imágenes (públicas)
- ✅ Crear mods (requieren aprobación, `is_active=False`)
- ❌ Editar mods
- ❌ Eliminar mods
- ❌ Crear usuarios
- ❌ Crear géneros

#### ✏️ EDITOR
- ✅ Ver todo (públicos)
- ✅ Crear mods (automáticamente aprobados)
- ✅ Editar/Eliminar mods
- ✅ Crear/Editar/Eliminar imágenes
- ✅ Crear/Editar/Eliminar géneros
- ✅ Crear usuarios (solo EDITOR/UPLOADER)

#### 👑 OWNER
- ✅ Acceso total a todos los recursos

---

## 🚀 Características Avanzadas

### 1. Auditoría Automática

Todos los modelos tienen estos campos:

```json
{
  "created_at": "2024-03-16T10:30:00Z",
  "created_by": "juan",
  "updated_at": "2024-03-16T10:30:00Z",
  "updated_by": "juan",
  "deleted_at": null,
  "deleted_by": null,
  "is_active": true
}
```

### 2. Soft Delete

Los datos nunca se eliminan realmente, solo se marcan como inactivos:

```python
# DELETE /mod/1
# No elimina, solo marca:
mod.is_active = False
mod.deleted_at = datetime.now()
mod.deleted_by = "usuario"
```

### 3. Carga de Imágenes a S3

Cada tipo de imagen tiene su propia ruta con validaciones específicas:

#### Logo (1 imagen máximo)
```bash
# Proceso automático:
# 1. Validación (formato, tamaño)
# 2. Redimensionamiento
# 3. Conversión a WebP
# 4. Compresión
# 5. Subida a S3
# 6. Retorna URL pública

curl -X POST http://localhost:8000/images/logo/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@logo.jpg"

# Response:
# {
#   "url": "https://bucket.s3.region.amazonaws.com/mods/1/logo/...",
#   "type": "logo",
#   "mod_id": 1,
#   "created_at": "2024-03-16T10:30:00Z",
#   "created_by": "usuario"
# }
```

#### Imagen Main (1 imagen máximo)
```bash
curl -X POST http://localhost:8000/images/main/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@main.jpg"
```

#### Screenshots (máximo 4 imágenes)
```bash
# Puedes subir hasta 4 screenshots
curl -X POST http://localhost:8000/images/screenshots/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@screenshot.jpg"

# Si intentas subir una 5ta, recibirás error 409
```

### 4. Notificaciones Discord

Automáticamente se envían notificaciones cuando:

- ✅ Se crea un mod
- ✅ Se actualiza un mod
- ✅ Se aprueba un mod

Colores por tipo:
- 🔴 **Rojo**: Mod pendiente aprobación (UPLOADER)
- 🟢 **Verde**: Mod aprobado automáticamente (EDITOR)
- 🟠 **Naranja**: Mod actualizado
- 🟢 **Verde Oscuro**: Mod aprobado por admin

---

## 📚 Documentación Adicional

- **[API_GUIDE.md](./API_GUIDE.md)** - Guía completa de uso de endpoints
- **[DISCORD_SETUP.md](./DISCORD_SETUP.md)** - Configuración de notificaciones Discord
- **[Swagger UI](http://localhost:8000/docs)** - Documentación interactiva (cuando está corriendo)
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentación oficial de FastAPI

---

## 🧪 Testing

### Test Manual con cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "juan", "password": "password"}' | jq -r '.access_token')

# 2. Crear mod
curl -X POST http://localhost:8000/mod \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Test", "slug": "test", "status": "beta", "duration": "medium", "character": "monika"}'

# 3. Listar mods
curl http://localhost:8000/mod/all
```

### Test en Swagger UI

1. Accede a http://localhost:8000/docs
2. Click en "Authorize"
3. Ingresa tu token
4. Prueba los endpoints interactivamente

---

## 🐛 Troubleshooting

### Error: "No se puede conectar a MySQL"

```bash
# Verificar que MySQL está corriendo
mysql -h localhost -u root -p

# Verificar credenciales en .env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
```

### Error: "Webhook inválido"

```bash
# Verificar DISCORD_WEBHOOK_URL
# Copiar exactamente desde Discord sin espacios
echo $DISCORD_WEBHOOK_URL

# Si está vacío, Discord está deshabilitado (normal)
```

### Error: "Credenciales AWS inválidas"

```bash
# Verificar credenciales en .env
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=yyy

# Si está vacío, S3 está deshabilitado (normal)
```

---

## 📝 Notas Importantes

- **Soft Delete**: Los registros nunca se eliminan realmente
- **JWT**: Token válido por 48 horas
- **Async**: Las notificaciones Discord son asincrónicas (no bloquean la API)
- **S3 Público**: Las imágenes se suben con ACL público de lectura
- **WebP**: Todas las imágenes se convierten a WebP automáticamente
- **ContextVar**: Se usa para auditoría automática sin parámetros adicionales

---

## 🔄 Flujo Típico de Creación de Mod

```
1. Usuario hace login
   POST /users/login → Token JWT

2. Usuario crea mod
   POST /mod → Según rol:
     - UPLOADER: is_active=False (necesita aprobación)
     - EDITOR: is_active=True (automáticamente aprobado)
   
   → Discord notifica (color rojo/verde según rol)

3. Usuario sube imágenes (3 rutas separadas)
   
   a) Logo (1 imagen obligatoria)
      POST /images/logo/{mod_id} → Rechaza si ya existe logo
   
   b) Imagen Main (1 imagen obligatoria)
      POST /images/main/{mod_id} → Rechaza si ya existe main
   
   c) Screenshots (máximo 4 imágenes)
      POST /images/screenshots/{mod_id} (repetir hasta 4 veces)
      POST /images/screenshots/{mod_id} 
      POST /images/screenshots/{mod_id} 
      POST /images/screenshots/{mod_id}
      → Rechaza si intenta una 5ta imagen
   
   → Cada imagen se procesa: valida → redimensiona → convierte a WebP → sube a S3

4. Admin aprueba mod (si es UPLOADER)
   PUT /mod/{id} → required_revision: False
   → Discord notifica (verde oscuro - aprobado)

5. Otros usuarios ven el mod público
   GET /mod/all → Solo mods con is_active=True
```

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

## 👥 Contribuidores

- Creado como parte del proyecto DDSC Mods API

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa [API_GUIDE.md](./API_GUIDE.md) y [DISCORD_SETUP.md](./DISCORD_SETUP.md)
2. Revisa los logs de la API
3. Consulta la documentación interactiva en Swagger UI

---

## 🎯 Roadmap Futuro

- [ ] Notificaciones por email
- [ ] Sistema de ratings/comentarios
- [ ] Búsqueda avanzada de mods
- [ ] Estadísticas y reportes
- [ ] Sistema de etiquetas
- [ ] Versioning de mods
- [ ] Integración con GitHub
- [ ] CLI para administración

---

**Desarrollado con ❤️ usando FastAPI**
