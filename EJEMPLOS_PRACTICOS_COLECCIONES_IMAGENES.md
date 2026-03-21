# Ejemplos Prácticos: cURL y Código

## EJEMPLOS COLECCIONES

### 1. Crear colección
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Mod Horror Clásico",
    "description": "Colección de mods de terror clásicos"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "response": "created",
  "message": "Colección creada exitosamente",
  "data": {
    "resource": {
      "id": 1,
      "name": "Mod Horror Clásico",
      "description": "Colección de mods de terror clásicos"
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

### 2. Actualizar colección
```bash
curl -X PUT http://localhost:8000/collections/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Horror Moderno",
    "description": "Mods de horror contemporáneo"
  }'
```

**Respuesta exitosa (200):**
```json
{
  "response": "updated",
  "message": "Colección actualizada exitosamente",
  "data": {
    "resource": {
      "id": 1,
      "name": "Horror Moderno",
      "description": "Mods de horror contemporáneo"
    },
    "info": {
      "created_at": "2026-03-20T15:30:45.123456Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:35:10.654321Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  }
}
```

### 3. Eliminar colección (soft delete)
```bash
curl -X DELETE http://localhost:8000/collections/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "response": "deleted",
  "message": "Colección eliminada exitosamente",
  "data": null
}
```

### 4. Listar colecciones activas (público)
```bash
curl -X GET "http://localhost:8000/collections?skip=0&limit=10"
```

**Respuesta exitosa (200):**
```json
{
  "response": "success",
  "message": "Colecciones obtenidas exitosamente",
  "data": [
    {
      "id": 1,
      "name": "Horror Moderno",
      "description": "Mods de horror contemporáneo",
      "created_at": "2026-03-20T15:30:45.123456Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:35:10.654321Z",
      "updated_by": "admin_user",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Mods Românticos",
      "description": "Colección de mods románticos",
      "created_at": "2026-03-20T16:00:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T16:00:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  ]
}
```

### 5. Reactivar colección eliminada
```bash
curl -X POST http://localhost:8000/collections/1/reactivate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta exitosa (200):** Misma estructura que actualizar

---

## EJEMPLOS MODS-COLECCIONES

### 1. Agregar mod a colección
```bash
curl -X POST http://localhost:8000/mods-collections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "mod_id": 5,
    "collection_id": 1
  }'
```

**Respuesta exitosa (201):**
```json
{
  "response": "created",
  "message": "Mod agregado a colección exitosamente",
  "data": {
    "resource": {
      "id": 10,
      "mod_id": 5,
      "collection_id": 1
    },
    "info": {
      "created_at": "2026-03-20T15:40:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:40:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  }
}
```

### 2. Obtener mods de una colección
```bash
curl -X GET http://localhost:8000/mods-collections/collection/1
```

**Respuesta exitosa (200):**
```json
{
  "response": "success",
  "message": "Mods de la colección obtenidos exitosamente",
  "data": [
    {
      "id": 10,
      "mod_id": 5,
      "collection_id": 1,
      "created_at": "2026-03-20T15:40:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:40:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    },
    {
      "id": 11,
      "mod_id": 8,
      "collection_id": 1,
      "created_at": "2026-03-20T15:42:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:42:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  ]
}
```

### 3. Remover mod de colección
```bash
curl -X DELETE http://localhost:8000/mods-collections/10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "response": "deleted",
  "message": "Mod removido de colección exitosamente",
  "data": null
}
```

---

## EJEMPLOS IMÁGENES

### 1. Subir logo
```bash
curl -X POST http://localhost:8000/images/logo/5 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/logo.png"
```

**Respuesta exitosa (201):**
```json
{
  "response": "created",
  "message": "Logo subido exitosamente",
  "data": {
    "resource": {
      "id": 1,
      "url": "https://s3.amazonaws.com/ddsc-mods/mod_5/logo/logo_20260320_153045.webp",
      "type": "logo",
      "mod_id": 5
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

**Error si ya existe (409):**
```json
{
  "response": "error",
  "message": "Ya existe un logo para este mod. Usa DELETE para reemplazarlo.",
  "data": null
}
```

### 2. Actualizar logo (reemplazar)
```bash
curl -X PUT http://localhost:8000/images/logo/5 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/new_logo.jpg"
```

**Respuesta exitosa (200):**
```json
{
  "response": "updated",
  "message": "Logo actualizado exitosamente",
  "data": {
    "resource": {
      "id": 1,
      "url": "https://s3.amazonaws.com/ddsc-mods/mod_5/logo/logo_20260320_154010.webp",
      "type": "logo",
      "mod_id": 5
    },
    "info": {
      "created_at": "2026-03-20T15:30:45.123456Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:40:10.654321Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  }
}
```

### 3. Subir screenshot
```bash
curl -X POST http://localhost:8000/images/screenshots/5 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/screenshot1.png"
```

**Respuesta exitosa (201):** Similar a logo

**Error si ya tiene 4 screenshots (409):**
```json
{
  "response": "error",
  "message": "Este mod ya tiene 4 screenshots (máximo 4). Usa DELETE para reemplazar uno.",
  "data": null
}
```

### 4. Actualizar screenshot específico
```bash
curl -X PUT http://localhost:8000/images/screenshots/3 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/new_screenshot.png"
```

**Respuesta exitosa (200):** Similar a logo actualizado

### 5. Obtener imágenes de un mod
```bash
curl -X GET http://localhost:8000/images/mod/5
```

**Respuesta exitosa (200):**
```json
{
  "response": "success",
  "message": "Imágenes obtenidas exitosamente",
  "data": [
    {
      "id": 1,
      "url": "https://s3.amazonaws.com/ddsc-mods/mod_5/logo/...",
      "type": "logo",
      "mod_id": 5,
      "created_at": "2026-03-20T15:30:45.123456Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:40:10.654321Z",
      "updated_by": "admin_user",
      "is_active": true
    },
    {
      "id": 2,
      "url": "https://s3.amazonaws.com/ddsc-mods/mod_5/main/...",
      "type": "main",
      "mod_id": 5,
      "created_at": "2026-03-20T15:31:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:31:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    },
    {
      "id": 3,
      "url": "https://s3.amazonaws.com/ddsc-mods/mod_5/screenshot/...",
      "type": "screenshot",
      "mod_id": 5,
      "created_at": "2026-03-20T15:32:00.000000Z",
      "created_by": "admin_user",
      "updated_at": "2026-03-20T15:32:00.000000Z",
      "updated_by": "admin_user",
      "is_active": true
    }
  ]
}
```

### 6. Eliminar imagen
```bash
curl -X DELETE http://localhost:8000/images/3 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "response": "deleted",
  "message": "Imagen eliminada exitosamente",
  "data": null
}
```

---

## CÓDIGO PYTHON (requests)

### Cliente para Collections

```python
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token_here"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

class CollectionsClient:
    @staticmethod
    def create(name: str, description: str = None) -> dict:
        """Crear colección"""
        data = {"name": name}
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{BASE_URL}/collections",
            headers=HEADERS,
            json=data
        )
        return response.json()
    
    @staticmethod
    def update(collection_id: int, name: str = None, description: str = None) -> dict:
        """Actualizar colección"""
        data = {}
        if name:
            data["name"] = name
        if description is not None:
            data["description"] = description
        
        response = requests.put(
            f"{BASE_URL}/collections/{collection_id}",
            headers=HEADERS,
            json=data
        )
        return response.json()
    
    @staticmethod
    def delete(collection_id: int) -> dict:
        """Eliminar colección (soft delete)"""
        response = requests.delete(
            f"{BASE_URL}/collections/{collection_id}",
            headers=HEADERS
        )
        return response.json()
    
    @staticmethod
    def list(skip: int = 0, limit: int = 20) -> dict:
        """Listar colecciones activas"""
        response = requests.get(
            f"{BASE_URL}/collections",
            params={"skip": skip, "limit": limit}
        )
        return response.json()
    
    @staticmethod
    def get(collection_id: int) -> dict:
        """Obtener colección específica"""
        response = requests.get(
            f"{BASE_URL}/collections/{collection_id}"
        )
        return response.json()
    
    @staticmethod
    def reactivate(collection_id: int) -> dict:
        """Reactivar colección"""
        response = requests.post(
            f"{BASE_URL}/collections/{collection_id}/reactivate",
            headers=HEADERS
        )
        return response.json()

# Uso
if __name__ == "__main__":
    # Crear
    result = CollectionsClient.create(
        "Mods Románticos",
        "Colección de mods románticos"
    )
    print("Crear:", json.dumps(result, indent=2))
    
    collection_id = result['data']['resource']['id']
    
    # Listar
    result = CollectionsClient.list()
    print("Listar:", json.dumps(result, indent=2))
    
    # Actualizar
    result = CollectionsClient.update(
        collection_id,
        name="Mods Románticos Actualizados"
    )
    print("Actualizar:", json.dumps(result, indent=2))
    
    # Eliminar
    result = CollectionsClient.delete(collection_id)
    print("Eliminar:", json.dumps(result, indent=2))
    
    # Reactivar
    result = CollectionsClient.reactivate(collection_id)
    print("Reactivar:", json.dumps(result, indent=2))
```

### Cliente para Imágenes

```python
import requests
from pathlib import Path

class ImagesClient:
    @staticmethod
    def upload_logo(mod_id: int, file_path: str, token: str) -> dict:
        """Subir logo"""
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/images/logo/{mod_id}",
                headers=headers,
                files=files
            )
        return response.json()
    
    @staticmethod
    def upload_main(mod_id: int, file_path: str, token: str) -> dict:
        """Subir imagen main"""
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/images/main/{mod_id}",
                headers=headers,
                files=files
            )
        return response.json()
    
    @staticmethod
    def upload_screenshot(mod_id: int, file_path: str, token: str) -> dict:
        """Subir screenshot"""
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/images/screenshots/{mod_id}",
                headers=headers,
                files=files
            )
        return response.json()
    
    @staticmethod
    def get_images(mod_id: int) -> dict:
        """Obtener imágenes de un mod"""
        response = requests.get(f"{BASE_URL}/images/mod/{mod_id}")
        return response.json()
    
    @staticmethod
    def delete_image(image_id: int, token: str) -> dict:
        """Eliminar imagen"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f"{BASE_URL}/images/{image_id}",
            headers=headers
        )
        return response.json()

# Uso
if __name__ == "__main__":
    token = "your_jwt_token_here"
    
    # Subir logo
    result = ImagesClient.upload_logo(
        mod_id=5,
        file_path="/path/to/logo.png",
        token=token
    )
    print("Logo subido:", json.dumps(result, indent=2))
    
    # Obtener imágenes
    result = ImagesClient.get_images(mod_id=5)
    print("Imágenes del mod:", json.dumps(result, indent=2))
```

---

## MANEJO DE ERRORES

### Ejemplo: Crear colección con nombre duplicado
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "Ya Existe"}'
```

**Respuesta error (400):**
```json
{
  "detail": "Ya existe una colección con este nombre"
}
```

### Ejemplo: UPLOADER intentando crear colección
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer UPLOADER_TOKEN" \
  -d '{"name": "Nueva Colección"}'
```

**Respuesta error (403):**
```json
{
  "detail": "No autorizado para crear colecciones"
}
```

### Ejemplo: Obtener colección inexistente
```bash
curl http://localhost:8000/collections/999
```

**Respuesta error (404):**
```json
{
  "detail": "Colección no encontrada"
}
```

---

## MANEJO EN CLIENTE PYTHON

```python
import requests
from requests.exceptions import RequestException

def create_collection_safe(name: str, token: str) -> tuple[bool, dict]:
    """Crear colección con manejo de errores"""
    try:
        response = requests.post(
            f"{BASE_URL}/collections",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"name": name},
            timeout=10
        )
        
        if response.status_code == 201:
            return True, response.json()
        elif response.status_code == 400:
            return False, {"error": "Nombre duplicado o inválido"}
        elif response.status_code == 403:
            return False, {"error": "No autorizado"}
        elif response.status_code == 404:
            return False, {"error": "No encontrado"}
        else:
            return False, {"error": f"Error {response.status_code}"}
            
    except RequestException as e:
        return False, {"error": f"Error de conexión: {str(e)}"}

# Uso
success, result = create_collection_safe("Mi Colección", token)
if success:
    print("Colección creada:", result['data']['resource']['id'])
else:
    print("Error:", result['error'])
```

