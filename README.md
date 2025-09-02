# KAI — Personal Voice AI Assistant

KAI listens to your mic 🎤, transcribes speech with Whisper, sends text to a **Groq-hosted LLM**, and **talks back** using macOS TTS.

- 🎤 **STT**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- 🧠 **LLM**: [Groq API](https://groq.com) (LLaMA-3 models, free tier available)
- 🗣️ **TTS**: macOS `say` (voice + rate configurable)
- 🐳 **Server**: FastAPI in Docker
- 🔒 **Secrets**: `.env` (never commit real keys)

---

## Architecture

- [You] → mic → client (Whisper) → POST /chat → server (FastAPI → Groq) → reply → client → macOS TTS → speakers


---

## Prerequisites

- macOS (for `say` TTS; Linux/Windows needs another TTS engine)
- Python 3.10+
- Docker Desktop *or* Colima
- A Groq API key (get one from your Groq dashboard)

---

## Quick Start

```bash
# 1. Clone & set up virtualenv
git clone https://github.com/<yourname>/kai.git
cd kai
python3 -m venv ~/.venvs/kai
source ~/.venvs/kai/bin/activate

# 2. Install dependencies
pip install -r server/requirements.txt
pip install -r client/requirements.txt

# 3. Configure environment (local only, never commit)
cp .env.example .env
# edit .env and set:
# GROQ_API_KEY=sk_your_groq_key
# GROQ_MODEL=llama3-70b-8192

# 4. Start server (Docker)
docker compose up -d --build
curl -s -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"text":"hello"}'

# 5. Run voice client
python client/kai_client.py
# Press ENTER to talk, 'q' to quit.
```

## Configuration

```bash
GROQ_API_KEY=sk_your_groq_key_here
GROQ_MODEL=llama3-70b-8192
```

## TTS settings
```bash
say -v "?"
# Pick One

export KAI_VOICE=Samantha
export KAI_RATE=190
```

## Files & Folders

```bash
server/
  main.py             # FastAPI → Groq API
  requirements.txt
client/
  kai_client.py       # mic → Whisper → /chat → TTS
  requirements.txt
docker-compose.yml    # builds/runs kai-server
.env.example          # placeholder env vars
README.md             # this file

```

# 🛠 Instructions to Run KAI

## 1. Clone & enter repo

```bash
git clone https://github.com/<yourname>/kai.git
cd kai
```

---

## 2. Create & activate Python virtual environment

```bash
python3 -m venv ~/.venvs/kai
source ~/.venvs/kai/bin/activate
```

---

## 3. Install dependencies

### Server

```bash
pip install -r server/requirements.txt
```

### Client

If you don’t already have it, create `client/requirements.txt`:

```bash
cat > client/requirements.txt <<'REQ'
faster-whisper
sounddevice
numpy
requests
pyttsx3
REQ
```

Then install:

```bash
pip install -r client/requirements.txt
```

---

## 4. Add your Groq API key

Copy the example env and edit:

```bash
cp .env.example .env
nano .env
```

Inside `.env`, add:

```
GROQ_API_KEY=sk_your_groq_key_here
GROQ_MODEL=llama3-70b-8192
```

Save and exit (`CTRL+O`, `Enter`, `CTRL+X` in nano).

---

## 5. Start the server

### Option A — Docker (recommended)

Start Docker Desktop or Colima, then:

```bash
docker compose up -d --build
```

Check it’s working:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"text":"Say hi in five words"}'
```

You should see a JSON reply.

### Option B — No Docker (dev mode)

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

---

## 6. Run the client (voice)

In a terminal with your venv active:

```bash
python client/kai_client.py
```

* Press **Enter** → speak for \~5 seconds
* KAI will **transcribe** your speech and **speak back** using macOS TTS
* Type **q** + Enter to quit

---

## 7. Optional: configure TTS voice & rate

List voices available:

```bash
say -v "?"
```

Pick one and set it before running the client:

```bash
export KAI_VOICE=Samantha
export KAI_RATE=190
python client/kai_client.py
```

---

# ✅ Quick Summary

1. Clone repo
2. Setup venv & install requirements
3. Put Groq key in `.env`
4. Run server (`docker compose up -d --build`)
5. Run client (`python client/kai_client.py`)
6. Talk to KAI 🎤 → it talks back 🗣️

---

