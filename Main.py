from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read().strip()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as db_file:
                    db_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json not found. Creating a new one.")
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            json.dump([], file)

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    
    for i, entry in enumerate(json_data):
        role = entry.get("role", "")
        content = entry.get("content", "")

        if role == "user":
            formatted_chatlog += f"{Username}: {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname}: {content}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            data = file.read()
        
        if data.strip():
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as resp_file:
                resp_file.write(data)
    except FileNotFoundError:
        print("Database.data not found.")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def CleanAssistantAnswer(answer: str) -> str:
    return "\n".join([line.strip() for line in answer.splitlines() if line.strip() != ""])

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    SetAssistantStatus("Listening...")

    Query = SpeechRecognition()
    if Query is None:
        print("No input detected. Please try again.")
        return

    Query = Query.strip()
    ShowTextToScreen(f"{Username}: {Query}\n")  # ← Only 1 newline (no visual gap)
    SetAssistantStatus("Thinking...")

    Decision = FirstLayerDMM(Query)

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            if "play" in queries:
                print("Pausing microphone to prevent unwanted commands during video playback...")
                SetMicrophoneStatus("False")
                run(Automation(list(Decision)))
                sleep(10)
                print("Resuming microphone after video playback...")
                SetMicrophoneStatus("True")
            else:
                run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
            f.write(f"{ImageGenerationQuery}, True")
        subprocess.Popen(["python", "Backend/ImageGeneration.py"])

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        Answer = CleanAssistantAnswer(Answer)
        ShowTextToScreen(f"\n{Assistantname}: {Answer.strip()}")  # ← Only 1 newline
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                Answer = CleanAssistantAnswer(Answer)
                ShowTextToScreen(f"{Assistantname}: {Answer.strip()}\n")  # ← Only 1 newline
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                Answer = CleanAssistantAnswer(Answer)
                ShowTextToScreen(f"{Assistantname}: {Answer.strip()}\n")  # ← Only 1 newline
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                Answer = CleanAssistantAnswer(Answer)
                ShowTextToScreen(f"{Assistantname}: {Answer.strip()}\n")  # ← Only 1 newline
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            if "Available..." not in GetAssistantStatus():
                SetAssistantStatus("Available...")
        sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
