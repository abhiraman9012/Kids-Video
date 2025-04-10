# File: config.py
# Description: Configuration constants and settings for the project
# - API_KEYS: List of Gemini API keys
# - SAFETY_SETTINGS: Safety settings for content generation

import os
from google.genai import types

# List of all available API keys
API_KEYS = [
    "AIzaSyAqbqE86FKFXS6t5qrpXJVj9jAf-arQ1Js",
    "AIzaSyDVmSA9ricHVEzo6v1gj-crkuaJvQD72yw",
    "AIzaSyDNeeKDXnwGF7MYhFrnFoD9VL-ecvO5mEE",
    "AIzaSyAHvAdcSoRmeXB9xJjvvdXKtXw3dHSmJiQ",
    "AIzaSyC_XqbLjFQnLXfo26J-RX_WDx59H4ql9Qs",
    "AIzaSyC8FuTNC3FxLs0Qx2ciRoLwxjOrLGqOB5A",
    "AIzaSyBL8KngLHXOY0rSk5R4awta1tfDl6xC8rM"
]

# Google Drive Credentials file ID
DRIVE_CREDENTIALS_FILE_ID = "152LtocR_Lvll37IW3GXJWAowLS02YBF2"

# Define Safety Settings
SAFETY_SETTINGS = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

# API Models
PROMPT_MODEL = "gemini-2.0-flash-thinking-exp-01-21"
STORY_MODEL = "gemini-2.0-flash-exp-image-generation"

# API Retry settings
MAX_CONSECUTIVE_FAILURES = 1000
RETRY_DELAY = 10  # seconds

# Story generation settings
MIN_STORY_SEGMENTS = 6  # Minimum number of segments required for a complete story

# Default prompt if no input provided
DEFAULT_PROMPT = """Generate a story about a white baby goat named Pip going on an adventure in a farm in a highly detailed 3d cartoon animation style. For each scene, generate a high-quality, photorealistic image **in landscape orientation suitable for a widescreen (16:9 aspect ratio) YouTube video**. Ensure maximum detail, vibrant colors, and professional lighting."""

# Audio settings
SAMPLE_RATE = 24000  # Sample rate for audio files

# Set a selected API key in environment
def set_api_key():
    # Randomly select one API key
    import random
    selected_api_key = random.choice(API_KEYS)
    os.environ['GEMINI_API_KEY'] = selected_api_key
    print(f"✅ Randomly selected one of {len(API_KEYS)} available API keys")
    
    # Verify API key
    api_key_check = os.environ.get("GEMINI_API_KEY")
    if not api_key_check:
        print("🛑 ERROR: Environment variable GEMINI_API_KEY is not set.")
        print("💡 TIP: Uncomment and set your API key above, or run this in a cell before running this script:")
        print("    os.environ['GEMINI_API_KEY'] = 'YOUR_API_KEY_HERE'")
        raise ValueError("API Key not found in environment.")
    else:
        print(f"✅ Found API Key: ...{api_key_check[-4:]}")
    
    return api_key_check
