import streamlit as st
import os
import requests
import json
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Generator

# --- Configuración de la Página ---
st.set_page_config(page_title="Agente BI Avanzado", layout="wide", page_icon="🚀")

# --- Lógica de Carga y Configuración del Backend ---
@st.cache_resource
def load_resources():
    """Carga las variables de entorno y los clientes necesarios de forma segura."""
    load_dotenv()
    config = {
        "tavily_api_key": os.getenv("TAVILY_API_KEY"),
        "model_url": os.getenv("MODEL_URL"),
        "model_name": os.getenv("MODEL_NAME"),
    }
    if not all(config.values()):
        st.error("Una o más variables de entorno no están configuradas. Revisa tu archivo .env.")
        st.stop()
    return config, TavilyClient(api_key=config["tavily_api_key"])

config, tavily_client = load_resources()

# --- Funciones del Agente (Backend) ---
def buscar_en_web(consulta: str) -> str:
    """Realiza una búsqueda web y devuelve un contexto resumido."""
    try:
        search_result = tavily_client.search(query=consulta, search_depth="basic", max_results=3)
        return "\n".join([f"- FUENTE: {r['url']}\n  DATO: {r['content'][:800]}" for r in search_result['results']])
    except Exception as e:
        return f"Error en búsqueda web: {e}"

def invocar_agente(messages: list) -> Generator[str, None, None]:
    """
    Función principal que orquesta la lógica del agente y devuelve la respuesta en streaming.
    """
    # --- NUEVO SYSTEM PROMPT ---
    system_prompt = """
    Eres un consultor de Business Intelligence experto y autónomo. Tu objetivo es proporcionar respuestas precisas, técnicas y actualizadas.

    **Tus Reglas de Operación:**
    1.  **Evalúa la Pregunta**: Determina si la pregunta requiere información en tiempo real o muy reciente.
    2.  **Decide Cuándo Buscar**:
        *   **DEBES** buscar para noticias, eventos recientes, o datos que cambian con el tiempo.
        *   **NO DEBES** buscar para preguntas generales, conceptuales o creativas. Usa tu conocimiento interno.

    **Formato de Salida Obligatorio:**
    *   Si decides buscar, tu única respuesta debe ser en dos líneas:
        ACCION: BUSCAR
        TERMINO: término de búsqueda
    *   Si decides responder directamente, tu respuesta debe empezar con: `REPORTE:`
    """
    
    if not messages:
        return
        
    decision_messages = [
        {"role": "system", "content": system_prompt},
        messages[-1] # Solo la última pregunta del usuario para la decisión
    ]

    try:
        response = requests.post(config["model_url"], json={"model": config["model_name"], "messages": decision_messages, "temperature": 0}, timeout=60)
        response.raise_for_status()
        respuesta_ia = response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        yield f"REPORTE: Error de conexión con el modelo LLM: {e}"
        return

    # --- NUEVA LÓGICA DE PROCESAMIENTO (SIN REGEX) ---
    if "ACCION: BUSCAR" in respuesta_ia:
        termino_busqueda = ""
        try:
            for line in respuesta_ia.split('\n'):
                if line.strip().startswith("TERMINO:"):
                    termino_busqueda = line.split(":", 1)[1].strip()
                    break
        except Exception:
            yield "REPORTE: El agente intentó buscar pero su respuesta no tuvo el formato esperado (TERMINO:)."
            return

        if not termino_busqueda:
            yield "REPORTE: El agente decidió buscar pero no especificó un término de búsqueda."
            return

        with st.status(f"🔎 Buscando en la web: '{termino_busqueda}'...", state="running", expanded=False):
            datos = buscar_en_web(termino_busqueda)
            st.write(f"Contexto encontrado:\n{datos[:500]}...")
        
        synthesis_messages = [{"role": "system", "content": system_prompt}] + messages
        synthesis_messages.append({"role": "assistant", "content": respuesta_ia})
        synthesis_messages.append({"role": "user", "content": f"DATOS:\n{datos}\nGenera un reporte breve en viñetas."})

        try:
            with requests.post(config["model_url"], stream=True, json={"model": config["model_name"], "messages": synthesis_messages, "temperature": 0.1}, timeout=180) as r:
                r.raise_for_status()
                for chunk in r.iter_lines():
                    if chunk:
                        decoded_line = chunk.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            try:
                                json_data = json.loads(decoded_line[6:])
                                content = json_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                pass
        except requests.exceptions.RequestException as e:
            yield f"REPORTE: Error de conexión en la fase de síntesis: {e}"

    else:
        # Si no hay "ACCION: BUSCAR", se devuelve la respuesta directamente.
        yield respuesta_ia


# --- Interfaz de Usuario (Frontend) ---
st.header("🤖 Agente BI Avanzado", divider='rainbow')

with st.sidebar:
    st.title("🚀 Agente BI Avanzado")
    st.info(f"**Modelo en uso:**\n`{config['model_name']}`")
    st.markdown("---")
    st.markdown("Este agente puede responder tus preguntas y, si es necesario, realizará búsquedas en la web para obtener información actualizada.")
    st.code("- ¿Cuáles son las últimas tendencias en IA para 2025?", language=None)
    st.code("- Resume las noticias económicas más importantes de esta semana.", language=None)
    st.markdown("---")
    if st.button("🗑️ Limpiar Historial del Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_generator = invocar_agente(st.session_state.messages)
        full_response = st.write_stream(response_generator)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})