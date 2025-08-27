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
