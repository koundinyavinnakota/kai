from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import webbrowser, datetime, re

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
    tool_result = tool_router(req.text)
    if tool_result:
        return ChatOut(reply=tool_result)
    # else fall back to LLM (existing code)

    reply = ollama_chat(req.text)
    return ChatOut(reply=reply)

def tool_router(text: str) -> str:
    t = text.lower().strip()
    if any(k in t for k in ["time", "current time"]):
        return datetime.datetime.now().strftime("It's %I:%M %p.")
    if t.startswith("open "):
        target = t.split("open ", 1)[1]
        url = target if target.startswith("http") else f"https://{target}"
        # Server is in Docker; just return a message (client can't open browser).
        # Later: send a "command" back and let the client open it.
        return f"(Client should open) {url}"
    if t.startswith("calc "):
        expr = t[5:]
        if not re.fullmatch(r"[0-9\.\+\-\*\/\%\(\) ]+", expr):
            return "Only digits and math ops allowed."
        return str(eval(expr))
    return None
