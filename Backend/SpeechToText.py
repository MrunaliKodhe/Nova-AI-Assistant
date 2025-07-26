from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager 
from dotenv import dotenv_values 
import os 
import mtranslate as mt
import time
from fake_useragent import UserAgent  

# Load environment variables from the .env file
env_vars = dotenv_values(".env") 
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# Define the HTML code for the speech recognition interface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        let output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = false;  // Stop after one sentence

            recognition.onresult = function(event) {
                output.innerText = event.results[0][0].transcript;  // Only store the latest result
            };

            recognition.onerror = function(event) {
                output.innerText = "Error: " + event.error;
            };

            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                recognition = null;  // Clear the reference
            }
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file
os.makedirs("Data", exist_ok=True)  # Ensure the directory exists
with open(r"Data\Voice.html", "w", encoding="utf-8") as f: 
    f.write(HtmlCode)

# Get the absolute path to the HTML file
current_dir = os.getcwd() 
Link = f"file:///{current_dir}/Data/Voice.html"

# Set up Chrome options
chrome_options = Options()
ua = UserAgent()  # Generate dynamic user-agent
chrome_options.add_argument(f'user-agent={ua.chrome}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")

# Initialize the Chrome WebDriver
service = Service(ChromeDriverManager().install()) 
driver = webdriver.Chrome(service=service, options=chrome_options) 

# Define the path for temporary files
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)  # Ensure the directory exists

# Function to modify a query to ensure proper punctuation
def QueryModifier(Query): 
    new_query = Query.lower().strip() 
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    if any(new_query.startswith(word) for word in question_words):
        return new_query.capitalize() + "?"
    return new_query.capitalize() + "."

# Function to translate text into English
def UniversalTranslator(Text): 
    return mt.translate(Text, "en", "auto").capitalize()

# Function to perform speech recognition
def SpeechRecognition(): 
    driver.get(Link)  
    driver.find_element(By.ID, "start").click() 
    print("Listening... Speak now!")

    start_time = time.time()
    timeout = 10  # Max wait time in seconds

    while time.time() - start_time < timeout:  
        try:
            element = driver.find_element(By.ID, "output")
            if element.is_displayed():
                Text = element.text.strip()
                if Text:  
                    driver.find_element(By.ID, "end").click()
                    print(f"Recognized: {Text}")

                    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower(): 
                        return QueryModifier(Text)
                    else: 
                        return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            print("Error:", e)
            break  

    print("Speech recognition timeout.")
    return None

# Main execution block
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print("Final Output:", Text)
