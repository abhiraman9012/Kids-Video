# File: ai/story_generator.py
# Functions:
# - generate()
# - retry_story_generation()

import os
import re
import json
import base64
import tempfile
import datetime
from PIL import Image as PILImage
from IPython.display import display
from google import genai

from ..config import (STORY_MODEL, SAFETY_SETTINGS, DEFAULT_PROMPT, 
                     MIN_STORY_SEGMENTS, set_api_key)
from .prompt_generator import generate_prompt, retry_api_call
from ..media.audio import generate_audio_from_text
from ..media.video import create_video_from_images_and_audio
from ..media.utils import collect_complete_story
from ..google_drive.uploader import upload_video_to_drive
from .seo import generate_seo_metadata

def retry_story_generation(use_prompt_generator=True, prompt_input=DEFAULT_PROMPT):
    """
    Retries story generation until success (handles JSON/image errors).
    
    Args:
        use_prompt_generator (bool): Whether to use the prompt generator
        prompt_input (str): Input to guide prompt generation
        
    Returns:
        dict: Dictionary with story_text, image_files, output_path, etc.
    """
    print("⏳ Starting story generation with retry mechanism...")
    
    # Initialize variables
    max_retries = 5
    retry_count = 0
    success = False
    result = None
    
    # Set the API key
    api_key = set_api_key()
    
    # Start retry loop
    while not success and retry_count < max_retries:
        retry_count += 1
        print(f"\n✨ Attempt {retry_count}/{max_retries} ✨")
        
        try:
            # Generate the story
            result = generate(use_prompt_generator, prompt_input)
            
            # Check if generation was successful
            if result and 'story_text' in result and 'image_files' in result:
                # Ensure we have enough story segments
                story_segments = collect_complete_story(result['story_text'], return_segments=True)
                
                if len(story_segments) >= MIN_STORY_SEGMENTS and len(result['image_files']) >= MIN_STORY_SEGMENTS:
                    print(f"✅ Story generation successful with {len(story_segments)} segments and {len(result['image_files'])} images")
                    success = True
                else:
                    print(f"⚠️ Generated story insufficient: {len(story_segments)} segments, {len(result['image_files'])} images")
                    print(f"   Expected minimum: {MIN_STORY_SEGMENTS} segments and images")
            else:
                print("⚠️ Story generation failed or returned incomplete data")
        
        except Exception as e:
            print(f"❌ Error during generation attempt {retry_count}: {e}")
        
        # If not successful, try again
        if not success and retry_count < max_retries:
            print(f"⏳ Retrying story generation in 5 seconds...")
            import time
            time.sleep(5)
    
    if success:
        print("✅ Story generation completed successfully after retry mechanism")
        return result
    else:
        print("❌ All retry attempts failed")
        return None

def generate(use_prompt_generator=True, prompt_input=DEFAULT_PROMPT):
    """
    Main function to generate stories, images, audio, and video.
    
    Args:
        use_prompt_generator (bool): Whether to use prompt generator
        prompt_input (str): Input to guide prompt generation
        
    Returns:
        dict: Result with story_text, image_files, and output paths
    """
    # Create a temporary directory for outputs
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created temporary directory: {temp_dir}")
    
    # Generate prompt if enabled
    if use_prompt_generator:
        prompt = retry_api_call(generate_prompt, prompt_input)
        if not prompt:
            prompt = prompt_input
            print(f"⚠️ Using fallback prompt: {prompt[:50]}...")
        else:
            print(f"✅ Using generated prompt: {prompt[:50]}...")
    else:
        prompt = prompt_input
        print(f"✅ Using provided prompt: {prompt[:50]}...")
    
    # Create the Gemini generative AI client
    client = genai.GenerativeModel(model_name=STORY_MODEL,
                                  generation_config={
                                      "temperature": 1.0,
                                      "top_p": 0.95,
                                      "top_k": 64,
                                      "max_output_tokens": 8192,
                                  },
                                  safety_settings=SAFETY_SETTINGS)
                                  
    print("⏳ Requesting content generation...")
    
    # Define wrapper function for streaming generation
    def attempt_stream_generation():
        nonlocal temp_dir
        response = client.generate_content(prompt, stream=True)
        
        # Process streamed response
        raw_text = ""
        image_files = []
        image_count = 0
        
        for chunk in response:
            # Handle text
            if hasattr(chunk, 'text') and chunk.text:
                raw_text += chunk.text
                print(".", end="", flush=True)
                
            # Handle images
            if hasattr(chunk, 'parts'):
                for part in chunk.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        try:
                            # Save the image to a file
                            image_count += 1
                            image_data = base64.b64decode(part.inline_data.data)
                            image_path = os.path.join(temp_dir, f"image_{image_count:02d}.png")
                            
                            with open(image_path, "wb") as f:
                                f.write(image_data)
                                
                            # Add to list of images
                            image_files.append(image_path)
                            print(f"\n✅ Saved image {image_count} to {image_path}")
                            
                            # Display the image (if in notebook environment)
                            try:
                                img = PILImage.open(image_path)
                                display(img)
                            except Exception:
                                # Skip display if not in notebook
                                pass
                                
                        except Exception as e:
                            print(f"\n⚠️ Error processing image from stream: {e}")
        
        print(f"\n✅ Completed streaming content generation")
        return raw_text, image_files
    
    # Define wrapper function for non-streaming generation (fallback)
    def attempt_non_stream_generation():
        nonlocal temp_dir
        response = client.generate_content(prompt)
        
        raw_text = response.text
        image_files = []
        image_count = 0
        
        # Process images from response
        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    try:
                        # Save the image to a file
                        image_count += 1
                        image_data = base64.b64decode(part.inline_data.data)
                        image_path = os.path.join(temp_dir, f"image_{image_count:02d}.png")
                        
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                            
                        # Add to list of images
                        image_files.append(image_path)
                        print(f"✅ Saved image {image_count} to {image_path}")
                        
                        # Display the image (if in notebook environment)
                        try:
                            img = PILImage.open(image_path)
                            display(img)
                        except Exception:
                            # Skip display if not in notebook
                            pass
                            
                    except Exception as e:
                        print(f"⚠️ Error processing image from non-stream: {e}")
        
        print(f"✅ Completed non-streaming content generation")
        return raw_text, image_files
    
    # First try streaming generation
    try:
        print("⏳ Attempting streaming generation...")
        raw_text, image_files = retry_api_call(attempt_stream_generation)
        
        # If no text or images, try non-streaming
        if not raw_text or not image_files:
            print("⚠️ Streaming generation returned no content, trying non-streaming...")
            raw_text, image_files = retry_api_call(attempt_non_stream_generation)
            
    except Exception as e:
        print(f"⚠️ Error in streaming generation: {e}")
        print("⏳ Falling back to non-streaming generation...")
        raw_text, image_files = retry_api_call(attempt_non_stream_generation)
    
    # Check if we have content
    if not raw_text or not image_files:
        print("❌ Failed to generate content using both streaming and non-streaming methods")
        return None
    
    # Sort image files by name to ensure proper order
    image_files = sorted(image_files)
    
    # Process the story text
    print("⏳ Processing story text...")
    story_text = collect_complete_story(raw_text)
    
    if not story_text:
        print("⚠️ Failed to extract story text from response")
        return None
    
    # Save the story text to a file
    story_file = os.path.join(temp_dir, "story.txt")
    with open(story_file, "w", encoding="utf-8") as f:
        f.write(story_text)
    print(f"✅ Saved story text to {story_file}")
    
    # Generate audio from text
    print("⏳ Generating audio from story text...")
    audio_file = generate_audio_from_text(story_text, temp_dir)
    
    if not audio_file or not os.path.exists(audio_file):
        print("⚠️ Failed to generate audio")
        return {
            'story_text': story_text,
            'image_files': image_files,
            'prompt_text': prompt,
            'temp_dir': temp_dir
        }
    
    # Create video from images and audio
    print("⏳ Creating video from images and audio...")
    video_file = create_video_from_images_and_audio(image_files, audio_file, temp_dir)
    
    if not video_file or not os.path.exists(video_file):
        print("⚠️ Failed to create video")
        return {
            'story_text': story_text,
            'image_files': image_files,
            'audio_file': audio_file,
            'prompt_text': prompt,
            'temp_dir': temp_dir
        }
    
    # Generate SEO metadata
    print("⏳ Generating SEO metadata...")
    metadata = generate_seo_metadata(story_text, image_files, prompt)
    
    # Generate thumbnail 
    from ..media.video import generate_thumbnail
    thumbnail_path = generate_thumbnail(image_files, story_text, metadata)
    
    # Upload to Google Drive
    print("⏳ Uploading video to Google Drive...")
    upload_result = upload_video_to_drive(video_file, metadata, thumbnail_path)
    
    if upload_result:
        print(f"✅ Uploaded video to Google Drive. Video ID: {upload_result.get('video_id')}")
        print(f"✅ Direct link: {upload_result.get('video_link')}")
    else:
        print("⚠️ Failed to upload to Google Drive")
        print(f"💡 Your video is still available locally at: {video_file}")
    
    # Return the final result
    result = {
        'story_text': story_text,
        'image_files': image_files,
        'audio_file': audio_file,
        'video_file': video_file,
        'thumbnail': thumbnail_path,
        'metadata': metadata,
        'prompt_text': prompt,
        'temp_dir': temp_dir,
        'upload_result': upload_result
    }
    
    print("✅ Content generation complete!")
    return result
