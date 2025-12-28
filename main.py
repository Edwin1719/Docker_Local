import requests

url = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

data = {
    "model": "ai/gemma3:4B",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "hablame en un parrafo corto sobre inteligencia artificial en el futuro para el año 2030"},
    ],
}

response = requests.post(url, json=data)
response.raise_for_status()

# Print the model's reply
print(response.json()["choices"][0]["message"]["content"])