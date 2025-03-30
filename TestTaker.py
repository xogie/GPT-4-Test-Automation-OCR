#highlight example
import pyautogui
import time
import threading
import requests
import base64
import pytesseract
import tkinter as tk
from openai import OpenAI
from PIL import Image
import json
import re

# --- Configuration ---
DETECTION_DURATION = 2      # Time (seconds) text must remain the same
SMALL_WIDTH = 120           # Small preview width
SMALL_HEIGHT = 40           # Small preview height
BIG_WIDTH = 1200            # Large capture width (original)
BIG_HEIGHT = 1200           # Large capture height (original)
TOP_MARGIN = 20             # Moves both small and big image UP relative to cursor
LEFT_MARGIN = 5             # Moves big image capture area further left

# OpenAI API details (Mock Key)
API_KEY = "sk-proj-fXNiTA0ovF-Oud9cvLshtPXdHqGNuI1VRQyNxdmD89HcOkfjoHT3BlbkFJaH5w9Q6"
GPT_VISION_API_URL = "https://api.openai.com/v1/chat/completions"

client = OpenAI(api_key=API_KEY)

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_json_from_response(text):
    """ Extract JSON object from GPT response, handling errors gracefully. """
    matches = re.findall(r'```json\n(.*?)\n```', text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])  
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON format received. Raw response:", text)
            return {"error": "Invalid JSON format"}
    else:
        print("⚠️ No JSON detected in GPT response. Raw response:", text)
        return {"error": "No JSON in response"}

def send_image_to_chatgpt(image_path):
    """ Sends the captured image to GPT-4o and extracts responses. """
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    prompt = """
    Extract the question and possible answers from top of this image.

    Format response as:
    ```json
    {
        "question_detected": "Yes" | "No",
        "type_of_question": "Multiple Choice" | "True/False" | "Fill in the Blank",
        "Question": "The question",
        "possible_answers": ["Option 1", "Option 2"],
        "best_answers": ["Correct Answer(s)"]
    }
    ```
    """

    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt},
                                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}
        ],
        "max_tokens": 300,
    }

    response = requests.post(GPT_VISION_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        extracted_data = extract_json_from_response(response.json()["choices"][0]["message"]["content"])
        return extracted_data

    return {"error": "GPT API request failed"}

def show_overlay(best_answer):
    """ Creates a transparent fullscreen overlay displaying the best answer. """
    overlay = tk.Tk()
    overlay.attributes("-fullscreen", True)
    overlay.configure(bg='black')
    overlay.wm_attributes("-alpha", 0.5)  # 50% transparency

    label = tk.Label(
        overlay,
        text=f"✅ Answer: {best_answer}",
        font=("Arial", 30, "bold"),
        fg="black",
        bg="white"
    )
    label.pack(expand=True)

    # Close the overlay after 5 seconds
    overlay.after(5000, overlay.destroy)
    overlay.mainloop()

def capture_images():
    """ Detects stable text in the small image, then captures and processes the big image. """
    stable_start_time, last_detected_text = time.time(), None  

    while True:
        current_position = pyautogui.position()

        # Capture small preview
        small_screenshot = pyautogui.screenshot(region=(
            current_position.x, current_position.y - TOP_MARGIN, SMALL_WIDTH, SMALL_HEIGHT))

        small_text = pytesseract.image_to_string(small_screenshot, config="--psm 6").strip()

        if not small_text:
            stable_start_time = time.time()
            last_detected_text = None
            continue  

        if last_detected_text and small_text == last_detected_text:
            if time.time() - stable_start_time >= DETECTION_DURATION:
                print(f"✅ Stable Text Found: {small_text} - Capturing Big Image...")

                big_screenshot = pyautogui.screenshot(region=(
                    current_position.x - LEFT_MARGIN, current_position.y - TOP_MARGIN, BIG_WIDTH, BIG_HEIGHT))

                image_path = "captured_image.png"
                big_screenshot.save(image_path)

                # Process Image with GPT-4o
                chatgpt_response = send_image_to_chatgpt(image_path)
                print("\n📌 **AI Final Analysis:**", json.dumps(chatgpt_response, indent=2))

                # Show transparent overlay with best answer
                if "best_answers" in chatgpt_response and chatgpt_response["best_answers"]:
                    best_answer = chatgpt_response["best_answers"][0]
                    show_overlay(best_answer)

        else:
            stable_start_time = time.time()
            last_detected_text = small_text  

# Start the capture process in a separate thread
threading.Thread(target=capture_images, daemon=True).start()

