# File: media/audio.py
# Functions:
# - generate_audio_from_text()

import os
import re
import json
import numpy as np
import soundfile as sf
from kokoro import KPipeline

import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SAMPLE_RATE

def generate_audio_from_text(story_text, output_dir):
    """
    Generates audio from story text using Kokoro TTS.
    
    Args:
        story_text (str): Complete story text to convert to speech
        output_dir (str): Directory to save audio files
        
    Returns:
        str: Path to the combined audio file or None if generation fails
    """
    print("⏳ Generating audio with Kokoro TTS...")
    
    try:
        # Initialize Kokoro TTS
        pipeline = KPipeline(lang_code='a')
        
        # Create an audio directory
        audio_dir = os.path.join(output_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Split story text into paragraphs for processing
        paragraphs = re.split(r'\n\s*\n', story_text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Process each paragraph
        audio_segments = []
        
        for i, paragraph in enumerate(paragraphs):
            try:
                print(f"⏳ Processing audio segment {i+1}/{len(paragraphs)}...")
                
                # Generate audio for this paragraph
                generator = pipeline(paragraph, voice='af_heart')
                
                # Process all audio chunks
                paragraph_audio = []
                for _, (gs, ps, audio) in enumerate(generator):
                    paragraph_audio.append(audio)
                
                # Combine all audio chunks
                audio_data = np.concatenate(paragraph_audio) if paragraph_audio else np.array([])
                
                # Create file path for this segment
                segment_path = os.path.join(audio_dir, f"segment_{i+1:03d}.wav")
                
                # Save the audio segment
                sf.write(segment_path, audio_data, SAMPLE_RATE)
                
                # Add to list of segments
                audio_segments.append(segment_path)
                
                print(f"✅ Generated audio segment {i+1}")
                
            except Exception as e:
                print(f"⚠️ Error generating audio for segment {i+1}: {e}")
                continue
        
        if not audio_segments:
            print("❌ Failed to generate any audio segments")
            return None
            
        # Combine all segments into one file
        combined_audio_path = os.path.join(output_dir, "story_audio.wav")
        
        # Read all audio data
        all_audio_data = []
        for segment_path in audio_segments:
            try:
                data, _ = sf.read(segment_path)
                all_audio_data.append(data)
            except Exception as e:
                print(f"⚠️ Error reading audio segment {segment_path}: {e}")
                
        if not all_audio_data:
            print("❌ Failed to read any audio segments")
            return None
            
        # Add a small silence between segments
        silence = np.zeros(int(0.5 * SAMPLE_RATE))  # 0.5 seconds of silence
        combined_data = []
        
        for i, data in enumerate(all_audio_data):
            combined_data.append(data)
            if i < len(all_audio_data) - 1:
                combined_data.append(silence)
                
        # Convert list to numpy array
        combined_data = np.concatenate(combined_data)
        
        # Save combined audio
        sf.write(combined_audio_path, combined_data, SAMPLE_RATE)
        print(f"✅ Combined audio saved to: {combined_audio_path}")
        
        return combined_audio_path
        
    except Exception as e:
        print(f"❌ Error in audio generation: {e}")
        return None
