import speech_recognition as sr
try:
    print("Available microphones:", sr.Microphone.list_microphone_names())
    for index in [1, 3, 8, 18, 25]:  # Test likely indices
        print(f"\nTesting microphone index {index}")
        with sr.Microphone(device_index=index) as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            print(f"Speak something (e.g., transfer money) for index {index}...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            with open(f"test_audio_index_{index}.wav", "wb") as f:
                f.write(audio.get_wav_data())
            print(f"Audio saved as test_audio_index_{index}.wav")
except Exception as e:
    print(f"Error with index {index}: {e}")