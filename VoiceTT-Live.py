import os
# Приховування повідомлень pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import asyncio
from dotenv import load_dotenv
import pyperclip
import pygame
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

# Ініціалізація pygame для відтворення звуку
pygame.mixer.init()

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

async def get_transcript():
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
                    print(f"{full_sentence}")
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

        print("Listening...")

        # Keep the connection open indefinitely
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Could not open socket: {e}")
    finally:
        microphone.finish()
        await dg_connection.finish()

if __name__ == "__main__":
    # Вимкнення виведення для pygame
    pygame.mixer.set_num_channels(0)
    
    asyncio.run(get_transcript())