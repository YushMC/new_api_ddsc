# 🚀 Guía de Uso: Notificaciones Discord de Mods

## 📍 Requisitos Previos

1. **Token Discord Webhook configurado**
   - Variable de entorno: `DISCORD_WEBHOOK_URL`
   - Debe estar en tu archivo `.env`

2. **API en ejecución**
   ```bash
   uvicorn src.main:app --reload
   ```

---

## 📥 Eventos Automáticos

Ahora **cada cambio** en un mod genera automáticamente una notificación en Discord:

### 1️⃣ **Creación de Mod**
**Endpoint:** `POST /mods`
```bash
curl -X POST http://localhost:8000/mods \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Nuevo Mod",
    "description": "Un mod increíble",
    "type": "MODIFICATION",
    "character": "MC",
    "duration": "LONG",
    "status": "STABLE"
  }'
```

**Discord notificará:**
```
✅ NUEVO MOD - APROBADO (si eres EDITOR/OWNER)
o
📝 NUEVO MOD - PENDIENTE APROBACIÓN (si eres UPLOADER)
```

---

### 2️⃣ **Actualizar Mod**
**Endpoint:** `PUT /mods/{id}`
```bash
curl -X PUT http://localhost:8000/mods/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nombre Actualizado",
    "description": "Nueva descripción"
  }'
```

**Discord notificará:**
```
🔄 MOD ACTUALIZADO
├─ Cambios:
│  ├─ name: "Antiguo" → "Nombre Actualizado"
│  └─ description: "Anterior" → "Nueva descripción"
└─ Actualizado por: Juan
```

---

### 3️⃣ **Aprobar Mod**
**Endpoint:** `POST /mods/{id}/approve`
```bash
curl -X POST http://localhost:8000/mods/1/approve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Discord notificará:**
```
✅ MOD APROBADO
├─ Mod: "Tu Mod Increíble"
├─ Aprobado por: Juan
└─ Este mod ahora es visible públicamente
```

---

### 4️⃣ **Rechazar Mod**
**Endpoint:** `POST /mods/{id}/rejected`
```bash
curl -X POST http://localhost:8000/mods/1/rejected \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Falta completar la descripción"
  }'
```

**Discord notificará:**
```
❌ MOD RECHAZADO
├─ Mod: "Tu Mod Increíble"
├─ Rechazado por: Juan
└─ Comentarios: "Falta completar la descripción"
```

---

### 5️⃣ **Eliminar Mod**
**Endpoint:** `DELETE /mods/{id}`
```bash
curl -X DELETE http://localhost:8000/mods/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Violación de derechos de autor"
  }'
```

**Discord notificará:**
```
🗑️ MOD ELIMINADO
├─ Mod: "Tu Mod Increíble"
├─ Eliminado por: Juan
└─ Razón: "Violación de derechos de autor"
```

---

### 6️⃣ **Restaurar Mod**
**Endpoint:** `POST /mods/{id}/restore`
```bash
curl -X POST http://localhost:8000/mods/1/restore \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Discord notificará:**
```
✅ MOD RESTAURADO
├─ Mod: "Tu Mod Increíble"
├─ Restaurado por: Juan
└─ Este mod es visible nuevamente
```

---

### 7️⃣ **Agregar Géneros** ✨ NUEVO
**Endpoint:** `POST /mods/{id}/genres`
```bash
curl -X POST http://localhost:8000/mods/1/genres \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "genre_ids": [1, 3, 5]
  }'
```

**Discord notificará:**
```
🏷️ GÉNEROS AGREGADOS
├─ Mod: "Tu Mod Increíble"
├─ Actualizado por: Juan
└─ Géneros Agregados: "Acción, Drama, Comedia"
```

---

### 8️⃣ **Remover Géneros** ✨ NUEVO
**Endpoint:** `DELETE /mods/{id}/genres`
```bash
curl -X DELETE http://localhost:8000/mods/1/genres \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "genre_ids": [1]
  }'
```

**Discord notificará:**
```
🏷️ GÉNEROS REMOVIDOS
├─ Mod: "Tu Mod Increíble"
├─ Actualizado por: Juan
└─ Géneros Removidos: "Acción"
```

---

## 🔍 Debugging

### Ver logs de notificaciones
```bash
# En la terminal donde corre el servidor uvicorn
# Busca líneas como:
# INFO: Notificación enviada a Discord exitosamente
# ERROR: Error notificando creación de mod a Discord: ...
```

### Verificar configuración de Discord
```python
from src.conf.discord_config import DiscordConfig

# En la terminal Python
print(DiscordConfig.is_configured())  # Debe ser True
print(DiscordConfig.WEBHOOK_URL[:20])  # Muestra primeros 20 caracteres
```

### Simular un error
Si Discord está caído y quieres simular:
1. Pausa tu servidor Discord
2. Haz una request a la API
3. Verás en logs: `Error enviando webhook: 404`
4. Pero la API retornará éxito (no se interrumpe)

---

## 🎯 Casos de Uso

### Caso 1: Workflow de Moderación

```
1. Uploader crea mod
   → Discord: "📝 NUEVO MOD - PENDIENTE APROBACIÓN"

2. Editor revisa el mod
   → Discord: "🔄 MOD ACTUALIZADO" (si hace cambios)

3. Editor aprueba
   → Discord: "✅ MOD APROBADO"
   
4. Uploader agrega géneros
   → Discord: "🏷️ GÉNEROS AGREGADOS"

5. Todo completo
   → 4 notificaciones en Discord del progreso
```

### Caso 2: Rápida Clasificación

```
1. Creas mod con todos los datos
2. Inmediatamente agregas géneros
   → 2 notificaciones en Discord
   → Tu canal ve todo el contexto
```

### Caso 3: Auditoría

```
Cada cambio queeda registrado en Discord
Puedes hacer scroll y ver:
- Quién hizo qué
- Cuándo lo hizo
- Exactamente qué cambió
```

---

## ⚙️ Arquitectura Detrás de Escenas

### Flujo Técnico

```
Cliente API
    ↓ [POST /mods]
FastAPI Route Handler
    ↓ [crud.create_mod()]
    ├─ Valida datos
    ├─ Guarda en BD
    └─ Retorna (mod)
    ↓ [background_tasks.add_task()]
    ├─ No bloquea respuesta
    └─ Agrega a cola
    ↓ [Retorna 201 Created]
Cliente recibe respuesta INMEDIATAMENTE ✅
    ↓ [En background]
Background Task Ejecuta:
    ├─ notify_mod_created(mod, user)
    ├─ Obtiene/crea event loop async
    ├─ loop.run_until_complete()
    ├─ DiscordNotifier.notify_mod_created()
    ├─ _format_embed_created()
    ├─ aiohttp POST webhook
    └─ Discord recibe embed
```

### Por qué es así

- ✅ **No bloquea**: Usuario recibe respuesta al instante
- ✅ **Robusto**: Si Discord falla, API sigue funcionando
- ✅ **Asincrónico**: Múltiples notificaciones en paralelo
- ✅ **Logged**: Todos los errores se registran

---

## 📊 Monitoreo

### Métricas a Considerar

- **Notificaciones enviadas por hora**
- **Tasa de error de webhook Discord**
- **Latencia promedio de notificaciones**

### Logs Recomendados

```python
# En discord_notifier.py
logger.info(f"Notificación enviada: {type(notification)}")
logger.error(f"Error en {function_name}: {e}")

# En background_tasks.py
logger.error(f"Error en background task {task_name}: {e}")
```

---

## 🔐 Consideraciones de Seguridad

### ✅ Implementado

- Notificaciones no exponen datos sensibles
- Solo información pública de mods
- No incluye tokens o credenciales
- Los links van a URLs públicas

### ⚠️ Ten Cuidado

- **WEBHOOK_URL** es sensible (incluir en .env.local)
- No compartir URL del webhook en público
- Si se comparte, alguien puede enviar mensajes

---

## 📝 Próximas Mejoras

1. **Batch Notifications**
   - Agrupar cambios si suceden en menos de 5 segundos

2. **Reactions**
   - Reaccionar en Discord para aprobar/rechazar

3. **Embeds Interactivos**
   - Botones para ver más detalles

4. **Rate Limiting**
   - Limitar si hay más de 10 eventos por minuto

5. **Analytics**
   - Dashboard con estadísticas

---

## 🆘 Troubleshooting

### "No recibo notificaciones"

1. ✅ Verifica que `DISCORD_WEBHOOK_URL` está configurada
   ```bash
   echo $DISCORD_WEBHOOK_URL
   ```

2. ✅ Verifica que el servidor está corriendo
   ```bash
   ps aux | grep uvicorn
   ```

3. ✅ Revisa los logs de la terminal

4. ✅ Prueba manualmente en Discord UI

### "Recibo error de webhook"

1. ✅ Verifica que la URL es válida
2. ✅ Verifica permisos del bot en Discord
3. ✅ Verifica que el canal existe

### "La notificación aparece tarde"

- Es normal, puede tardar 1-5 segundos
- Es una background task asincrónica
- No afecta la respuesta de la API (es instantánea)

---

## 📞 Soporte

Si algo no funciona:

1. Revisa los logs de la terminal
2. Verifica la configuración de Discord
3. Prueba con curl desde la terminal
4. Activa modo debug: `logger.setLevel(DEBUG)`

---

## ✅ Checklist Final

Antes de ir a producción:

- [ ] `DISCORD_WEBHOOK_URL` configurada en .env
- [ ] Discord bot tiene permisos en el canal
- [ ] API corre sin errores
- [ ] Probaste al menos 2 eventos
- [ ] Revisaste los logs
- [ ] El embed se ve bien en Discord

¡Listo para producción! 🚀
