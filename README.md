# Veo v3 Video Generator 🎬

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Generate stunning AI videos using Google's Veo v3 model** - Production-ready Python repository with CLI support

---

## ⚡ Quick Start

### 1️⃣ Install

```bash
# Clone repository
git clone <repository-url>
cd veo-video-generator

# Install dependencies
pip install -r requirements.txt

# Setup API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

Get your API key from [Google AI Studio](https://aistudio.google.com/)

### 2️⃣ Generate Your First Video

**Command Line (Easiest):**
```bash
python veo_generator.py "A cinematic shot of a sunset over mountains"
```

**Python Code:**
```python
from veo_generator import VeoVideoGenerator

generator = VeoVideoGenerator()
video = generator.generate_video(prompt="Your prompt here")
print(f"Video saved to: {video}")
```

**Interactive Mode:**
```bash
python quick_start.py
```

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🎬 **Single Videos** | Generate videos from text prompts |
| 🎞️ **Extended Videos** | Chain multiple scenes (up to 21 scenes) |
| 🖼️ **Image-to-Video** | Animate images with AI |
| 🔍 **Model Discovery** | List and explore 5 Veo models |
| ⚙️ **Full Control** | Customize resolution, aspect ratio, duration |
| 🛡️ **Production Ready** | Logging, error handling, validation |
| 📦 **CLI & Python API** | Use from command line or Python code |

---

## 💻 Command Line Interface

### Generate Single Video

```bash
# Basic usage
python veo_generator.py "Your prompt here"

# With options
python veo_generator.py "Futuristic city" \
  --model veo-3.1-fast-generate-preview \
  --resolution 1080p \
  --duration 8 \
  --aspect-ratio 16:9

# Image-to-video
python veo_generator.py "Animate this scene" --image input.jpg

# Help
python veo_generator.py --help
```

### Generate Extended Video (Scenes)

```bash
# From JSON file
python veo_extension.py scenes.json

# With custom output
python veo_extension.py scenes.json --output my_video.mp4

# Verbose mode
python veo_extension.py scenes.json --verbose
```

**scenes.json format:**
```json
{
  "scenes": [
    {
      "prompt": "A spaceship orbiting Earth",
      "params": {"resolution": "720p"}
    },
    {
      "prompt": "The spaceship enters atmosphere",
      "params": {}
    }
  ]
}
```

### List Available Models

```bash
# List all models
python model_discovery.py

# Get specific model info
python model_discovery.py --model veo-3.1-generate-preview

# Get recommendation
python model_discovery.py --recommend fast

# List all use cases
python model_discovery.py --list-use-cases
```

---

## 🐍 Python API

### Basic Video Generation

```python
from veo_generator import VeoVideoGenerator

generator = VeoVideoGenerator()

# Simple
video = generator.generate_video(
    prompt="A serene lake at sunrise"
)

# Advanced
video = generator.generate_video(
    prompt="Cyberpunk city at night",
    model="veo-3.1-generate-preview",
    resolution="1080p",
    duration_seconds=8,
    aspect_ratio="16:9",
    negative_prompt="people, cars",
    seed=12345
)
```

### Scene-Based Videos

```python
from veo_extension import VeoVideoExtension

extender = VeoVideoExtension()

scenes = [
    {
        "prompt": "Opening scene description",
        "params": {"resolution": "720p", "duration_seconds": 8}
    },
    {
        "prompt": "Second scene continues the story",
        "params": {"aspect_ratio": "16:9"}
    }
]

video = extender.extend_from_scenes(scenes)
# Result: ~15 second video (8s + 7s)
```

### Image-to-Video

```python
video = generator.generate_video_with_image(
    prompt="Animate with gentle camera movement",
    image_path="my_image.jpg",
    duration_seconds=8
)
```

---

## 📖 Parameters Reference

### Video Generation Options

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `model` | See [models](#available-models) | `veo-3.1-generate-preview` | Veo model to use |
| `aspect_ratio` | `16:9`, `9:16` | `16:9` | Video aspect ratio |
| `resolution` | `720p`, `1080p` | `720p` | Video resolution |
| `duration_seconds` | `4`, `6`, `8` | `8` | Video duration |
| `negative_prompt` | Any text | None | Elements to exclude |
| `seed` | Any integer | None | For reproducibility |

### Available Models

| Model | Speed | Quality | Audio | Best For |
|-------|-------|---------|-------|----------|
| `veo-3.1-generate-preview` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | High quality |
| `veo-3.1-fast-generate-preview` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | Quick iteration |
| `veo-3.0-generate-001` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | Production stable |
| `veo-3.0-fast-generate-001` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | Fast stable |
| `veo-2.0-generate-001` | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | Legacy |

---

## ❓ Troubleshooting

**"API key is required"**
- Create `.env` file with `GOOGLE_API_KEY=your_key`

**"ImportError: google-genai"**
- Run: `pip install google-genai`

**"1080p resolution only supports 8 second duration"**
- Use `--duration 8` with 1080p

**Video generation is slow**
- Use `--model veo-3.1-fast-generate-preview`
- Try 720p instead of 1080p

**Enable debug logging**
```bash
python veo_generator.py "prompt" --verbose
```

## 💡 Tips & Best Practices

### Writing Good Prompts
- ✅ **Be specific**: "A red Ferrari racing on a coastal highway at sunset"
- ✅ **Add camera details**: "Wide angle shot of...", "Close-up of..."
- ✅ **Include mood**: "Cinematic", "dramatic lighting", "whimsical"
- ✅ **Use quotes for dialogue**: "Hello world," she said softly

### Performance
- Use **fast models** for testing: `veo-3.1-fast-generate-preview`
- Use **720p** for faster generation
- Generation takes **2-5 minutes** typically
- 1080p only works with **8 second duration**

### Scene-Based Videos
- First scene can be any resolution
- Extension scenes must be **720p**
- Each extension adds **~7 seconds**
- Maximum **21 scenes** (1 initial + 20 extensions)

---

## 📦 Project Structure

```
veo-video-generator/
├── veo_generator.py      # Single video generation (CLI & API)
├── veo_extension.py      # Scene-based extension (CLI & API)
├── model_discovery.py    # Model information (CLI & API)
├── quick_start.py        # Interactive CLI menu
├── config.py             # Configuration
├── utils.py              # Utilities
├── scenes.json           # Example scenes
├── examples/             # Example scripts
│   ├── simple_video_generation.py
│   ├── scene_based_extension.py
│   ├── model_discovery_example.py
│   └── image_to_video.py
└── output/               # Generated videos
```

---

## 📚 More Resources

- **[examples/](examples/)** - Working code examples
- **[Google AI Studio](https://aistudio.google.com/)** - Get your API key
- **[Gemini API Docs](https://ai.google.dev/)** - Official API documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

<div align="center">

**Made with ❤️ using Google's Veo v3**

**v1.0.0** · Python 3.8+

</div>
