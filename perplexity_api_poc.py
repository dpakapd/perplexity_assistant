import os
import struct
import pyaudio
import pvporcupine
import speech_recognition as sr
import openai
from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS
import pygame
import time
import wave

# --- Configuration ---
load_dotenv()
PICOVOICE_ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
KEYWORD_PATHS = ["Krishna_en_raspberry-pi_v3_0_0.ppn"]
MODEL_NAME = "sonar"
PERPLEXITY_API_BASE_URL = "https://api.perplexity.ai"

# --- Sanity Checks ---
if not all([PICOVOICE_ACCESS_KEY, PERPLEXITY_API_KEY]):
    print("FATAL ERROR: An API key is missing from the .env file.")
    exit()
if not os.path.exists(KEYWORD_PATHS[0]):
    print(f"FATAL ERROR: Wake word file '{KEYWORD_PATHS[0]}' not found.")
    exit()

# --- Initialize Perplexity Client ---
try:
    perplexity_client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_API_BASE_URL)
except Exception as e:
    print(f"FATAL ERROR: Could not initialize Perplexity client: {e}")
    exit()

# --- Text-to-Speech Function ---
def speak_text(text_to_speak, lang='en'):
    print(f"Assistant (speaking): {text_to_speak}")
    try:
        pygame.mixer.init()
        tts = gTTS(text=text_to_speak, lang=lang, slow=False)
        mp3_filename = "response_audio.mp3"
        tts.save(mp3_filename)
        pygame.mixer.music.load(mp3_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        os.remove(mp3_filename)
    except Exception as e:
        print(f"Error in Text-to-Speech: {e}")

# --- Main Application ---
def main():
    porcupine = None
    paudio = None
    audio_stream = None
    recognizer = sr.Recognizer()

    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=KEYWORD_PATHS
        )
        paudio = pyaudio.PyAudio()
        audio_stream = paudio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Assistant is ready. Listening for 'Krishna'...")
        speak_text("Assistant is ready.")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("Wake word detected!")
                speak_text("Yes?")
                
                # --- Record command from the same audio stream ---
                frames = []
                print("Listening for command...")
                # You have ~10 seconds to speak after saying "Yes?"
                for _ in range(0, int(porcupine.sample_rate / porcupine.frame_length * 10)):
                    frames.append(audio_stream.read(porcupine.frame_length))
                
                # Convert the recorded frames into audio data SpeechRecognition can use
                audio_data = sr.AudioData(b"".join(frames), porcupine.sample_rate, paudio.get_sample_size(pyaudio.paInt16))
                
                try:
                    print("Recognizing command...")
                    command = recognizer.recognize_google(audio_data)
                    print(f"You (command): {command}")

                    if command.lower().strip() in ["exit", "quit", "goodbye", "stop"]:
                        speak_text("Goodbye!")
                        break

                    messages = [{"role": "system", "content": "You are an AI assistant. You are located in Twinsburg, Ohio. All answers must be relevant to Cleveland, Ohio unless asked for differently by the user.  You MUST answer all questions in a single and VERY concise sentence. "
                "Do not elaborate. Do not ask follow-up questions. If a question is complex, provide the most direct and simple summary possible in one sentence. "
                "For conversational greetings, respond simply. For example, if asked 'how are you?', respond 'I am always fine.'"}]
                    messages.append({"role": "user", "content": command})
                    
                    print("Processing your request...")
                    response = perplexity_client.chat.completions.create(model=MODEL_NAME, messages=messages)
                    assistant_response_text = response.choices[0].message.content.strip()
                    speak_text(assistant_response_text)

                except sr.UnknownValueError:
                    speak_text("Sorry, I didn't catch that.")
                except sr.RequestError as e:
                    speak_text("Speech recognition service is unavailable.")
                except openai.APIError as e:
                    speak_text("Sorry, I had an issue with the Perplexity service.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    speak_text("Sorry, an unexpected error occurred.")
                
                print("\nReturning to wake word listening...")

    except KeyboardInterrupt:
        print("Stopping assistant.")
    finally:
        if audio_stream is not None: audio_stream.close()
        if paudio is not None: paudio.terminate()
        if porcupine is not None: porcupine.delete()
        print("Cleanup complete.")

if __name__ == '__main__':
    main()
