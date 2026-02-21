# KittenTTS API

OpenAI-compatible TTS API built with FastAPI and the great (and fast and tiny) [KittenTTS](https://github.com/KittenML/KittenTTS).

Using `kitten-tts-mini` (80M) model, downloaded on startup.

## Features

* OpenAI-compatible /v1/audio/speech endpoint
* Multiple output formats: WAV, MP3, OGG

## Quick Start

### Using Docker

```bash
# Pull the image
docker pull ghcr.io/<your-username>/kittentts-api:latest

# Run the container
docker run -d -p 8000:8000 ghcr.io/<your-username>/kittentts-api:latest
```

## API Usage

### cURL

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello world!",
    "voice": "Jasper",
    "response_format": "mp3"
  }' \
  -o output.mp3
```

### OpenAI Python Client

```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy",
    base_url="http://localhost:8000/v1"
)

response = client.audio.speech.create(
    model="tts-1",
    input="Hello world!",
    voice="Jasper",
    response_format="mp3"
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

## API Endpoints

| Endpoint              | Description                                       |
| --------------------- | ------------------------------------------------- |
| POST /v1/audio/speech | Generate speech audio                             |
| GET /v1/models        | List available models (`tts-1` for compatibility) |

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for MP3/OGG)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
# Windows:
winget install ffmpeg

# Run the server
uvicorn main:app --reload
```

### Build Docker Image

```bash
docker build -t kittentts-api .
```

## License

AGPLv3
