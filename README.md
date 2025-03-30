GPT-4 Test Automation & OCR

This Python script automatically captures test questions from your screen, sends them to OpenAI’s GPT-4 for analysis, and displays the best answer as a transparent overlay.

Features

    Auto Test Answering: Detects and captures questions from your screen.
    OCR Integration: Uses Tesseract OCR to extract text.
    GPT-4 API: Sends images to GPT-4 for answer extraction.
    Overlay Display: Shows the best answer on your screen.

Requirements

    Python 3.x
    Install dependencies:
    pip install pyautogui pytesseract requests Pillow openai
    Tesseract OCR: Install Tesseract
    OpenAI API Key

Setup

    Install Tesseract OCR and set the correct path in the script.
    Replace the API_KEY in the script with your OpenAI API key.

How It Works

    Detects Text: Monitors a small area for questions.
    Captures Image: Takes a screenshot once stable text is detected.
    Sends to GPT-4: Analyzes the image and extracts the best answer.
    Shows Overlay: Displays the answer as a fullscreen overlay for 5 seconds.

Configuration

    DETECTION_DURATION: Time (in seconds) text must remain stable before capturing.
    SMALL_WIDTH, SMALL_HEIGHT: Dimensions for the small text detection area.
    BIG_WIDTH, BIG_HEIGHT: Dimensions for the full question capture.
    TOP_MARGIN, LEFT_MARGIN: Offsets for the capture area relative to the cursor.

Usage

    Run the script to automatically detect and capture test questions.
    The best answer will appear as a fullscreen overlay.


![image](https://github.com/user-attachments/assets/f150732e-5e7f-4837-9526-0d34e2f035c7)
