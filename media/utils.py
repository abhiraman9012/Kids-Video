# File: media/utils.py
# Functions:
# - collect_complete_story()

import re

def collect_complete_story(raw_text, return_segments=False):
    """
    Extracts and cleans story text from Gemini's output.
    
    Args:
        raw_text (str): Raw text output from Gemini
        return_segments (bool): If True, returns a list of segments instead of full story
        
    Returns:
        str or list: Cleaned story text or list of story segments
    """
    print("⏳ Processing and extracting story text...")
    
    # Clean up the text (remove markdown formatting, etc.)
    cleaned_text = raw_text.strip()
    
    # Define patterns for story segments
    segment_patterns = [
        # Pattern 1: Segment numbers with optional scene labels ("Segment 1: Introduction")
        r'(?:Segment|SEGMENT|Scene|SCENE)\s+\d+(?:\s*[-:][^a-zA-Z0-9]*\s*[^"\']+)?',
        
        # Pattern 2: Just numbers as separators ("1.", "1)", "[1]")
        r'(?:^|\n)\s*(?:\d+[\.\)\]]|\[\d+\])\s+',
        
        # Pattern 3: Image descriptions or labels ("[Image 1: A forest scene]")
        r'\[(?:Image|IMG|Picture|PIC)\s*\d+[^\]]*\]'
    ]
    
    # Try each pattern to identify segments
    segments = []
    
    for pattern in segment_patterns:
        # Use the pattern to split the text
        potential_segments = re.split(pattern, cleaned_text)
        
        # Filter out empty segments
        potential_segments = [s.strip() for s in potential_segments if s.strip()]
        
        # If we found at least 3 segments, consider this a valid segmentation
        if len(potential_segments) >= 3:
            segments = potential_segments
            print(f"✅ Identified {len(segments)} story segments using pattern: {pattern[:30]}...")
            break
    
    # If no segments were found using patterns, try to split by double newlines
    if not segments:
        print("⚠️ No segments found using patterns, trying paragraph splitting...")
        segments = re.split(r'\n\s*\n', cleaned_text)
        segments = [s.strip() for s in segments if s.strip()]
        print(f"✅ Split story into {len(segments)} paragraphs")
    
    # Final cleanup - remove non-story content
    story_segments = []
    
    for segment in segments:
        # Skip segments that look like they're not part of the story
        if (len(segment.split()) < 5 or
            segment.startswith("Image generation:") or
            segment.startswith("Note:") or
            "end of story" in segment.lower() or
            "```" in segment):
            continue
            
        # Clean up remaining markdown artifacts and text formatting
        clean_segment = segment.replace("```", "").strip()
        
        # Remove image descriptions if they're inline
        clean_segment = re.sub(r'\[(?:Image|IMG|Picture|PIC)\s*\d+[^\]]*\]', '', clean_segment)
        
        # Remove other bracket notations often used in generation
        clean_segment = re.sub(r'\[(.*?)\]', '', clean_segment)
        
        # Add the cleaned segment to our list
        if clean_segment:
            story_segments.append(clean_segment)
    
    print(f"✅ Extracted {len(story_segments)} clean story segments")
    
    # Return segments if requested
    if return_segments:
        return story_segments
    
    # Otherwise combine segments into a single story text
    full_story = '\n\n'.join(story_segments)
    
    # Final sanity check - if story seems too short, return the original
    if len(full_story) < 100 and len(cleaned_text) > 100:
        print("⚠️ Processed story seems too short, using original text")
        return cleaned_text
    
    return full_story
