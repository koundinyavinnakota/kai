from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, requests

app = FastAPI(title="KAI Server (Groq LLM)")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # try 8B first; you can switch to 70B later

SYSTEM_PROMPT = "You are KAI, a concise, helpful personal AI assistant. Keep answers short unless asked for detail."

class ChatIn(BaseModel):
    text: str

class ChatOut(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL, "has_key": bool(GROQ_API_KEY)}

@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY (check your .env and docker-compose).")
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.text},
        ],
        "temperature": 0.3,
    }
    try:
        r = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
        if not r.ok:
            # Surface Groq’s message so we see exactly why (wrong model name, bad key, etc.)
            raise HTTPException(status_code=r.status_code, detail=f"Groq error: {r.text}")
        data = r.json()
        return ChatOut(reply=data["choices"][0]["message"]["content"].strip())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
