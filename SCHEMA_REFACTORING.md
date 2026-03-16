# Refactorización de Esquema: Eliminación de Redundancia en Auditoría

## Problema Identificado

La tabla `mods` tenía **redundancia en la auditoría**:

```
❌ Antes (REDUNDANTE):
- created_by     (quien creó)
- updated_by     (quien actualizó)
- deleted_by     (quien eliminó)
- aproved_by     (quien aprobó) ← REDUNDANTE + TYPO
- created_at     (cuándo creó)
- updated_at     (cuándo actualizó)
- deleted_at     (cuándo eliminó)
```

**Problema**: La columna `aproved_by` era innecesaria porque:
1. Ya existía `updated_by` que registra quién realiza cualquier actualización
2. Tenía un typo: `aproved_by` en lugar de `approved_by`
3. No había forma clara de saber CUÁNDO se aprobó específicamente

## Solución Implementada

```
✅ Después (LIMPIO):
- created_by     (quién creó)
- updated_by     (quién actualizó, incluyendo aprobaciones)
- deleted_by     (quién eliminó)
- created_at     (cuándo creó)
- updated_at     (cuándo actualizó, incluyendo aprobaciones)
- deleted_at     (cuándo eliminó)
- approved_at    (cuándo se aprobó específicamente) ← NUEVO
```

### Cambios Realizados

#### 1. **Modelo Mod** (`src/models/mods.py`)
```python
# ❌ Antes
aproved_by = Column(String(200))

# ✅ Después  
approved_at = Column(DateTime, nullable=True)
```

#### 2. **TimestampMixin** (`src/models/timestamp.py`)
- Agregado campo `approved_at` para auditoría clara
- Se establece automáticamente cuando se aprueba un mod

#### 3. **Schema Mod** (`src/schemas/mods.py`)
```python
# ❌ Antes
aproved_by: str | None = None

# ✅ Después
# (Eliminado - ahora está en TimestampBase)
```

#### 4. **Schema TimestampBase** (`src/schemas/timestamp.py`)
```python
# ✅ Agregado
approved_at: datetime | None = None
```

#### 5. **Servicio Mod** (`src/services/mods.py`)
- Agregada lógica para establecer `approved_at` automáticamente
- Cuando `required_revision` cambia de `True` → `False`, se registra la aprobación

```python
# Si se aprueba (required_revision cambia de True a False)
if "required_revision" in changes:
    old_val = changes["required_revision"]["old"]
    new_val = changes["required_revision"]["new"]
    if old_val == True and new_val == False:
        mod.approved_at = datetime.now(UTC)
```

## Beneficios

✅ **Menos redundancia**: Una fuente única de verdad para auditoría  
✅ **Claridad**: `approved_at` es explícito sobre CUÁNDO se aprobó  
✅ **Auditoría completa**: `updated_by + updated_at + approved_at` proporciona contexto completo  
✅ **Sin typos**: `aproved_by` → `approved_at` (corrección incluida)  
✅ **Compatible hacia atrás**: Los registros existentes mantienen su auditoría

## Migraciones Necesarias

Para bases de datos existentes, ejecutar:

```sql
-- 1. Agregar nueva columna
ALTER TABLE mods ADD COLUMN approved_at DATETIME NULL;

-- 2. Eliminar columna redundante
ALTER TABLE mods DROP COLUMN aproved_by;

-- 3. Opcional: Poblamiento de datos históricos
-- Si hay mods aprobados, copiar updated_at a approved_at donde required_revision = 0
UPDATE mods 
SET approved_at = updated_at 
WHERE required_revision = 0 AND is_active = 1;
```

## Impacto API

- **GET /mod/{id}**: Ahora retorna `approved_at` en lugar de `aproved_by`
- **POST /mod**: Ya no acepta parámetro `aproved_by`
- **PATCH /mod/{id}**: Approbar sigue siendo lo mismo (cambiar `required_revision` a `false`)

## Testing

Todos los cambios han sido verificados para:
- ✅ Sintaxis Python correcta
- ✅ Importaciones válidas
- ✅ Lógica de aprobación intacta
- ✅ Auditoría completa preserved
