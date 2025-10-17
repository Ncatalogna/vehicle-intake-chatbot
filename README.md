# Demo Challenge: Agentes y Workflows con LangGraph - Vehicle Intake Chatbot

Este repositorio contiene una demostración técnica que explora la implementación de un sistema de agentes conversacionales y workflows utilizando **LangChain** y **LangGraph**. El objetivo principal es mostrar cómo orquestar flujos de conversación complejos de manera modular y robusta.

El proyecto se divide en dos componentes principales:

1.  **`/chatbot`**: Un asistente conversacional que guía a los usuarios a través de un proceso de admisión vehicular.
2.  **`/api`**: Un backend de servicios RESTful construido con **FastAPI** que maneja la lógica de negocio y la persistencia de datos.

Para una explicación detallada de cada componente, por favor, consulta sus respectivos `README.md`:

  - **[Documentación del Chatbot](./chatbot/README.md)**
  - **[Documentación de la API](./api/README.md)**

## 🚀 Entorno de Desarrollo (Recomendado)

La forma más sencilla de levantar y probar este proyecto es utilizando el **Dev Container** incluido, que garantiza un entorno de desarrollo consistente y autocontenido.

El Dev Container utiliza Docker Compose para orquestar los servicios necesarios:

  * **`app`**: Un contenedor con Python 3.12 y todas las dependencias del proyecto preinstaladas en un entorno virtual.
  * **`db`**: Un servicio de base de datos **PostgreSQL** con la extensión `pgvector` habilitada, listo para ser utilizado por la API.

### Cómo usar el Dev Container

1.  Abre el proyecto en **Visual Studio Code**.
2.  Asegúrate de tener instalada la extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
3.  VS Code detectará la configuración y te pedirá **"Reopen in Container"**. Haz clic para aceptar.
4.  Una vez dentro, podrás ejecutar la API y el Chatbot desde la terminal de VS Code como se describe en sus respectivos `README.md`.

Si prefieres una configuración manual, por favor, sigue las guías detalladas en la documentación de cada subdirectorio.

## Cómo ejecutar la aplicación

Si no se utiliza el devcontainer, se deben seguir los siguientes pasos:
1. Montar la base de datos con `docker-compose up db`.
2. Instalar las dependencias con `pip install -r requirements.txt`.
3. Configurar el archivo `.env` en la carpeta `api`.
4. Ejecutar las migraciones de la base de datos.
5. Ejecutar la API.
6. Configurar el archivo `.env` en la carpeta `chatbot`.
7. Ejecutar el chatbot.

## Pruebas HTTP

En la carpeta `.rest` se encuentran los archivos `clients.rest`, `eligibility.rest` y `vehicles.rest`. Estos archivos contienen pruebas HTTP que se pueden ejecutar con la extensión de Visual Studio Code [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) para probar los endpoints de la API.

-----

## 💡 Soluciones de Compromiso (Trade-offs)

Durante el desarrollo, se tomaron ciertas decisiones para mitigar limitaciones encontradas en las librerías:

  - **Serialización en LangGraph**: Se detectaron problemas de estabilidad al usar tipos `Enum` y `List` en los esquemas Pydantic para la salida estructurada (`with_structured_output`). Estos problemas, documentados en la comunidad de LangChain, podían causar fallos inesperados.
      - *LangChain Issue #33444*: Reporta un crash (`AttributeError: 'int' object has no attribute 'name'`) por un valor de `FinishReason` no reconocido de la API de Gemini.
      - *LangChain Discussion #28778*: Los usuarios confirman que el uso de `Enum` en la especificación de salida estructurada causa.
  - **Mitigación**: Para asegurar la robustez, se optó por usar tipos más simples como `str` en el esquema Pydantic y manejar la validación y conversión a `Enum` en el código de la aplicación. Esto evita delegar la restricción al LLM, que puede no ser consistente.

-----

## 🚧 Deuda Técnica

  - **Flujo de Agente más Dinámico**: El flujo actual, aunque orquestado, sigue un patrón relativamente estructurado. Una mejora sería hacerlo menos dependiente de un RAG (Retrieval-Augmented Generation) implícito y más capaz de decidir rutas complejas de manera autónoma.

-----

## 🌱 Posibles Implementaciones

Debido a limitaciones de tiempo, las siguientes características no fueron implementadas pero representan los siguientes pasos lógicos para el proyecto:

  - **Optimización del Flujo con un Patrón "Extractor-Ejecutor"**: El workflow actual se basa en agentes que interpretan la intención y ejecutan herramientas (tools) que a su vez llaman a la API. Para un flujo tan definido como este, se podría implementar un patrón más directo y eficiente en el uso de tokens. En lugar de un agente, el LLM se usaría únicamente para extraer la información del usuario en un formato estructurado (JSON). El propio nodo del grafo, al recibir estos datos, sería el encargado de ejecutar la lógica y realizar las llamadas a la API directamente con código Python. Este enfoque, similar a un RAG pero centrado en la acción, reduciría la sobrecarga de tokens y la complejidad de la interacción del LLM con las herramientas.
  - **Monitoreo con Langfuse**: Integrar Langfuse para obtener trazabilidad, monitoreo y análisis detallado de las interacciones y el rendimiento de los agentes.
  - **Búsqueda Vectorial con pgvector**: Implementar una búsqueda de similitud semántica (por ejemplo, para encontrar clientes o vehículos con datos parecidos) aprovechando la extensión `pgvector` ya incluida en la base de datos.
  - **Sub-Workflows en LangGraph**: Refactorizar el grafo principal para utilizar sub-grafos (o "sub-workflows"). Esto permitiría encapsular lógicas complejas (como todo el proceso de validación de cliente) en workflows anidados, haciendo el sistema principal más limpio y modular.