-- Migration: Add 'type' field to mods table
-- Description: Adds ModTypeEnum field with values 'translation' or 'original'
-- Date: 2026-03-16

-- Agregar columna 'type' a la tabla mods si no existe
-- Esta columna almacena el tipo de mod: 'translation' o 'original'
ALTER TABLE mods 
ADD COLUMN type ENUM('translation', 'original') NOT NULL AFTER slug;

-- Para aplicar esta migración:
-- mysql -h <host> -u <user> -p <database> < migrations/001_add_type_to_mods.sql
