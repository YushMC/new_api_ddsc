# 🤖 Configuración de Notificaciones en Discord

## 📋 Resumen

Las notificaciones a Discord se envían automáticamente cuando:
- ✅ Se crea un nuevo mod
- ✅ Se actualiza un mod
- ✅ Se aprueba un mod (cuando UPLOADER es aprobado por EDITOR/OWNER)

---

## 🔧 Configuración Inicial

### 1. Crear un Webhook en Discord

1. **Abre tu servidor de Discord**
2. **Ve a Configuración del servidor** → **Integraciones** → **Webhooks**
3. Haz click en **"Nuevo Webhook"**
4. Dale un nombre descriptivo (ej: "DDSC Mods Bot")
5. Selecciona el canal donde quieres las notificaciones
6. Haz click en **"Copiar URL del Webhook"**

**La URL se verá así:**
```
https://discordapp.com/api/webhooks/123456789123456789/abcDefGhIjKlMnOpQrStUvWxYz-1234567890
```

### 2. Agregar al archivo `.env`

Abre tu archivo `.env` (creado desde `.env.example`) y completa:

```env
# Discord Notifications
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/123456789123456789/abcDefGhIjKlMnOpQrStUvWxYz-1234567890
FRONTEND_BASE_URL=https://tudominio.com
```

**Notas:**
- `DISCORD_WEBHOOK_URL`: La URL del webhook que copiaste
- `FRONTEND_BASE_URL`: URL de tu aplicación web (ej: `https://mods.miapp.com`)
  - Si no tienes frontend, se usará `http://localhost:8000/mod/{id}` por defecto

### 3. Reinicia la API

```bash
uvicorn main:app --reload
```

---

## 📱 Ejemplos de Notificaciones

### 1. Crear Mod (UPLOADER - Requiere Aprobación)

**Título:** 📝 NUEVO MOD - PENDIENTE APROBACIÓN
**Color:** 🔴 Rojo

```
Creador: juan (UPLOADER)
Nombre: Mi Nuevo Mod
Personaje: Monika
Duración: Medio
Estado: Beta
Revisión: ⏳ Requiere Revisión
Géneros: Horror, Psychological
🔗 Ver Mod
```

### 2. Crear Mod (EDITOR - Automáticamente Aprobado)

**Título:** ✅ NUEVO MOD - APROBADO
**Color:** 🟢 Verde

```
Creador: maria (EDITOR)
Nombre: Mi Nuevo Mod
Personaje: Yuri
Duración: Largo
Estado: Stable
Revisión: ✅ Automáticamente Aprobado
Géneros: Horror
🔗 Ver Mod
```

### 3. Actualizar Mod

**Título:** 🔄 MOD ACTUALIZADO
**Color:** 🟠 Naranja

```
Actualizado por: admin (EDITOR)
Mod: Mi Nuevo Mod

Cambios:
• status: beta → stable
• duration: medium → large
• character: monika → yuri

🔗 Ver Mod
```

### 4. Aprobar Mod (UPLOADER → Aprobado)

**Título:** ✅ MOD APROBADO
**Color:** 🟢 Verde Oscuro

```
Mod: Mi Nuevo Mod
Creador: juan
Aprobado por: maria (EDITOR)

✅ Este mod ahora es visible públicamente

Descripción: Lorem ipsum dolor sit amet...
🔗 Ver Mod
```

---

## 🔐 Seguridad

### Protege tu Webhook URL

⚠️ **IMPORTANTE**: La URL del webhook es una credencial. No la compartas públicamente.

**Buenas prácticas:**
- ✅ Guarda en `.env` (que está en `.gitignore`)
- ✅ Usa variables de entorno en producción
- ✅ No commits la URL a Git
- ✅ Si la comprometes, regenera el webhook

### Permisos del Webhook

El webhook necesita permisos básicos:
- Enviar mensajes
- Insertar embeds
- (No necesita permisos adicionales)

---

## 🧪 Pruebas

### Test Manual sin API

Puedes probar el webhook manualmente con `curl`:

```bash
curl -X POST https://discordapp.com/api/webhooks/YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "✅ Test Webhook",
      "description": "Si ves esto, tu webhook funciona!",
      "color": 65280
    }]
  }'
```

### Test con API

1. **Inicia la API**
2. **Crea un mod** vía API
   ```bash
   curl -X POST http://localhost:8000/mod \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Mod",
       "description": "Test",
       "slug": "test-mod",
       "status": "beta",
       "duration": "medium",
       "character": "monika"
     }'
   ```
3. **Verifica Discord**: Deberías ver el mensaje en tu canal

---

## 🆘 Troubleshooting

### No recibo notificaciones

**Problema:** La API no está enviando notificaciones a Discord

**Solución:**
1. Verifica que `DISCORD_WEBHOOK_URL` está en `.env`
2. Verifica que la URL es válida (copia exacta del webhook)
3. Revisa los logs de la API: `ERROR notificando ... a Discord`
4. Prueba el webhook manualmente con `curl` (ver Test Manual)

### URL incorrecta en Discord

**Problema:** El link en Discord no va al lugar correcto

**Solución:**
1. Verifica que `FRONTEND_BASE_URL` es correcto
2. Si no tienes frontend, deja vacío en `.env` (usará API por defecto)
3. La URL debe ser accesible públicamente

### Webhook URL expiró

**Problema:** Recibí error 404 al enviar notificación

**Solución:**
1. Regenera el webhook en Discord
2. Actualiza la URL en `.env`
3. Reinicia la API

---

## 📊 Logs

Las notificaciones a Discord se registran en los logs:

```
INFO: Notificación enviada a Discord exitosamente
ERROR: Error enviando webhook: 401 - Invalid webhook
ERROR: Timeout enviando webhook a Discord
```

---

## 🎨 Personalización

Puedes modificar los colores y formatos en `src/conf/discord_config.py`:

```python
class DiscordConfig:
    COLOR_PENDING = 0xFF0000      # Rojo (en hexadecimal)
    COLOR_APPROVED = 0x00FF00     # Verde
    COLOR_UPDATED = 0xFFA500      # Naranja
    COLOR_APPROVED_ADMIN = 0x00DD00  # Verde oscuro
```

Y los formatos de embed en `src/utils/discord_notifier.py`:
- `_format_embed_created()` - Formato de creación
- `_format_embed_updated()` - Formato de actualización
- `_format_embed_approved()` - Formato de aprobación

---

## ✅ Checklist

```
☐ Crear webhook en Discord
☐ Copiar URL del webhook
☐ Agregar DISCORD_WEBHOOK_URL a .env
☐ Agregar FRONTEND_BASE_URL a .env
☐ Reiniciar API
☐ Crear un mod de prueba
☐ Verificar notificación en Discord
☐ (Opcional) Personalizar colores o formato
```

---

## 📞 Ayuda

Si algo no funciona:

1. **Revisa los logs** de la API
2. **Prueba el webhook** manualmente con `curl`
3. **Verifica las variables de entorno** en `.env`
4. **Asegúrate que Discord está configurado** correctamente

Las notificaciones están diseñadas para **no interrumpit la API**, así que si falla Discord, el mod se crea normalmente.
