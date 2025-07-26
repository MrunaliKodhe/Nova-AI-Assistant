
# 🤖 Nova AI Assistant

Nova is a modular, intelligent, voice-enabled personal assistant built in Python. It interacts via voice, understands and remembers conversations, writes documents, opens apps and websites, plays music, generates AI content (text & images), and more.

---

## 🚀 Features

- 🎤 Voice Interaction (TTS & STT)
- 🧠 Conversational Memory
- 📝 Smart Document Writing (e.g., leave applications)
- 🌐 Opens/closes apps, websites, plays YouTube music
- 🎨 AI Image Generation via Hugging Face
- 🗣️ Multiple voices with Edge TTS
- 💬 Customizable tone, accent, and language (British, American, Australian English, Hindi, Japanese, etc.)
- 💡 Smart replies powered by Cohere & Groq

---

## 🛠️ Setup Instructions

### 1. 📦 Install Python 3.10.10

- Download from: https://www.python.org/downloads/release/python-31010/
- During installation, ensure you **check the box** to “Add Python to PATH”.

---

### 2. 📁 Clone the Repository

git clone https://github.com/MrunaliKodhe/Nova-AI-Assistant.git  
cd Nova-AI-Assistant

---

### 3. 🧪 Create and Activate a Virtual Environment

**For Windows:**

python -m venv venv  
venv\Scripts\activate


---

### 4. 📥 Install Dependencies

pip install -r requirements.txt

---

### 5. 🔐 Setup Environment Variables

1. Generate API Keys from:

   - Hugging Face: https://huggingface.co/settings/tokens  
   - Cohere: https://dashboard.cohere.com/api-keys  
   - Groq: https://console.groq.com/keys

2. Rename `.env.example` to `.env` and update it:

AssistantVoice=en-IN-PrabhatNeural  
InputLanguage=en  
HuggingFaceAPIKey=your_huggingface_api_key  
CohereAPIKey=your_cohere_api_key  
GroqAPIKey=your_groq_api_key  
Assistantname=Nova  
Username=YourName

3. 🎙️ **Customize Voice and Language**

   You can personalize Nova’s accent and input/output language by updating the following in `.env`:

   - `AssistantVoice`: Choose from multiple accents like British, American, Australian, Indian, etc.
   - `InputLanguage`: Choose supported input languages such as `en`, `hi`, `ja`, `fr`, etc.

   🔗 **Full list of voices and languages** available at:  
   https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462

---

### ▶️ Run the Assistant

python Main.py

---

### 📝 Notes

- Make sure your microphone and speakers are working.
- Internet is required for AI responses and generation.
- Voice and language can be customized in the `.env` file.

---



## ✨ Built with Passion

Made with ❤️, ☕, and a lot of debugging (https://github.com/MrunaliKodhe)



