import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import asyncio
from dotenv import load_dotenv
import pyperclip
import pygame
import tkinter as tk
from tkinter import scrolledtext
import threading
from datetime import datetime
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

pygame.mixer.init()

TRANSCRIPT_FILE = "transcriptions.txt"

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

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

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VoiceTT-Live Transcription")
        self.geometry("600x400")
        
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=20)
        self.text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        self.start_button = tk.Button(self, text="Start Transcription", command=self.start_transcription)
        self.start_button.pack(pady=10)
        
    def start_transcription(self):
        self.start_button.config(state=tk.DISABLED)
        self.write_session_start()
        threading.Thread(target=self.run_transcription, daemon=True).start()
        
    def run_transcription(self):
        asyncio.run(get_transcript(self))
        
    def update_transcript(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"[{timestamp}] {text}"
        self.text_area.insert(tk.END, formatted_text + "\n")
        self.text_area.see(tk.END)
        self.write_to_file(formatted_text)
        
    def write_session_start(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_start = f"\n--- Нова сесія розпочата {timestamp} ---\n"
        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as file:
            file.write(session_start)
        self.text_area.insert(tk.END, session_start)
        self.text_area.see(tk.END)
        
    def write_to_file(self, text):
        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as file:
            file.write(text + "\n")

async def get_transcript(app):
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient("", config)

        dg_connection = deepgram.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                if len(full_sentence.strip()) > 0:
                    full_sentence = full_sentence.strip()
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
            endpointing=300,
            smart_format=True,
        )

        await dg_connection.start(options)

        microphone = Microphone(dg_connection.send)
        microphone.start()

        app.update_transcript("Listening...")

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