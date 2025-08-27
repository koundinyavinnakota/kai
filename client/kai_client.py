import os
import subprocess
import requests
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# ===== Settings =====
SAMPLE_RATE = 16000
BLOCK_SECONDS = 5
SERVER_URL = os.getenv("KAI_SERVER_URL", "http://localhost:8000/chat")

# TTS config (macOS 'say'); list voices with:  say -v "?"
KAI_VOICE = os.getenv("KAI_VOICE", "Samantha")  # e.g., "Samantha", "Ava", "Alex", "Victoria"
KAI_RATE  = os.getenv("KAI_RATE", "190")        # words per minute

# ===== STT (Whisper) =====
stt = WhisperModel("base.en", device="cpu", compute_type="int8")

def transcribe(np_audio):
    segments, _ = stt.transcribe(np_audio, language="en")
    return "".join([s.text for s in segments]).strip()

# ===== TTS (macOS 'say') =====
def speak(text: str):
    if not text:
        return
    text = " ".join(text.split())
    try:
        subprocess.run(["say", "-v", KAI_VOICE, "-r", KAI_RATE, text], check=False)
    except FileNotFoundError:
        print("(TTS error) 'say' not found. Are you on macOS?")
    except Exception as e:
        print(f"(TTS error) {e}")

# ===== Record mic (push-to-talk) =====
def record_block(seconds=BLOCK_SECONDS):
    print("🎤 Speak now… (press Enter to start, 'q' then Enter to quit)")
    audio = sd.rec(int(seconds * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def main():
    print("KAI ready. Press ENTER to talk; type 'q' and ENTER to quit.")
    while True:
        cmd = input()
        if cmd.strip().lower() == "q":
            print("Bye!")
            break

        audio = record_block()
        text = transcribe(audio)
        if not text:
            print("(didn't catch that)")
            continue

        print("You:", text)
        try:
            r = requests.post(SERVER_URL, json={"text": text}, timeout=60)
            r.raise_for_status()
            reply = r.json().get("reply", "").strip()
        except Exception as e:
            reply = f"Request failed: {e}"

        print("KAI:", reply)
        speak(reply)

if __name__ == "__main__":
    main()
