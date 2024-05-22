from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# from elevenlabs import Voice, VoiceSettings, set_api_key, generate, stream, play
from elevenlabs import Voice, VoiceSettings, stream, play
from elevenlabs.client import ElevenLabs

# for mac tts
import shlex # for escaping special shell commands as strings

import os

# Load .env
from dotenv import load_dotenv


# Import VOICE_AI and VOICE_MODEL from custom.py
from yCustom.custom import VOICE_AI, VOICE_MODEL

import logging

# Initialize a logger
logger = logging.getLogger(__name__)

# os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TOKENIZERS_PARALLELISM"] = "true"

class Data(BaseModel):
    input: str
    use_mac_tts: bool

router = APIRouter()

# ------------------------------------ #
#             SETUP DOT.ENV            #
# ------------------------------------ #

# ------------ SCENARIO 1 ------------ #

# set_api_key("xxx")

# ------------ SCENARIO 2 ------------ #
# client = ElevenLabs(
#   api_key="xxx"
# )

# ------------ SCENARIO 3 ------------ #

os.chdir(os.path.dirname(os.path.dirname(__file__)))
load_dotenv('.env')

voice_key = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(
  api_key=voice_key
)

# ------------ SCENARIO 2 ------------ #

VOICE_ID = VOICE_AI
MODEL = VOICE_MODEL

# ------------ SCENARIO 3 ------------ #

# VOICE_ID = os.getenv("VOICE_REBECCA")
# MODEL = os.getenv("VOICE_MODEL_TURBO")

# ------------ SCENARIO 4 ------------ #

# Get voice and model IDs from environment
# Fetch the actual model ID from the .env selection

# VOICE_ID = os.getenv(os.getenv("VOICE_AI"))
# MODEL = os.getenv(os.getenv("VOICE_MODEL"))

@router.post("/speak")
async def speak(data: Data):
    try:
        if data.use_mac_tts:
            #~ DEBUGG
            logger.info(f"\nDEBUGG | speak.py | 🔊 Incoming Mac TTS Audio for text.")

            # Speak the text
            os.system(f"say {shlex.quote(data.input)}")
            
            #~ DEBUGG
            # logger.info(f"\nDEBUGG | speak.py | 🔊 Generated Mac TTS Audio: '{data.input}'")
            logger.info(f"\nDEBUGG | speak.py | 🔊 Generated Mac TTS Audio!")

            return { "message": f"speak.py | 🔊 Generated Mac TTS Audio: \n\n'{data.input}'\n" }
        else:
            #~ Generate the audio stream from the text w/Helper Function
            # audio_stream = client.generate(
            #     text=data.input,
            #     model=MODEL,
            #     stream=True,
            #     voice=Voice(
            #         voice_id=VOICE_ID,
            #         # settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
            #         settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            #     )
            # )
            
            #~ Generate the audio stream from the text w/Out Helper Function
            audio_stream = client.text_to_speech.convert_as_stream(
                text=data.input,
                model_id=MODEL,
                voice_id=VOICE_ID,
                output_format="mp3_44100_192",
                optimize_streaming_latency=3,
                voice_settings=VoiceSettings(
                    stability=1, similarity_boost=1, style=0, use_speaker_boost=True
                )
            )

            # Log the generated audio stream
            logger.info(f"\nDEBUGG | speak.py | 🔊 Incoming 11Labs audio stream for text.")
            
            # Print the response for debugging | this doesn't really tell much since stream!
            # print(f"\nDEBUGG | speak.py | 🔊 Audio Stream Response: {audio_stream}")
            
            # Stream the audio
            stream(audio_stream)

            # Log the Streamed audio
            logger.info(f"\nDEBUGG | speak.py | 🔊 Generated 11Labs Streamed Audio: '{data.input}'")

            return { "message": f"speak.py | 🔊 Generated 11Labs Streamed Audio: '{data.input}'" }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
