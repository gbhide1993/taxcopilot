import requests


OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "phi:latest"

def generate_answer(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "num_predict": 300,
            "temperature": 0.2,
            "repeat_penalty": 1.1
            
        }
    )

    if response.status_code != 200:
        raise Exception("LLM generation failed")

    return response.json()["response"]
