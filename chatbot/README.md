# Chatbot de Admisión Vehicular

Este es un chatbot conversacional diseñado para guiar a los usuarios a través de un proceso de admisión vehicular. Recopila información del cliente y del vehículo, la valida y finalmente comprueba la elegibilidad para un producto o servicio.

El proyecto está construido con **Python**, **LangChain** y **LangGraph** para orquestar el flujo de la conversación de manera robusta y modular.

## Características

  - **Flujo de Conversación Orquestado**: Utiliza un grafo de estados (StateGraph) para gestionar el diálogo, pasando por nodos de recolección, validación y confirmación de datos.
  - **Arquitectura Modular**: El chatbot se divide en "workers" especializados, cada uno responsable de una tarea específica (supervisar el flujo, validar datos del cliente, generar respuestas, etc.).
  - **Integración con Herramientas (Tools)**: Hace uso de herramientas de LangChain para interactuar con una base de datos simulada (en memoria) para clientes y vehículos.
  - **Soporte para Múltiples LLMs**: Configurable para usar diferentes proveedores de modelos de lenguaje como Groq o Google Gemini.

## Cómo Empezar

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 2\. Configuración del Entorno

El chatbot requiere claves de API y otras configuraciones que se gestionan a través de un archivo `.env`.

Crea un archivo llamado `.env` dentro de la carpeta `chatbot/`. Puedes hacerlo copiando el archivo de ejemplo `example.env`:

```bash
cp chatbot/example.env chatbot/.env
```

Ahora, abre `chatbot/.env` y edita las variables con tus propias claves de API y configuraciones.

#### Variables de Entorno

A continuación se detallan las variables que necesitas configurar en tu archivo `.env`. La mayoría son opcionales y tienen valores predeterminados seguros.

| Variable         | Descripción                                                                                                                                                             | Valor de Ejemplo        |
| :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------- |
| `LOG_LEVEL`      | Controla el nivel de detalle de los logs. Opciones: `DEBUG`, `INFO`, `WARNING`, `ERROR`. `DEBUG` es muy verboso.                                                          | `INFO`                  |
| `API_URL`        | Define la URL del backend. Aunque no se usa en la versión actual del chatbot de terminal, está reservado para futuras integraciones.                                     | `http://localhost:8000` |
| `LLM_PROVIDER`   | Selecciona el proveedor del modelo de lenguaje a utilizar. Las opciones válidas son `"groq"` o `"gemini"`.                                                                | `groq`                  |
| `GROQ_API_KEY`   | Tu clave de API para el servicio de Groq. Es necesaria si `LLM_PROVIDER` está configurado como `"groq"`. Puedes obtenerla en Groq Console. | `"gsk_..."`             |
| `GEMINI_API_KEY` | Tu clave de API para Google Gemini. Es necesaria si `LLM_PROVIDER` está configurado como `"gemini"`. Puedes obtenerla en Google AI Studio. | `"AIzaSy..."`           |

**Importante**: Asegúrate de que la variable `LLM_PROVIDER` esté configurada con el proveedor que deseas utilizar (`groq` o `gemini`) y que la `API_KEY` correspondiente tenga un valor válido.

### 3\. Ejecutar el Chatbot

Una vez que hayas configurado tu archivo `.env`, puedes iniciar el chatbot en modo terminal con el siguiente comando:

```bash
python chatbot/terminal.py
```

¡Y listo\! Ya puedes empezar a interactuar con el asistente en tu terminal. Escribe `salir` para finalizar la sesión.

## Debugging en VS Code

Para facilitar el desarrollo y la depuración, puedes usar la configuración de lanzamiento de Visual Studio Code incluida en este proyecto.

1.  Abre el proyecto en VS Code.
2.  Ve a la pestaña "Run and Debug" (o presiona `Ctrl+Shift+D`).
3.  En el menú desplegable de la parte superior, selecciona la configuración **"Python: Chatbot Terminal"**.
4.  Presiona `F5` o haz clic en el icono de play (▶️) para iniciar una sesión de depuración, elegir `Python: Chatbot Terminal`
