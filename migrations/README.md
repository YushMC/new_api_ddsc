# Database Migrations

Este directorio contiene los scripts SQL de migración para la base de datos.

## Cómo ejecutar las migraciones

### Opción 1: Manualmente con MySQL CLI

```bash
mysql -h <host> -u <usuario> -p <base_de_datos> < migrations/001_add_views_column_to_mods_estadisticas.sql
```

### Opción 2: Desde una herramienta MySQL GUI (phpMyAdmin, MySQL Workbench, etc.)

1. Abre la herramienta de gestión de MySQL
2. Conectate a la base de datos
3. Copia y ejecuta el contenido del archivo `.sql`

## Migraciones disponibles

### 001_add_views_column_to_mods_estadisticas.sql
- **Descripción**: Agrega la columna `views` a la tabla `mods_estadisticas`
- **Razón**: El modelo SQLAlchemy requiere esta columna para rastrear vistas de mods
- **Cambios**: 
  - Agrega `views INT DEFAULT 0` después de la columna `searchs`

## Notas importantes

- Las migraciones deben ejecutarse en orden numérico
- No se pueden ejecutar dos migraciones simultáneamente
- Realizar backup de la base de datos antes de ejecutar migraciones
- Las migraciones son irreversibles, considerar rollback manualmente si es necesario
