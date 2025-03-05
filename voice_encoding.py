from io import BytesIO
from typing import IO, Union

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import io
import wave
import math
import numpy as np
from config import config


class VoiceModel:
    def __init__(self,
                 *,
                 api_key: str = config.ELEVENLABS_API_KEY,
                 voice_id: str | None = None) -> None:
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.voice_id = voice_id

    def speech_to_text(self, audio_data: Union[BytesIO, bytes]):
        if isinstance(audio_data, BytesIO):
          audio_data = audio_data.read()
        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            # Model to use, for now only "scribe_v1" and "scribe_v1_base" are supported
            model_id="scribe_v1",
            # Tag audio events like laughter, applause, etc.
            tag_audio_events=True,
            # Language of the audio file. If set to None, the model will detect the language automatically.
            language_code="eng",
            diarize=True,  # Whether to annotate who is speaking
     )
        return transcription.text

    def text_to_speech_stream(self, text: str) -> IO[bytes]:
        response = self.client.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            # Optional voice settings that allow you to customize the output
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
                speed=1.0,
            ),
        )
        audio_stream = BytesIO()
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)
        audio_stream.seek(0)
        return audio_stream


    def get_demo_message_stream(self, text: str) -> io.BytesIO:
        import os
        import random 
        random_input = random.choice(['sample.mp3', 'sample1.mp3', 'sample2.mp3'])
        filename = f"/Users/surajpisal/personal/interview-agent/{random_input}"
        # Check if file exists in current directory
        if not os.path.exists(filename):
            raise FileNotFoundError(f"MP3 file '{filename}' not found in the current directory.")
        
        # Open the file and read its contents
        try:
            with open(filename, 'rb') as file:
                # Create a BytesIO stream from the file contents
                mp3_stream = io.BytesIO(file.read())
            
            # Reset stream position to the beginning
            mp3_stream.seek(0)
            
            return mp3_stream
        
        except IOError as e:
            raise IOError(f"Error reading MP3 file: {e}")