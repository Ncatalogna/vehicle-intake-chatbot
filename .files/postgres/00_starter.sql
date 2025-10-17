-- Script inicial para configuraciones básicas de la base de datos
-- Este script asegura que las extensiones necesarias estén disponibles

-- Crear la extensión uuid-ossp si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;