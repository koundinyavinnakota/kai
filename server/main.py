from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

app = FastAPI(title="KAI Server (Local LLM via Ollama)")

class ChatIn(BaseModel):
    text: str

class ChatOut(BaseModel):
    reply: str

SYSTEM_PROMPT = "You are KAI, a concise, helpful assistant. Keep answers short unless asked for detail."

def ollama_chat(user_text: str) -> str:
    # streaming=false for simplicity
    r = requests.post(f"{OLLAMA_URL}/v1/chat/completions", json={
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.3,
    }, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn):
    # (Optional: call your tool_router here first, then fallback)
    reply = ollama_chat(req.text)
    return ChatOut(reply=reply)
