# File: ai/prompt_generator.py
# Functions:
# - generate_prompt()
# - retry_api_call()

import os
import time
import random
from google import genai
from google.genai import types

import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PROMPT_MODEL, SAFETY_SETTINGS, RETRY_DELAY, MAX_CONSECUTIVE_FAILURES

def retry_api_call(retry_function, *args, **kwargs):
    """
    Retries API calls with exponential backoff.
    
    Args:
        retry_function: Function to retry
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function or None after max retries
    """
    max_consecutive_failures = kwargs.pop('max_consecutive_failures', MAX_CONSECUTIVE_FAILURES)
    retry_delay = kwargs.pop('retry_delay', RETRY_DELAY)
    failures = 0
    last_exception = None
    
    # Keep trying until we hit the max failures
    while failures < max_consecutive_failures:
        try:
            return retry_function(*args, **kwargs)
        except custom_genai.genai_errors.ResourceExhaustedError as e:
            print(f"⚠️ API quota exceeded: {e}")
            retry_delay = 60  # Wait longer when quota is exceeded
            last_exception = e
        except custom_genai.genai_errors.InternalServerError as e:
            print(f"⚠️ Server error: {e}")
            last_exception = e
        except custom_genai.genai_errors.InvalidArgumentError as e:
            print(f"⚠️ Invalid argument: {e}")
            if "safety" in str(e).lower():
                print("💡 Trying different prompt due to safety concerns")
                # For safety errors, we might want to try a different approach
                kwargs['safety_retry'] = True
            else:
                # For other invalid arguments, we might need to fix our request
                print("⚠️ Invalid API argument - check request format")
                failures += 10  # Increase failures more for invalid arguments
            last_exception = e
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            last_exception = e
        
        # Increment failure counter
        failures += 1
        
        # If we're about to give up, log that
        if failures >= max_consecutive_failures:
            print(f"❌ Giving up after {failures} failures. Last error: {last_exception}")
            return None
            
        # Add some randomness to the delay to avoid synchronized retries
        jitter = random.uniform(0.5, 1.5)
        adjusted_delay = retry_delay * jitter
        
        print(f"⏳ Retry {failures}/{max_consecutive_failures} after {adjusted_delay:.1f}s...")
        time.sleep(adjusted_delay)
        
        # Increase the delay for next time
        retry_delay = min(retry_delay * 2, 60)  # Cap at 60 seconds
    
    # If we get here, we've failed too many times
    return None

def generate_prompt(prompt_input, use_streaming=True):
    """
    Generates a story prompt using Gemini AI.
    
    Args:
        prompt_input (str): Input to guide prompt generation
        use_streaming (bool): Whether to use streaming API
        
    Returns:
        str: Generated prompt text or None if generation fails
    """
    # Create Generative AI client
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.GenerativeModel(model_name=PROMPT_MODEL, 
                                    api_key=api_key,
                                    generation_config={
                                        "temperature": 1.0,
                                        "top_p": 0.95,
                                        "top_k": 64,
                                        "max_output_tokens": 8192,
                                    },
                                    safety_settings=SAFETY_SETTINGS)
    
    # System message/instructions for the model to create a detailed prompt
    system_message = """
    As a creative writing expert for children's stories, your task is to generate a detailed story prompt for our creative AI.
    
    Please structure your response in this specific format:
    ```
    Generate a story about [CHARACTER] going on an adventure in [SETTING] in a highly detailed 3d cartoon animation style. Make sure each scene has maximum detail, vibrant colors, and professional lighting. The story should be positive, uplifting, and perfect for a YouTube children's channel. Generate images in 16:9 aspect ratio suitable for a widescreen YouTube video.
    ```
    
    IMPORTANT RULES:
    1. Always include "in a highly detailed 3d cartoon animation style" in the prompt
    2. Always include "Generate images in 16:9 aspect ratio suitable for a widescreen YouTube video"
    3. Make the character and setting family-friendly, colorful and appealing to young children
    4. Your response should ONLY contain the prompt text in the format above, without any additional explanations or text
    5. Create a unique character and fantasy setting each time
    6. No RPG/video game settings or popular cartoon characters
    7. Include specific visual style details like "vibrant colors" and "professional lighting"
    """
    
    # Combine system message with the user's specific request
    if prompt_input:
        prompt = f"{system_message}\n\nUser request: {prompt_input}"
    else:
        prompt = system_message
    
    print("⏳ Generating story prompt...")
    
    try:
        # Use streaming API if requested
        if use_streaming:
            generated_prompt = ""
            response = client.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    generated_prompt += chunk.text
                    
            print("✅ Generated prompt using streaming API")
            
        else:
            # Fallback to non-streaming API if requested
            response = client.generate_content(prompt)
            generated_prompt = response.text
            print("✅ Generated prompt using non-streaming API")
        
        # Clean up the prompt - extract just the proper format
        import re
        # Look for the specific format pattern
        pattern = r'Generate a story about (.*?) going on an adventure in (.*?) in a highly detailed 3d cartoon animation style'
        matches = re.search(pattern, generated_prompt)
        
        if matches:
            # We found the right pattern, extract and use the full prompt from this point
            start_idx = generated_prompt.find("Generate a story about")
            if start_idx >= 0:
                clean_prompt = generated_prompt[start_idx:]
                # Ensure it includes the 16:9 aspect ratio requirement
                if "16:9" not in clean_prompt:
                    clean_prompt += " Generate images in 16:9 aspect ratio suitable for a widescreen YouTube video."
                return clean_prompt
        
        # If we can't find the pattern or need to clean up markdown
        clean_prompt = generated_prompt.replace("```", "").strip()
        
        # Last check - ensure we have the critical parts
        if "Generate a story about" not in clean_prompt:
            clean_prompt = f"Generate a story about {clean_prompt}"
        if "highly detailed 3d cartoon animation style" not in clean_prompt:
            clean_prompt += " in a highly detailed 3d cartoon animation style"
        if "16:9" not in clean_prompt:
            clean_prompt += " Generate images in 16:9 aspect ratio suitable for a widescreen YouTube video."
        
        return clean_prompt
        
    except Exception as e:
        print(f"❌ Error generating prompt: {e}")
        return None
