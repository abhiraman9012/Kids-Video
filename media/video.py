# File: media/video.py
# Functions:
# - create_video_from_images_and_audio()
# - generate_thumbnail()

import os
import subprocess
import platform
from PIL import Image, ImageDraw, ImageFont
import PIL.Image as PILImage
import tempfile
import json
import datetime

def create_video_from_images_and_audio(image_files, audio_file, output_dir):
    """
    Creates a video from images and audio using FFmpeg.
    
    Args:
        image_files (list): List of paths to image files
        audio_file (str): Path to audio file
        output_dir (str): Directory to save the output video
        
    Returns:
        str: Path to the output video file or None if creation fails
    """
    print("⏳ Creating video from images and audio...")
    
    if not image_files or not audio_file:
        print("❌ Missing image files or audio file")
        return None
        
    try:
        # Resize images to consistent dimensions (16:9 ratio)
        target_width = 1920
        target_height = 1080
        
        resize_dir = os.path.join(output_dir, "resized_images")
        os.makedirs(resize_dir, exist_ok=True)
        
        resized_images = []
        for i, img_path in enumerate(image_files):
            try:
                # Open image
                img = Image.open(img_path)
                
                # Resize to target dimensions
                img = img.resize((target_width, target_height), PILImage.LANCZOS)
                
                # Save resized image
                output_path = os.path.join(resize_dir, f"resized_{i+1:03d}.jpg")
                img.save(output_path, "JPEG", quality=95)
                
                resized_images.append(output_path)
                print(f"✅ Resized image {i+1}/{len(image_files)}")
                
            except Exception as e:
                print(f"⚠️ Error resizing image {img_path}: {e}")
                # Use original image as fallback
                resized_images.append(img_path)
        
        # Set output path for video
        output_video = os.path.join(output_dir, "story_video.mp4")
        
        # Create a temporary file for FFmpeg filter script
        filter_script = os.path.join(output_dir, "filter_script.txt")
        
        # Calculate timing based on audio duration
        try:
            # Get audio duration using FFprobe
            duration_cmd = [
                "ffprobe", 
                "-i", audio_file,
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ]
            
            duration_output = subprocess.check_output(duration_cmd, universal_newlines=True)
            audio_duration = float(duration_output.strip())
            
            # Calculate time per image
            total_images = len(resized_images)
            time_per_image = audio_duration / total_images
            
            print(f"✅ Audio duration: {audio_duration:.2f}s")
            print(f"✅ Time per image: {time_per_image:.2f}s")
            
            # Generate filter script with zoom/pan effect
            with open(filter_script, "w") as f:
                # Start with empty list for inputs
                inputs = []
                
                # For each image
                for i in range(total_images):
                    # Add input with duration and fade
                    inputs.append(f"[{i}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=PTS-STARTPTS+{i*time_per_image}/TB,trim=duration={time_per_image},fade=t=in:st=0:d=0.5,fade=t=out:st={time_per_image-0.5}:d=0.5[v{i}];")
                
                # Concatenate all inputs
                f.write("".join(inputs))
                
                # Add concatenation filter
                v_inputs = "".join(f"[v{i}]" for i in range(total_images))
                f.write(f"{v_inputs}concat=n={total_images}:v=1:a=0[outv]")
                
            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
            ]
            
            # Add input images
            for img in resized_images:
                cmd.extend(["-loop", "1", "-t", str(time_per_image), "-i", img])
            
            # Add audio input
            cmd.extend(["-i", audio_file])
            
            # Add filter complex
            cmd.extend([
                "-filter_complex_script", filter_script,
                "-map", "[outv]",
                "-map", f"{total_images}:a",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-r", "30",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-b:v", "5M",  # Higher bitrate for better quality
                "-maxrate", "5M",
                "-bufsize", "10M",
                output_video
            ])
            
            # Execute FFmpeg
            print("⏳ Running FFmpeg...")
            print(f"💡 Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully created video: {output_video}")
                
                # Get video info
                info_cmd = [
                    "ffprobe",
                    "-i", output_video,
                    "-show_entries", "format=duration,size",
                    "-v", "quiet",
                    "-of", "json"
                ]
                
                info_output = subprocess.check_output(info_cmd, universal_newlines=True)
                info = json.loads(info_output)
                
                video_duration = float(info["format"]["duration"])
                video_size = int(info["format"]["size"]) / (1024 * 1024)  # Convert to MB
                
                print(f"📊 Video duration: {video_duration:.2f}s")
                print(f"📊 Video size: {video_size:.2f} MB")
                
                return output_video
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
                
                # Try simple slideshow as fallback
                print("⏳ Attempting simple slideshow as fallback...")
                
                simple_cmd = [
                    "ffmpeg",
                    "-y",
                    "-framerate", "1/" + str(time_per_image),
                ]
                
                # Add input images
                for img in resized_images:
                    simple_cmd.extend(["-i", img])
                
                # Add audio input
                simple_cmd.extend(["-i", audio_file])
                
                # Add simple concatenation
                simple_cmd.extend([
                    "-filter_complex", f"concat=n={total_images}:v=1:a=0[outv]",
                    "-map", "[outv]",
                    "-map", f"{total_images}:a",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    output_video
                ])
                
                print(f"💡 Fallback command: {' '.join(simple_cmd)}")
                
                result = subprocess.run(simple_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Successfully created simple slideshow video: {output_video}")
                    return output_video
                else:
                    print(f"❌ Simple slideshow failed: {result.stderr}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error during video creation: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error in video creation process: {e}")
        return None

def generate_thumbnail(image_files, story_text, metadata):
    """
    Generates a video thumbnail using one of the generated images and adding text overlay.
    
    Args:
        image_files (list): List of images from the story
        story_text (str): The complete story text
        metadata (dict): The SEO metadata dictionary
        
    Returns:
        str: Path to the generated thumbnail
    """
    print("⏳ Generating video thumbnail...")
    
    try:
        # Select the best image for thumbnail
        # Typically one of the first few images works well as they introduce the character
        if not image_files:
            print("⚠️ No images available for thumbnail generation")
            return None
            
        # Choose image based on availability - prioritize 2nd image if available (often shows main character clearly)
        thumbnail_base_img = image_files[min(1, len(image_files) - 1)]
        
        # Create a temporary file for the thumbnail
        thumbnail_path = os.path.join(os.path.dirname(thumbnail_base_img), "thumbnail.jpg")
        
        # Open the image using PIL
        from PIL import Image, ImageDraw, ImageFont
        
        # Open and resize the image to standard YouTube thumbnail size (1920x1080) for high quality
        # Then we'll downscale to 1280x720 for the final thumbnail with better quality
        img = Image.open(thumbnail_base_img)
        # First upscale if needed to ensure we have enough details
        if img.width < 1920 or img.height < 1080:
            img = img.resize((1920, 1080), PILImage.LANCZOS)
            
        # Ensure proper aspect ratio for YouTube thumbnail
        img = img.resize((1280, 720), PILImage.LANCZOS)
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, with fallback to default
        try:
            # Try to find a suitable font
            font_path = None
            
            # List of common system fonts to try
            font_names = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                '/System/Library/Fonts/Supplemental/Arial Bold.ttf',     # macOS
                'C:\\Windows\\Fonts\\arialbd.ttf',                       # Windows
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',  # Another Linux option
            ]
            
            for font_name in font_names:
                if os.path.exists(font_name):
                    font_path = font_name
                    break
                    
            # Use the font if found, otherwise will use default
            if font_path:
                # Title font (large)
                title_font = ImageFont.truetype(font_path, 60)
                # Get the title from metadata
                title = metadata['title']
                
                # Measure text size to position it
                text_width = draw.textlength(title, font=title_font)
                
                # Add semi-transparent background for better readability
                # Draw a rectangle at the bottom for the title
                rectangle_height = 120
                draw.rectangle(
                    [(0, img.height - rectangle_height), (img.width, img.height)],
                    fill=(0, 0, 0, 180)  # Semi-transparent black
                )
                
                # Draw the title text
                draw.text(
                    (img.width / 2 - text_width / 2, img.height - rectangle_height / 2 - 30),
                    title,
                    font=title_font,
                    fill=(255, 255, 255)  # White color
                )
                
                # Add a small banner at the top for "Children's Story"
                draw.rectangle(
                    [(0, 0), (img.width, 80)],
                    fill=(0, 0, 0, 150)  # Semi-transparent black
                )
                
                # Use a smaller font for the banner
                banner_font = ImageFont.truetype(font_path, 40)
                banner_text = "Children's Story Animation"
                banner_width = draw.textlength(banner_text, font=banner_font)
                
                draw.text(
                    (img.width / 2 - banner_width / 2, 20),
                    banner_text,
                    font=banner_font,
                    fill=(255, 255, 255)  # White color
                )
            else:
                print("⚠️ Could not find a suitable font, using basic text overlay")
                # Use PIL's default font
                # Add semi-transparent black rectangles for text placement
                draw.rectangle(
                    [(0, img.height - 100), (img.width, img.height)],
                    fill=(0, 0, 0, 180)
                )
                draw.rectangle(
                    [(0, 0), (img.width, 80)],
                    fill=(0, 0, 0, 150)
                )
                
                # Add text - simplified when no font is available
                draw.text(
                    (40, img.height - 80),
                    metadata['title'][:50],
                    fill=(255, 255, 255)
                )
                draw.text(
                    (40, 30),
                    "Children's Story Animation",
                    fill=(255, 255, 255)
                )
                
        except Exception as font_error:
            print(f"⚠️ Error with font rendering: {font_error}")
            # Add basic text using default settings
            draw.rectangle(
                [(0, img.height - 100), (img.width, img.height)],
                fill=(0, 0, 0, 180)
            )
            draw.text(
                (40, img.height - 80),
                metadata['title'][:50],
                fill=(255, 255, 255)
            )
            
        # Save the thumbnail
        img.save(thumbnail_path, quality=95)
        print(f"✅ Thumbnail generated and saved to: {thumbnail_path}")
        
        return thumbnail_path
        
    except Exception as e:
        print(f"⚠️ Error generating thumbnail: {e}")
        return None
