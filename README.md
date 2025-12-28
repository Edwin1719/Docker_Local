# Agente Local Docker Model Runner con Capacidad de Búsqueda Web

Este proyecto implementa un entorno para interactuar con Modelos de Lenguaje Grandes (LLMs) de forma local, potenciado por un agente ligero de Business Intelligence (BI) con capacidad para realizar búsquedas en la web en tiempo real. La ejecución del LLM se realiza a través de la funcionalidad "Docker Model Runner" de Docker Desktop, que proporciona un servidor de inferencia de modelos en un puerto TCP local.

## 📜 Descripción

El sistema permite a los usuarios enviar consultas a un modelo de lenguaje que se ejecuta localmente. Se incluyen dos scripts principales:

1.  `main.py`: Un cliente simple para enviar prompts directos al modelo y recibir respuestas.
2.  `agent_search.py`: Un agente más sofisticado que puede interpretar una consulta, decidir si necesita información externa, realizar una búsqueda web utilizando la API de Tavily y, finalmente, sintetizar una respuesta informada basada en los datos recopilados.

Adicionalmente, el entorno se complementa con una interfaz de usuario web (`Open-WebUI`) para la interacción conversacional directa con el modelo.

## 🌱 Evolución del Proyecto

Este proyecto se desarrolló en tres fases clave, demostrando un camino progresivo desde una simple conexión hasta una aplicación web funcional.

### Fase 1: Conexión Directa (`main.py`)
El punto de partida fue establecer una comunicación básica con el modelo de lenguaje local servido a través del "Docker Model Runner". El script `main.py` es un testimonio de esta fase: un código sencillo y directo que envía un prompt al modelo y recibe una respuesta. Sirve como la prueba de concepto fundamental de la conexión.

### Fase 2: Un Agente con Herramientas (`agent_search.py`)
Una vez establecida la conexión, el siguiente paso fue dotar al sistema de mayor inteligencia. Se creó `agent_search.py`, un agente simple pero funcional. Este agente introdujo la capacidad de "razonamiento": podía analizar una pregunta y decidir autónomamente si responder con su conocimiento base o utilizar una herramienta externa (la API de Tavily) para realizar una búsqueda en la web y obtener información actualizada.

### Fase 3: Interfaz Gráfica con Streamlit (`app.py`)
La fase final consistió en hacer que el agente fuera accesible y fácil de usar para cualquier persona. Se desarrolló `app.py`, una aplicación web completa construida con Streamlit. Esta interfaz no solo proporciona un chat interactivo, sino que también implementa características profesionales como:
- **Historial de conversación** para mantener el contexto (aunque con limitaciones intencionadas para mejorar el rendimiento).
- **Respuestas en streaming** para una experiencia de usuario fluida y en tiempo real.
- **Un diseño profesional** con una barra lateral informativa y una disposición clara.
- **Manejo de errores y estados de carga** para una mayor robustez.

## 🏗️ Arquitectura del Sistema

La arquitectura de este proyecto se compone de tres partes principales que operan de manera coordinada:

![Arquitectura del Sistema](https://i.imgur.com/your-architecture-diagram.png)  <!-- Reemplazar con un diagrama real si es posible -->

1.  **Motor del LLM (Docker Model Runner)**
    *   **Tecnología**: El servicio que ejecuta el modelo de lenguaje es proporcionado por la funcionalidad **"Docker Model Runner"** de Docker Desktop. Esta característica permite a Docker Desktop ejecutar motores de inferencia acelerados por GPU y exponerlos en el host.
    *   **Configuración**: El "Docker Model Runner" está habilitado para el soporte TCP en el lado del host, exponiendo el servicio del LLM en el puerto **`12434`** (`http://localhost:12434`).
    *   **Modelo**: El modelo `ai/gemma3:4B` es descargado y gestionado directamente por este "Docker Model Runner".

2.  **Scripts de Python (Clientes de la API)**
    *   Los scripts `main.py` y `agent_search.py` actúan como clientes que consumen la API del LLM.
    *   Envían peticiones HTTP POST al endpoint `http://localhost:12434/v1/chat/completions` para interactuar con el modelo.
    *   `agent_search.py` además se conecta a la API externa de [Tavily AI](https://tavily.com/) para sus capacidades de búsqueda web.

3.  **Interfaz de Usuario (Open-WebUI)**
    *   **Tecnología**: Es una aplicación web que se ejecuta en un **contenedor Docker** a partir de la imagen `ghcr.io/open-webui/open-webui:main`.
    *   **Función**: Provee una interfaz gráfica de chat (accesible en `http://localhost:3000`) para una interacción más amigable con el modelo.
    *   **Conexión**: Esta interfaz está configurada para comunicarse internamente con el "Docker Model Runner" (posiblemente a través de `model-runner.docker.internal:80`), lo que permite que Open-WebUI funcione como un frontend para el LLM.

## 🔧 Configuración del Entorno de Docker

Antes de la instalación del proyecto, es crucial configurar correctamente Docker Desktop para que pueda servir el modelo de lenguaje.

### 1. Configuración del Docker Model Runner

El "Docker Model Runner" es una característica de Docker Desktop que gestiona la ejecución de modelos de IA. Sigue estos pasos para configurarlo:

1.  Abre **Docker Desktop** y ve a **Settings** (el icono del engranaje).
2.  Navega a la sección **AI/ML**.
3.  Activa la opción principal: **"Enable Docker Model Runner"**.
4.  **Activa la aceleración por GPU (MUY RECOMENDADO)**: Marca la casilla **"Enable GPU-backed inference"**. Esto es fundamental para obtener un buen rendimiento y evitar timeouts.
    *   *Nota: Requiere una tarjeta gráfica NVIDIA compatible con los drivers de CUDA correctamente instalados en tu sistema.*
5.  **Habilita la conexión local**: Marca la casilla **"Enable host-side TCP support"**. Esto expone el modelo en un puerto de tu máquina para que nuestras aplicaciones puedan conectarse.
6.  **Configura el Puerto**: En el campo **Port**, asegúrate de que el valor sea **`12434`**. Este es el puerto que nuestro proyecto espera.
7.  **Orígenes CORS**: Deja el valor por defecto (`All` o `*`) para desarrollo local.

Tu configuración debería verse similar a esto:

```text
Docker Model Runner
[x] Enable Docker Model Runner

    Enable GPU-accelerated inference engines...

[x] Enable host-side TCP support
    Port: 12434

    CORS allowed origins: All

[x] Enable GPU-backed inference
```

### 2. Descarga del Modelo de Lenguaje

Con el "Docker Model Runner" activado, puedes descargar modelos directamente desde Docker Hub a través de la interfaz de Docker Desktop.

1.  Abre **Docker Desktop**.
2.  En el panel de la izquierda, busca y haz clic en la sección **Models**.
3.  Dentro de la sección de "Models", verás una lista de modelos disponibles de Docker Hub. Usa la barra de búsqueda para encontrar el modelo que necesitamos para este proyecto:
    ```
    ai/gemma3:4B
    ```
4.  Una vez encontrado, haz clic en el botón **Download** (o similar) junto al nombre del modelo.
5.  Espera a que Docker Desktop complete la descarga. El progreso se mostrará en la misma interfaz.

Este proceso descargará el modelo y lo hará disponible para que el "Docker Model Runner" lo utilice, asegurando que esté listo cuando nuestra aplicación lo solicite.

## ⚙️ Prerrequisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

*   **Python 3.8+**
*   **Docker Desktop**: Necesario. Asegúrate de tener la funcionalidad "Docker Model Runner" habilitada y configurada para exponer el puerto `12434` en el host. Esta configuración suele encontrarse en las preferencias de Docker Desktop, en la sección "AI/ML" o similar.
*   **Modelo de Lenguaje**: El modelo `ai/gemma3:4B` será descargado y gestionado automáticamente por el "Docker Model Runner" cuando se le solicite, o puedes iniciarlo directamente desde la terminal si el "Docker Model Runner" lo permite.
*   **Docker Desktop**: Necesario si deseas utilizar la interfaz gráfica de Open-WebUI. Descárgalo desde [Docker Hub](https://www.docker.com/products/docker-desktop/).

## 🚀 Instalación

Sigue estos pasos para configurar el proyecto en tu máquina local:

1.  **Asegúrate de que Docker Desktop esté instalado y el "Docker Model Runner" esté habilitado**:
    *   Verifica que Docker Desktop esté ejecutándose en tu sistema.
    *   En las preferencias de Docker Desktop, navega a la sección de "AI/ML" o similar y asegúrate de que el "Docker Model Runner" esté habilitado.
    *   Confirma que el puerto `12434` esté configurado y expuesto para el "host-side TCP support".

2.  **Clona el repositorio** (o descarga los archivos en un directorio local):
    ```bash
    git clone <URL-del-repositorio>
    cd <nombre-del-directorio>
    ```

3.  **Crea un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

4.  **Instala las dependencias** de Python:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configura las variables de entorno**:
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Añade tu clave de API de Tavily. El archivo debe lucir así:
    ```ini
    TAVILY_API_KEY="tu-clave-de-api-de-tavily"
    MODEL_URL="http://localhost:12434/v1/chat/completions"
    MODEL_NAME="ai/gemma3:4B"
    ```

## ▶️ Uso

Asegúrate de que el **"Docker Model Runner" esté activo y gestionando el modelo `ai/gemma3:4B`** en el puerto `12434`.

### Ejecutar el script simple

Este script enviará un prompt predefinido al modelo y mostrará la respuesta.

```bash
python main.py
```

### Ejecutar el Agente de Búsqueda

Este script te pedirá que introduzcas una pregunta. El agente procesará la pregunta, buscará en la web si es necesario y generará un reporte.

```bash,
python agent_search.py
```
> **Pregunta:** `[Escribe tu pregunta aquí y presiona Enter]`


### Acceder a la Interfaz Web (Opcional)

Si tienes Docker y has iniciado el contenedor de `open-webui`, puedes acceder a la interfaz de chat abriendo tu navegador y visitando:
[**http://localhost:3000**](http://localhost:3000)

---
*Este README fue generado para documentar la arquitectura y el funcionamiento del proyecto de agente local.*

## 💡 Casos de Uso Potenciales

Esta arquitectura de LLM local abre un amplio abanico de posibilidades para el desarrollo de aplicaciones inteligentes y seguras:

*   **Desarrollo Rápido de Agentes de IA**: Prototipar y depurar agentes complejos (como `agent_search.py`) que requieren múltiples interacciones con el LLM, aprovechando la baja latencia de la ejecución local.
*   **Herramientas Internas y Asistentes de Código**: Crear herramientas para equipos de desarrollo que ayuden a generar código, refactorizar, explicar fragmentos complejos o buscar en la documentación interna, todo sin que el código fuente salga de la red local.
*   **Análisis y Resumen de Documentos Confidenciales**: Construir aplicaciones que procesen documentos sensibles (informes financieros, legales, médicos) de forma segura, garantizando que ninguna información se envíe a servicios en la nube.
*   **Aplicaciones "Offline-First"**: Desarrollar aplicaciones que puedan funcionar sin conexión a internet, ya que el motor de inferencia principal reside en la máquina local.
*   **Educación e Investigación**: Aprender sobre el funcionamiento de los LLMs, la ingeniería de prompts y la arquitectura de agentes en un entorno controlado y sin coste por uso.

## ✨ Capacidades y Beneficios de esta Arquitectura



*   **Privacidad y Seguridad de Datos**: Al ejecutarse el modelo de forma local, toda la información procesada, incluyendo prompts y respuestas, permanece en tu máquina. Esto es fundamental para manejar datos sensibles, código propietario o información personal.

*   **Reducción de Costes**: Elimina la dependencia de APIs de pago por uso. El coste se limita a la inversión inicial en hardware y el consumo eléctrico, permitiendo un uso intensivo y experimentación sin preocuparse por la factura del servicio.

*   **Baja Latencia y Alto Rendimiento**: La ejecución local, especialmente con la aceleración por GPU que facilita el "Docker Model Runner", ofrece tiempos de respuesta casi instantáneos en comparación con las llamadas a APIs remotas, lo que es crucial para aplicaciones interactivas.

*   **Control y Personalización Total**: Tienes control absoluto sobre la versión del modelo, la configuración del servidor y el entorno de ejecución. Permite una personalización que los proveedores de API no ofrecen.

*   **Funcionamiento sin Conexión**: El núcleo de la funcionalidad del LLM no requiere una conexión a internet, lo que habilita el desarrollo de aplicaciones robustas que pueden operar en entornos con conectividad limitada o nula (la búsqueda web del agente sí requiere internet).

*   **Despliegue Simplificado con Docker**: El "Docker Model Runner" abstrae la complejidad de configurar y ejecutar motores de inferencia, permitiendo a los desarrolladores centrarse en la aplicación en lugar de en la infraestructura del modelo.



## 👤 Contacto del Desarrollador



Este proyecto fue desarrollado por:



*   **Nombre:** Edwin Quintero Alzate

*   **GitHub:** [Edwin1719](https://github.com/Edwin1719)

*   **LinkedIn:** [Edwin Quintero Alzate](https://www.linkedin.com/in/edwinquintero0329/)

*   **Email:** databiq29@gmail.com



---

*Este README fue generado para documentar la arquitectura y el funcionamiento del proyecto de agente local.*


