import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load voice setting from .env
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# 🧹 Clean text to avoid awkward TTS reads (e.g., asterisks)
def clean_for_speech(text: str) -> str:
    replacements = {
        "*": "",
        "•": "",
        "#": "",
        ">": "",
        "\t": " ",
        "  ": " "
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    return text.strip()

# 🎙 Generate speech audio from cleaned text
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

# 🔊 Play the generated audio using pygame
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)
            return True
        except Exception as e:
            print(f"Error in TTS: {e}")
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")

# 🗣 Speak full or summarized text based on sentence and character count
def TextToSpeech(Text, func=lambda r=None: True):
    if not Text or not isinstance(Text, str) or Text.strip() == "":
        return

    Data = str(Text).split(".")  # Split text into sentences
    Text = Text.strip()

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "The rest of the text is now on the chat screen, please check it.",
        "You can see the rest of the text on the chat screen.",
        "The remaining part of the text is now on the chat screen.",
        "You’ll find more text on the chat screen to view.",
        "The rest of the answer is now on the chat screen.",
        "Please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen.",
        "The next part of the text is on the chat screen.",
        "Please check the chat screen for more information.",
        "There's more text on the chat screen for you.",
        "Take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen.",
        "Check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text.",
        "There's more to see on the chat screen, please look.",
        "The chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out.",
        "Please review the chat screen for the rest of the text.",
        "Look at the chat screen for the complete answer."
    ]

    # 🔁 Speak first 2 sentences and suggest checking chat if text is long
    if len(Data) > 4 and len(Text) >= 250:
        preview = ". ".join(Text.split(".")[0:2]).strip() + ". " + random.choice(responses)
        TTS(clean_for_speech(preview), func)
    else:
        TTS(clean_for_speech(Text), func)

# 🔁 For direct testing via terminal
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
