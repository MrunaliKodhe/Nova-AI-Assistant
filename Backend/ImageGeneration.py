import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep
from dotenv import load_dotenv
load_dotenv()


# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = os.getenv("HuggingFaceAPIKey")  # Ensure API Key is set
headers = {"Authorization": f"Bearer {API_KEY}"}

# Validate API Key before making requests
if headers["Authorization"] == "Bearer None":
    raise ValueError("❌ Missing Hugging Face API Key! Set it in your environment variables.")

# Ensure necessary folders exist
os.makedirs("Data", exist_ok=True)
os.makedirs("Frontend/Files", exist_ok=True)

# Create ImageGeneration.data file if it doesn't exist
if not os.path.exists("Frontend/Files/ImageGeneration.data"):
    with open("Frontend/Files/ImageGeneration.data", "w") as f:
        f.write("False, False")  # Default status


# Function to open and display images
def open_images(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]  # Generate filenames

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"📸 Opening image: {image_path}")
            img.show(title=f"Generated: {jpg_file}")  # Ensure title is set
            sleep(1)  # Pause before showing the next image
        except FileNotFoundError:
            print(f"❌ Unable to open {image_path}")


# Async function to send a request to Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

        # Validate API response
        if "image" in response.headers.get("Content-Type", ""):
            return response.content
        else:
            print(f"❌ API Response Error: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        return None


# Async function to generate images
async def generate_images(prompt: str):
    tasks = []
    for _ in range(1):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    # Gather results
    image_bytes_list = await asyncio.gather(*tasks)

    # Save images if they are valid
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            with open(f"Data/{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
                f.write(image_bytes)


# Wrapper function to handle async execution
def GenerateImages(prompt: str):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(generate_images(prompt))
        else:
            asyncio.run(generate_images(prompt))
    except RuntimeError as e:
        print(f"❌ Async Runtime Error: {e}")

    open_images(prompt)  # Display generated images


# Main loop to monitor image generation requests
while True:
    try:
        # Read the image generation request file
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            Data = f.read().strip()

        if not Data:
            continue

        Prompt, Status = Data.split(",")

        # If image generation is requested
        if Status.strip().lower() == "true":
            print("🎨 Generating Images ...")
            GenerateImages(prompt=Prompt.strip())

            # Reset the status after generating images
            with open("Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False, False")

            break  # Exit after processing

        else:
            sleep(1)

    except Exception as e:
        print(f"⚠️ Error: {e}")
