# Vehicle Intake API

Esta API, desarrollada con **FastAPI**, proporciona los servicios backend necesarios para la gestión de clientes y vehículos, así como para la evaluación de elegibilidad. Está diseñada para ser consumida por el `Chatbot de Admisión Vehicular` (enlaza aquí tu otro repositorio si lo deseas).

La API utiliza **SQLAlchemy** para el ORM, **Alembic** para las migraciones de la base de datos y sigue una arquitectura limpia y modular separando rutas, servicios y entidades.

## Características

  - **API Asíncrona**: Construida sobre FastAPI y `asyncio` para un alto rendimiento.
  - **Gestión de Clientes y Vehículos**: Endpoints para operaciones CRUD (Crear, Leer, Actualizar, Borrar) de clientes y sus vehículos asociados.
  - **Servicio de Elegibilidad**: Un endpoint dedicado para evaluar si un cliente y su vehículo cumplen con las reglas de negocio predefinidas.
  - **Base de Datos Relacional**: Integración con PostgreSQL y gestión de migraciones con Alembic.
  - **Validación de Datos**: Uso de Pydantic para la validación robusta de los datos de entrada y salida.

## Cómo Empezar

Sigue estos pasos para levantar el servicio de la API en tu entorno local.

### Prerrequisitos

  - Python 3.10 o superior
  - Docker y Docker Compose (recomendado para la base de datos)
  - `pip` y `virtualenv` para gestionar las dependencias.

### 1\. Instalación

Crea y activa un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
```

Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

### 2\. Configuración del Entorno

La API se configura mediante variables de entorno. Crea un archivo `.env` en el directorio raíz de la API. Puedes usar el archivo `example.env` como plantilla:

```bash
cp example.env .env
```

Abre el archivo `.env` y ajusta las variables si es necesario. La configuración por defecto está pensada para funcionar con el `docker-compose.yml`.

#### Variables de Entorno

| Variable               | Descripción                                       | Valor por Defecto |
| ---------------------- | ------------------------------------------------- | ----------------- |
| `DB_POSTGRES_HOST`     | El host donde se ejecuta la base de datos.        | `db`              |
| `DB_POSTGRES_PORT`     | El puerto de la base de datos.                    | `5432`            |
| `DB_POSTGRES_USER`     | El nombre de usuario para la conexión.            | `admin`           |
| `DB_POSTGRES_PASSWORD` | La contraseña para la conexión.                   | `Ab123456`        |
| `DB_POSTGRES_DB`       | El nombre de la base de datos a la que conectar.  | `vic_db`          |

### 3\. Base de Datos

La forma más sencilla de levantar la base de datos es usando Docker Compose.

```bash
docker-compose up -d
```

Una vez que el contenedor de la base de datos esté en funcionamiento, aplica las migraciones de Alembic para crear las tablas:

```bash
alembic upgrade head
```

### 4\. Ejecutar la API

Finalmente, inicia el servidor de la API con Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en `http://localhost:8000`. Puedes explorar los endpoints interactivos en `http://localhost:8000/docs`.

## Migraciones con Alembic

Alembic se utiliza para gestionar los cambios en el esquema de la base de datos. A continuación se muestran los comandos más comunes.

### Crear una nueva migración

Cuando realices cambios en los modelos de SQLAlchemy (en `api/entities`), debes generar un nuevo script de migración:

```bash
alembic revision --autogenerate -m "Descripción breve de los cambios"
```

### Aplicar migraciones

Para aplicar todas las migraciones pendientes y llevar la base de datos a la última versión:

```bash
alembic upgrade head
```

### Otros comandos útiles

```bash
# Ver la revisión actual
alembic current

# Ver el historial de migraciones
alembic history --verbose
```
