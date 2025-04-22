import speech_recognition as sr
import pyttsx3
import requests
import pandas as pd
import logging
import whisper
import os
import subprocess

# Configuration
API_URL = "http://localhost:5000/predict_intent"
LOG_FILE = "D:/IVR Case-02/splunk.log"
CSV_LOG = "D:/IVR Case-02/ivr_log.csv"
WHISPER_MODEL = "base"  # Options: tiny, base, small
MICROPHONE_INDEX = 1  # Try 1, 3, 8, 18, or 25 based on test_mic_select.py
USE_MANUAL_INPUT = False  # Set to True to bypass STT
FFMPEG_PATH = r"D:/IVR Case-02/ffmpeg/bin/ffmpeg.exe"

# Check and update PATH
if os.path.exists(FFMPEG_PATH):
    ffmpeg_dir = os.path.dirname(FFMPEG_PATH)
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ FFmpeg path added to PATH: {ffmpeg_dir}")
else:
    print("❌ FFmpeg path is INVALID. Please check the FFMPEG_PATH.")
    
# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Text-to-Speech
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        logger.info(f"TTS: {text}")
    except Exception as e:
        print(f"❌ TTS error: {e}")
        logger.error(f"TTS error: {e}")

# Speech-to-Text with OpenAI Whisper
def listen():
    if USE_MANUAL_INPUT:
        query = input("Enter query (e.g., transfer money): ")
        if query:
            print(f"🗣️ You said: {query}")
            logger.info(f"Transcribed query: {query}")
            return query
        return None

    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=MICROPHONE_INDEX) as source:
            print("🎙️ Listening... Speak now.")
            print("Available microphones:", sr.Microphone.list_microphone_names())
            r.adjust_for_ambient_noise(source, duration=2)
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=10)
                logger.info("Audio captured successfully")
            except sr.WaitTimeoutError:
                print("⏳ No speech detected within timeout.")
                logger.warning("No speech detected within timeout")
                return None
            except Exception as e:
                print(f"❌ Audio capture error: {e}")
                logger.error(f"Audio capture error: {e}")
                return None
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        logger.error(f"Microphone error: {e}")
        return None

    # Save audio to WAV
    try:
        audio_file = "temp_audio.wav"
        with open(audio_file, "wb") as f:
            f.write(audio.get_wav_data())
        logger.info(f"Audio saved to {audio_file}")
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            print(f"❌ Audio file {audio_file} is missing or empty.")
            logger.error(f"Audio file {audio_file} is missing or empty")
            return None
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        logger.error(f"Error saving audio: {e}")
        return None

    # Whisper transcription
    try:
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(audio_file, fp16=False)
        query = result["text"].strip()
        if query:
            print(f"🗣️ You said: {query}")
            logger.info(f"Transcribed query: {query}")
            return query
        else:
            print("😕 Could not understand.")
            logger.warning("Speech recognition failed: No text recognized")
            return None
    except Exception as e:
        print(f"❌ STT error: {e}")
        logger.error(f"STT error: {e}")
        return None

# Talk to Flask API and log results
def ask_bot():
    query = listen()
    if not query:
        speak("Sorry, I didn't catch that.")
        return

    payload = {"query": query}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        intent = result.get("intent", "Unknown")
        confidence = result.get("confidence", 0.0)
        bot_response = result.get("response", f"I understood your intent as {intent}.")

        print(f"🤖 Bot: {bot_response}")
        speak(bot_response)

        # Log to CSV
        message = {
            "query": query,
            "intent": intent,
            "confidence": confidence,
            "response": bot_response,
            "timestamp": str(pd.Timestamp.now())
        }
        log_entry = pd.DataFrame([message])
        log_entry.to_csv(CSV_LOG, mode='a', header=not os.path.exists(CSV_LOG), index=False)
        logger.info(f"Logged to CSV: {CSV_LOG}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        speak("There was an error talking to the server.")
        logger.error(f"API call failed: {e}")

# Main loop
if __name__ == "__main__":
    while True:
        ask_bot()
        print("-" * 50)
