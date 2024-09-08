import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import asyncio
from dotenv import load_dotenv
import pyperclip
import pygame
import customtkinter as ctk
import threading
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
    LiveResultResponse,
)

load_dotenv()

# Налаштування SSL для macOS
ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ['SSL_CERT_FILE'] = certifi.where()

# Налаштування логування
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Налаштування файлового логування для детального відстеження
file_handler = logging.FileHandler("voicett_live.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Налаштування обробки помилок
def log_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Виникла помилка в {func.__name__}: {str(e)}")
            raise
    return wrapper

pygame.mixer.init()

TRANSCRIPT_FILE = "transcriptions.txt"

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []
        self.last_part = ""

    def add_part(self, part):
        # Видаляємо повторення на початку нової частини
        if self.last_part and part.startswith(self.last_part):
            part = part[len(self.last_part):].strip()
        
        if part:
            self.transcript_parts.append(part)
            self.last_part = part

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()

def play_sound():
    sound_file = "notification-clicking-joshua-chivers-1-1-00-00.mp3"
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Не вдалося відтворити звук: {e}")

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VoiceTT-Live Transcription")
        self.geometry("600x400")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.text_area = ctk.CTkTextbox(self, wrap="word", font=("Arial", 14))
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.start_transcription()
        
    def start_transcription(self):
        threading.Thread(target=self.run_transcription, daemon=True).start()
        
    def run_transcription(self):
        asyncio.run(get_transcript(self))
        
    def update_transcript(self, text):
        self.text_area.insert("end", text + "\n\n")
        self.text_area.see("end")
        self.write_to_file(text)
        
    def write_to_file(self, text):
        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as file:
            file.write(text + "\n\n")

@log_exceptions
async def get_transcript(app):
    microphone = None
    dg_connection = None
    try:
        logger.info("Починаємо процес транскрипції")
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)

        dg_connection = deepgram.listen.asyncwebsocket.v("1")
        logger.debug("WebSocket з'єднання встановлено")

        @log_exceptions
        async def on_message(self, result):
            if not isinstance(result, LiveResultResponse):
                return

            if result.type == "Results" and result.channel.alternatives:
                sentence = result.channel.alternatives[0].transcript
                if not result.speech_final:
                    transcript_collector.add_part(sentence)
                    logger.debug(f"Проміжна транскрипція: {sentence}")
                else:
                    transcript_collector.add_part(sentence)
                    full_sentence = transcript_collector.get_full_transcript()
                    if len(full_sentence.strip()) > 0:
                        full_sentence = full_sentence.strip()
                        logger.info(f"Фінальна транскрипція: {full_sentence}")
                        app.update_transcript(full_sentence)
                        pyperclip.copy(full_sentence)
                        play_sound()
                        transcript_collector.reset()

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="uk",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=800,
            smart_format=True,
        )

        await dg_connection.start(options)

        microphone = Microphone(dg_connection.send)
        microphone.start()

        logger.info("Listening...")

        while True:
            await asyncio.sleep(1)

    except Exception as e:
        app.update_transcript(f"Error: {e}")
    finally:
        microphone.finish()
        await dg_connection.finish()

if __name__ == "__main__":
    app = Application()
    app.mainloop()