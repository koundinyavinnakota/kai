import subprocess, requests
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
BLOCK_SECONDS = 5
SERVER_URL = "http://localhost:8000/chat"

# STT
stt = WhisperModel("base.en", device="cpu", compute_type="int8")

def transcribe(np_audio):
    segments, _ = stt.transcribe(np_audio, language="en")
    return "".join([s.text for s in segments]).strip()

def speak(text):
    subprocess.run(["say", text])

def record():
    print("🎤 Speak now… (Enter to start, q to quit)")
    while True:
        key = input()
        if key.strip().lower() == "q":
            print("Bye!"); return
        audio = sd.rec(int(BLOCK_SECONDS*SAMPLE_RATE), samplerate=SAMPLE_RATE,
                       channels=1, dtype="float32")
        sd.wait()
        text = transcribe(audio.flatten())
        if not text: 
            print("(no speech)"); continue
        print("You:", text)
        r = requests.post(SERVER_URL, json={"text": text}, timeout=60)
        reply = r.json()["reply"]
        print("Jarvis:", reply)
        speak(reply)

if __name__ == "__main__":
    record()
