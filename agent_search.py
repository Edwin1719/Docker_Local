import os
import requests
import json
import re
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
URL = os.getenv("MODEL_URL")
MODELO = os.getenv("MODEL_NAME")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def buscar_en_web(consulta):
    print(f"\n[HERRAMIENTA]: Buscando datos clave...")
    try:
        # Limitamos a 2 resultados para asegurar que el modelo no se bloquee por tokens
        search_result = tavily.search(query=consulta, search_depth="basic", max_results=2)
        contexto = ""
        for r in search_result['results']:
            # Solo tomamos los primeros 1000 caracteres de cada resultado
            contexto += f"\n- FUENTE: {r['url']}\n  DATO: {r['content'][:1000]}\n"
        return contexto
    except Exception as e: return f"Error: {e}"

def agente_bi_ligero(pregunta_usuario):
    # Forzamos al modelo a ser breve para ahorrar tiempo de cómputo
    system_prompt = (
        "Eres un consultor experto. Responde de forma técnica y muy concisa.\n"
        "Si necesitas buscar: ACCION: BUSCAR['termino']\n"
        "Si respondes: REPORTE: [Resumen en viñetas]"
    )

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": pregunta_usuario}]

    try:
        # Timeout de 180s y temperatura 0
        response = requests.post(URL, json={"model": MODELO, "messages": messages, "temperature": 0}, timeout=180)
        respuesta_ia = response.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"Error fase 1: {e}"

    match_buscar = re.search(r"ACCION:\s*BUSCAR\s*\[['\"](.+?)['\"]\]", respuesta_ia, re.IGNORECASE)

    if match_buscar:
        datos = buscar_en_web(match_buscar.group(1))
        print("[PROCESANDO]: Sintetizando reporte...")
        
        messages.append({"role": "assistant", "content": respuesta_ia})
        messages.append({"role": "user", "content": f"DATOS:\n{datos}\nGenera un reporte breve en viñetas."})
        
        try:
            # Segunda llamada con temperatura baja
            final_res = requests.post(URL, json={"model": MODELO, "messages": messages, "temperature": 0}, timeout=180)
            return final_res.json()["choices"][0]["message"]["content"]
        except Exception as e: return f"Error final (Timeout): {e}. El modelo 14B es muy lento para tu hardware actual."

    return respuesta_ia

if __name__ == "__main__":
    print("\n" + "="*50 + "\nMODO LIGERO ACTIVADO\n" + "="*50)
    pregunta = input("\nPregunta: ")
    print("\n" + agente_bi_ligero(pregunta))