# ✨ AI-Powered Children's Story Generator

*Automatically create animated story videos with Gemini AI, Kokoro TTS, and FFmpeg.*

![Project Banner](https://via.placeholder.com/1200x300?text=AI+Children's+Story+Generator)

## 🌟 Project Overview

This project automates the creation of high-quality animated children's stories from start to finish using AI. It generates engaging narratives with matching images, converts text to natural-sounding speech, combines everything into a professionally animated video, and uploads the result to Google Drive.

### ✨ Key Features

- **AI-Generated Content**: Creates original stories and matching images using Google's Gemini AI models
- **Text-to-Speech**: Converts story text to natural audio narration using Kokoro TTS
- **Professional Video Production**: Automatically creates videos with Ken Burns effects, transitions, and more
- **SEO Optimization**: Generates YouTube-ready titles, descriptions and tags
- **Custom Thumbnails**: Creates eye-catching video thumbnails with text overlay
- **Google Drive Integration**: Seamlessly uploads and organizes videos in the cloud

## 📊 Workflow Diagrams

### Data Flow Between Modules

```mermaid
%% Animated MermaidJS flowchart (render as GIF)  
flowchart LR  
    A[User Input] --> B(Gemini Prompt Generator)  
    B --> C[Story + Images]  
    C --> D{Kokoro TTS}  
    D --> E[Audio File]  
    E --> F[FFmpeg Video Render]  
    F --> G[(Google Drive)]
```

*Figure 1: How data flows through the system, from user input to final video upload.*

### AI Generation Pipeline

```mermaid
%% Animation: Show retry logic  
flowchart TB  
    subgraph AI Generation  
        A[Retry API Call] --> B{Success?}  
        B -->|Yes| C[Generate Story]  
        B -->|No| A  
        C --> D[Validate Images/Text]  
    end
```

*Figure 2: The AI generation process with built-in retry logic for reliability.*

### Video Rendering Process

```mermaid
%% Animation: Show FFmpeg effects  
flowchart LR  
    A[Images] --> B[Zoom/Pan Effects]  
    B --> C[Add Audio Track]  
    C --> D[Thumbnail Overlay]  
    D --> E[MP4 Output]
```

*Figure 3: The video rendering pipeline showing how images and audio are combined with effects.*

## 🔍 How It Works

### Step 1: Story Prompt Generation
User provides a concept or the system generates a creative prompt automatically using Gemini AI.

```python
# Example prompt
"Generate a story about a white baby goat named Pip going on an adventure in a farm"
```

### Step 2: AI Content Generation
The system uses Google's Gemini AI to:
- Generate a complete narrative with multiple segments
- Create high-quality images in 16:9 aspect ratio for each story scene
- Ensure content is family-friendly and visually appealing

### Step 3: Audio Narration
Kokoro TTS engine converts story text to natural-sounding speech:
- Processes the narrative segment by segment
- Combines audio chunks with appropriate pauses
- Creates a single cohesive audio file

### Step 4: Video Production
FFmpeg combines images and audio into a professional video:
- Applies Ken Burns effects (zoom and pan) to static images
- Adds fade transitions between scenes
- Synchronizes audio narration with visuals
- Creates a proper 16:9 widescreen format

### Step 5: Metadata & Upload
- Generates SEO-optimized title, description and tags
- Creates a custom thumbnail with text overlay
- Uploads everything to Google Drive in an organized folder structure
- Provides direct download links

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed on your system
- Google Drive API credentials
- Gemini API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-story-generator.git
cd ai-story-generator
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure API keys
   - Obtain a Gemini API key from [Google AI Studio](https://makersuite.google.com/)
   - Add your key to the environment:
```bash
# Linux/macOS
export GEMINI_API_KEY=your_api_key_here

# Windows PowerShell
$env:GEMINI_API_KEY = "your_api_key_here"
```

4. Set up Google Drive API
   - Create a Google Cloud project
   - Enable the Google Drive API
   - Create and download OAuth 2.0 credentials

## 🚀 Usage Examples

### Basic Usage
Run the project with default settings:

```bash
python main.py
```

This will:
1. Generate a creative story prompt
2. Create a complete story with images
3. Convert text to speech
4. Produce a video
5. Upload to Google Drive

### Custom Story Prompt
Provide your own story concept:

```python
from main import main

# Use a custom prompt to guide the story generation
main(prompt_input="A curious fox exploring a magical forest with talking trees")
```

### Programmatic API
Use the components in your own Python code:

```python
from ai.story_generator import generate
from media.video import create_video_from_images_and_audio

# Generate content
result = generate(use_prompt_generator=True)

# Access generated assets
story_text = result['story_text']
image_files = result['image_files']
audio_file = result['audio_file']
video_file = result['video_file']
```

## 📁 Project Structure

```
/project_root/
│
├── google_drive/           # Google Drive API operations
│   ├── __init__.py
│   ├── api_client.py       # Drive auth, file ops
│   └── uploader.py         # Video/metadata upload
│
├── ai/                     # AI-related functions
│   ├── __init__.py
│   ├── prompt_generator.py # generate_prompt, retry_api_call
│   ├── story_generator.py  # generate, retry_story_generation
│   └── seo.py              # generate_seo_metadata, default_seo_metadata
│
├── media/                  # Media processing
│   ├── __init__.py
│   ├── audio.py            # Kokoro TTS integration
│   ├── video.py            # FFmpeg video creation, thumbnail
│   └── utils.py            # collect_complete_story
│
├── main.py                 # Entry point (orchestrates all modules)
└── config.py               # Constants (API keys, safety_settings)
```

## 📝 Expected Output

The system produces:

1. **Story Text**: A complete narrative with multiple segments
2. **Images**: 6+ high-quality images matching the story
3. **Audio**: Professional narration of the story
4. **Video**: Animated MP4 with transitions and effects
5. **Thumbnail**: Custom image for video platforms
6. **Metadata**: SEO-optimized title, description and tags

Example output video:
![Video Example](https://via.placeholder.com/640x360?text=Story+Video+Example)

## 🔄 Creating the Animations

To create the animated workflow diagrams for this README:

1. **MermaidJS Animations**:
   - Use the Mermaid Live Editor: https://mermaid.live/
   - Copy the flowchart code from this README
   - Export as SVG or record as GIF using screen recording

2. **ScreenToGif for Process Recording**:
   - Download ScreenToGif: https://www.screentogif.com/
   - Record the application running to show the actual workflow
   - Edit and optimize the GIF for web embedding

3. **Matplotlib for Data Flow**:
   - Use Python's Matplotlib to create animated data flow visualizations
   - Save as GIF and embed in the README

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google Gemini AI](https://deepmind.google/technologies/gemini/) for content generation
- [Kokoro TTS](https://github.com/ynop/kokoro) for text-to-speech capabilities
- [FFmpeg](https://ffmpeg.org/) for video processing
