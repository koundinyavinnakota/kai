import os
import queue
import struct
import subprocess
import threading
import time

import numpy as np
import requests
import sounddevice as sd
from faster_whisper import WhisperModel

# ===== Settings =====
SAMPLE_RATE = 16000
BLOCK_SECONDS = 5
SERVER_URL = os.getenv("KAI_SERVER_URL", "http://localhost:8000/chat")

# Text-to-Speech (macOS 'say')
KAI_VOICE = os.getenv("KAI_VOICE", "Samantha")
KAI_RATE = os.getenv("KAI_RATE", "190")

# Speech-to-Text (Whisper)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base.en")
STT_SAMPLE_RATE = 16000      # Whisper works well at 16k
BLOCK_SECONDS = float(os.getenv("KAI_BLOCK_SECONDS", "5"))

# Wake word via Porcupine
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")  # required
KAI_WAKEWORD = os.getenv("KAI_WAKEWORD", "jarvis")        # built-in keyword name
KAI_WAKEWORD_FILE = os.getenv("KAI_WAKEWORD_FILE")        # path to custom .ppn (overrides KAI_WAKEWORD)

# =============== Initialize STT ===============
print(f"[KAI] Loading Whisper STT: {WHISPER_MODEL} …")
stt = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

def transcribe(np_audio_f32):
    # np_audio_f32: float32 in [-1,1], shape [N]
    segments, _ = stt.transcribe(np_audio_f32, language="en")
    return "".join(s.text for s in segments).strip()

# =============== TTS (macOS say) ===============
def speak(text: str):
    if not text:
        return
    text = " ".join(text.split())
    try:
        subprocess.run(["say", "-v", KAI_VOICE, "-r", KAI_RATE, text], check=False)
    except Exception as e:
        print(f"(TTS error) {e}")

# =============== Wake Word (Porcupine) ===============
def init_porcupine():
    if not PICOVOICE_ACCESS_KEY:
        raise RuntimeError(
            "Missing PICOVOICE_ACCESS_KEY. Get a free key at https://console.picovoice.ai/ "
            "and export PICOVOICE_ACCESS_KEY in your shell."
        )
    if KAI_WAKEWORD_FILE:
        print(f"[KAI] Wake word via custom file: {KAI_WAKEWORD_FILE}")
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[KAI_WAKEWORD_FILE],
        )
    else:
        print(f"[KAI] Wake word via built-in keyword: {KAI_WAKEWORD}")
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keywords=[KAI_WAKEWORD],
        )
    return porcupine

# =============== Interaction Flow ===============
def record_block(seconds=BLOCK_SECONDS, samplerate=STT_SAMPLE_RATE):
    print("🎙️  Listening… (speak your request)")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def ask_server(text: str) -> str:
    try:
        r = requests.post(SERVER_URL, json={"text": text}, timeout=60)
        r.raise_for_status()
        return r.json().get("reply", "").strip()
    except Exception as e:
        return f"Request failed: {e}"

# =============== Main (continuous wake-word) ===============
def main():
    # Wake-word engine
    porcupine = init_porcupine()
    pv_sr = porcupine.sample_rate
    frame_len = porcupine.frame_length  # number of 16-bit samples per frame

    print(f"[KAI] Wake-word ready ({'custom' if KAI_WAKEWORD_FILE else KAI_WAKEWORD}). "
          f"SampleRate={pv_sr}, FrameLen={frame_len}")
    speak("K A I is now listening. Say the wake word to begin.")

    triggered = threading.Event()

    def audio_callback(indata, frames, time_info, status):
        # indata: bytes (int16)
        if status:
            # overflow/underflow warnings
            print(f"(audio status) {status}")
        pcm = struct.unpack_from("h" * frame_len, indata)  # tuple of int16
        res = porcupine.process(pcm)
        if res >= 0:
            # Wake word detected
            triggered.set()

    try:
        with sd.RawInputStream(
            samplerate=pv_sr,
            blocksize=frame_len,
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            print("🟢 Say the wake word to start (e.g., 'Hey KAI' via custom .ppn, or 'Jarvis' if using built-in).")
            while True:
                triggered.wait()  # block until wake word
                triggered.clear()

                print("✅ Wake word detected!")
                speak("Yes?")

                # Record user request for a fixed window
                audio = record_block()
                # Resample if needed (Porcupine runs at pv_sr, Whisper we record at STT_SAMPLE_RATE)
                if pv_sr != STT_SAMPLE_RATE:
                    # should not happen in practice; both are 16k on macOS, but we guard anyway
                    audio = sd.resampling.resample(audio, pv_sr, STT_SAMPLE_RATE)

                # Ensure float32 [-1, 1]
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)

                text = transcribe(audio)
                if not text:
                    print("(no speech recognized)")
                    speak("Sorry, I didn't catch that.")
                    continue

                print("You:", text)
                reply = ask_server(text)
                print("KAI:", reply)
                speak(reply)

    except KeyboardInterrupt:
        print("\n[KAI] Stopping…")
    finally:
        if 'porcupine' in locals() and porcupine is not None:
            porcupine.delete()

if __name__ == "__main__":
    main()
