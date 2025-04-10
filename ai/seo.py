# File: ai/seo.py
# Functions:
# - generate_seo_metadata()
# - default_seo_metadata()

import os
import re
import json
import datetime
from google import genai
import google.generative.genai as custom_genai

from ..config import STORY_MODEL, SAFETY_SETTINGS

def generate_seo_metadata(story_text, image_files, prompt_text):
    """
    Generates SEO-friendly metadata (title, description, tags) for the video.
    
    Args:
        story_text (str): The complete story text
        image_files (list): List of paths to generated images
        prompt_text (str): Original prompt used to generate the story
        
    Returns:
        dict: Dictionary with title, description, and tags
    """
    print("⏳ Generating SEO metadata...")
    
    try:
        # Create the Gemini generative AI client
        client = genai.GenerativeModel(model_name=STORY_MODEL,
                                     generation_config={
                                         "temperature": 0.2,  # Lower temperature for more factual output
                                         "top_p": 0.95,
                                         "top_k": 64,
                                         "max_output_tokens": 1024,
                                     },
                                     safety_settings=SAFETY_SETTINGS)
                                     
        # Prepare image data if available
        images = []
        if image_files and len(image_files) > 0:
            # Use the first image for context
            try:
                with open(image_files[0], "rb") as img_file:
                    image_data = img_file.read()
                    images.append(image_data)
                print(f"✅ Added image data to the request")
            except Exception as img_err:
                print(f"⚠️ Error adding image to SEO request: {img_err}")
        
        # Prepare a condensed version of the story for the prompt
        story_preview = story_text[:500] + "..." if len(story_text) > 500 else story_text
        
        # Create prompt for SEO metadata generation
        seo_prompt = f"""
        Based on this children's story and its first image, create SEO-optimized metadata for a YouTube video.
        
        STORY PREVIEW:
        {story_preview}
        
        PROMPT USED:
        {prompt_text}
        
        Return ONLY a JSON object with:
        1. 'title': A catchy, SEO-friendly title (max 60 chars)
        2. 'description': Engaging description (300-500 chars) with relevant keywords
        3. 'tags': List of 10-15 relevant tags as strings
        
        Format your response as valid JSON without explanation:
        {{
          "title": "Your Title Here",
          "description": "Your description here...",
          "tags": ["tag1", "tag2", "tag3", ...]
        }}
        """
        
        try:
            # Generate SEO metadata
            if images:
                response = client.generate_content([seo_prompt, images[0]])
            else:
                response = client.generate_content(seo_prompt)
                
            # Extract JSON string from response
            json_str = response.text.strip()
            
            # Remove markdown formatting if present
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json", "").replace("```", "").strip()
            elif json_str.startswith("```"):
                json_str = json_str.replace("```", "").strip()
                
            # Parse the JSON data
            try:
                metadata = json.loads(json_str)
                # Validate the metadata
                if not all(key in metadata for key in ['title', 'description', 'tags']):
                    print("⚠️ Metadata is missing required fields, using fallback...")
                    return default_seo_metadata(story_text, prompt_text)
                
                print("✅ SEO metadata generated successfully")
                return metadata
            except json.JSONDecodeError:
                print("⚠️ Failed to parse metadata as JSON, using fallback...")
                return default_seo_metadata(story_text, prompt_text)
        except Exception as e:
            print(f"⚠️ Error generating SEO metadata: {e}")
            return default_seo_metadata(story_text, prompt_text)
    except Exception as e:
        print(f"⚠️ Error generating SEO metadata: {e}")
        return default_seo_metadata(story_text, prompt_text)

def default_seo_metadata(story_text, prompt_text):
    """
    Creates default SEO metadata if the AI generation fails.
    
    Args:
        story_text (str): The complete story text
        prompt_text (str): The original prompt used to generate the story
        
    Returns:
        dict: Dictionary with default title, description, and tags
    """
    # Extract character and setting from the prompt if possible
    import re
    char_setting = re.search(r'about\s+(.*?)\s+going\s+on\s+an\s+adventure\s+in\s+(.*?)(?:\s+in\s+a\s+3d|\.)',
                             prompt_text)
    
    character = "an animal"
    setting = "an adventure"
    
    if char_setting:
        character = char_setting.group(1)
        setting = char_setting.group(2)
    
    # Create a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Create default metadata
    title = f"Adventure of {character} in {setting} | Children's Story"
    title = title[:60]  # Ensure title is not too long
    
    # Create a brief description from the beginning of the story
    story_preview = story_text[:500] + "..." if len(story_text) > 500 else story_text
    description = f"""
    Join {character} on an exciting adventure in {setting}!
    
    {story_preview}
    
    This animated children's story is perfect for bedtime reading, family story time, or whenever your child wants to explore magical worlds and learn valuable lessons. Watch as our character overcomes challenges and discovers new friends along the way.
    
    #ChildrensStory #Animation #KidsEntertainment
    
    Created: {timestamp}
    """
    
    # Default tags
    tags = [
        "children's story",
        "kids animation",
        "bedtime story",
        "animated story",
        character,
        setting,
        "family friendly",
        "kids entertainment",
        "story time",
        "animated adventure",
        "educational content",
        "preschool",
        "moral story",
        "3D animation",
        "storybook"
    ]
    
    print("✅ Created default SEO metadata")
    return {
        "title": title,
        "description": description,
        "tags": tags
    }
