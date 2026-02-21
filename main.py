from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import soundfile as sf
import io

from kittentts import KittenTTS
from pydub import AudioSegment
from pydub.utils import which

# Configure pydub to use ffmpeg
AudioSegment.converter = which("ffmpeg")

app = FastAPI(title="KittenTTS API")

# Initialize the model at startup
m = KittenTTS("KittenML/kitten-tts-mini-0.8")

# Voice mapping from OpenAI-style voices to KittenTTS voices
VOICE_MAPPING = {
    # OpenAI-style -> KittenTTS
    "alloy": "Jasper",
    "echo": "Bruno",
    "fable": "Luna",
    "onyx": "Bruno",
    "shimmer": "Kiki",
    # Direct mapping for KittenTTS voices
    "Jasper": "Jasper",
    "Bella": "Bella",
    "Luna": "Luna",
    "Bruno": "Bruno",
    "Rosie": "Rosie",
    "Hugo": "Hugo",
    "Kiki": "Kiki",
    "Leo": "Leo",
}

DEFAULT_VOICE = "Jasper"
SAMPLE_RATE = 24000


class TTSRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str = DEFAULT_VOICE
    response_format: str = "wav"
    speed: float = 1.0


def convert_audio(audio_data, output_format: str, sample_rate: int = SAMPLE_RATE):
    """Convert audio to the requested format."""
    
    # First, write audio to WAV buffer
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
    wav_buffer.seek(0)
    
    # Load as pydub AudioSegment
    audio_segment = AudioSegment.from_wav(wav_buffer)
    
    # Convert to requested format
    output_buffer = io.BytesIO()
    
    if output_format == "mp3":
        audio_segment.export(output_buffer, format="mp3", bitrate="128k")
        media_type = "audio/mpeg"
        extension = "mp3"
    elif output_format == "wav":
        output_buffer = wav_buffer
        media_type = "audio/wav"
        extension = "wav"
    elif output_format == "ogg":
        audio_segment.export(output_buffer, format="ogg", bitrate="128k")
        media_type = "audio/ogg"
        extension = "ogg"
    else:
        raise ValueError(f"Unsupported format: {output_format}")
    
    output_buffer.seek(0)
    return output_buffer, media_type, extension


@app.post("/v1/audio/speech")
async def create_speech(request: TTSRequest):
    """OpenAI-compatible TTS endpoint."""
    
    # Validate input
    if not request.input:
        raise HTTPException(status_code=400, detail="Input text is required")
    
    # Validate format
    supported_formats = ["wav", "mp3", "ogg"]
    if request.response_format not in supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {', '.join(supported_formats)}"
        )
    
    # Map voice to available voice
    mapped_voice = VOICE_MAPPING.get(request.voice, DEFAULT_VOICE)
    
    try:
        # Generate audio
        audio = m.generate(request.input, voice=mapped_voice)
        
        # Convert to requested format
        audio_buffer, media_type, extension = convert_audio(
            audio, 
            request.response_format,
            SAMPLE_RATE
        )
        
        return Response(
            content=audio_buffer.read(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{extension}"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/v1/models")
async def list_models():
    """List available models (for compatibility)."""
    return {
        "object": "list",
        "data": [
            {"id": "tts-1", "object": "model", "created": 0, "owned_by": "kitten"},
            {"id": "tts-1-hd", "object": "model", "created": 0, "owned_by": "kitten"},
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
