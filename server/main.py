from fastapi import FastAPI
from pydantic import BaseModel
import os, requests

app = FastAPI(title="KAI Server (Groq LLM)")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")  # or llama3-8b-8192

SYSTEM_PROMPT = "You are KAI, a concise, helpful personal AI assistant. Keep answers short unless asked for detail."

class ChatIn(BaseModel):
    text: str

class ChatOut(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn):
    if not GROQ_API_KEY:
        return ChatOut(reply="Server misconfigured: missing GROQ_API_KEY.")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.text},
        ],
        "temperature": 0.3,
    }
    r = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    data = r.json()
    return ChatOut(reply=data["choices"][0]["message"]["content"].strip())
