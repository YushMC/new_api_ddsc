-- Migration: Add views column to mods_estadisticas table
-- Description: Agregar columna 'views' a la tabla mods_estadisticas
-- Date: 2026-03-25

ALTER TABLE mods_estadisticas ADD COLUMN views INT DEFAULT 0 AFTER searchs;
