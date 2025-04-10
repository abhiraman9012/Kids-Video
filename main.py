# File: main.py
# Description: Main entry point for the children's story generation application
# This orchestrates the entire process of generating stories, creating audio and video,
# and uploading the results to Google Drive.

import os
import sys
from ai.story_generator import retry_story_generation
from config import set_api_key
from google_drive.api_client import test_google_drive_api

def main():
    """
    Main function that orchestrates the story generation process.
    """
    print("=" * 50)
    print("Children's Story Generator".center(50))
    print("=" * 50)
    
    # Set API key from config
    try:
        api_key = set_api_key()
        print(f"✅ API key set successfully")
    except Exception as e:
        print(f"❌ Failed to set API key: {e}")
        sys.exit(1)
    
    # Test Google Drive API if needed
    try:
        if test_google_drive_api():
            print("✅ Google Drive API test successful")
        else:
            print("⚠️ Google Drive API test failed, but continuing...")
    except Exception as e:
        print(f"⚠️ Google Drive API test error: {e}")
        print("⚠️ Continuing without Google Drive integration...")
    
    # Generate the story
    print("\n--- Starting generation (attempting 16:9 via prompt) ---")
    result = retry_story_generation(use_prompt_generator=True)
    
    if result:
        print("\n✅ Story generation successful!")
        print(f"📊 Generated {len(result.get('image_files', []))} images")
        
        # Print video information if available
        if 'video_file' in result and result['video_file']:
            print(f"🎬 Video created: {result['video_file']}")
        
        # Print Google Drive information if available
        if 'upload_result' in result and result['upload_result']:
            video_link = result['upload_result'].get('video_link', '')
            if video_link:
                print(f"🔗 Video link: {video_link}")
    else:
        print("❌ Story generation failed")
    
    print("--- Generation function finished ---")

if __name__ == "__main__":
    main()
