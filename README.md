📌 Overview
This project implements a voice-driven Interactive Voice Response (IVR) bot. It uses OpenAI's Whisper model to transcribe user speech, sends the transcription to a backend intent prediction API, and speaks back the bot response using a text-to-speech engine. Additionally, it logs all queries and responses for audit and analysis.

🧩 Key Components
speech_recognition: Captures audio input from the microphone.

pyttsx3: Converts bot response text into speech (TTS).

whisper: Transcribes speech into text using OpenAI’s Whisper model.

requests: Sends the transcribed query to the backend Flask API.

pandas: Stores logs (queries, responses, timestamps) into CSV format.

torch: Required by Whisper for model inference.

logging: Used to log errors and operational events.

🔁 End-to-End Flow
User speaks into the microphone.

Audio is captured using the speech_recognition library.

The audio is saved as a temporary WAV file.

The Whisper model transcribes this audio into text.

Transcribed text is sent to the /predict_intent API.

The backend returns detected intent, confidence score, and a response.

The response is spoken back using pyttsx3.

The entire session is logged into a CSV file and a log file.

🧭 Flow Diagram
plaintext
Copy
Edit
🎙️ Voice Input
        ↓
🔊 Audio Captured (speech_recognition)
        ↓
🧠 Whisper Transcription (OpenAI Whisper)
        ↓
🌐 Send to API (/predict_intent via requests)
        ↓
📦 API Returns Intent & Response
        ↓
🗣️ Text-to-Speech (pyttsx3)
        ↓
📝 Log to CSV + Logging Module
🚀 Running Locally
Install Python 3.8+.

Install FFmpeg and update the FFMPEG_PATH in your script.

Clone the repo and create a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the script:

bash
Copy
Edit
python voice_bot.py
📮 Testing the API with Postman
Ensure your backend Flask app is running and accessible at http://localhost:5000/predict_intent.

Open Postman and create a new POST request to:

bash
Copy
Edit
http://localhost:5000/predict_intent
In the Body, select raw → JSON and paste:

json
Copy
Edit
{
  "query": "transfer money"
}
Send the request and observe the intent, confidence, and response in the returned JSON.

📦 requirements.txt
nginx
Copy
Edit
SpeechRecognition
pyttsx3
requests
pandas
whisper
torch
numpy
📁 Logs
Voice/audio logs: Stored as temporary WAV files.

CSV logs: Stored at D:/IVR Case-02/ivr_log.csv.

Text logs: Stored in D:/IVR Case-02/splunk.log.
