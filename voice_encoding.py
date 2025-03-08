from io import BytesIO
from typing import Union

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from config import config


class VoiceModel:
    def __init__(self,
                 *,
                 api_key: str = config.ELEVENLABS_API_KEY,
                 voice_id: str | None = None) -> None:
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id

    def speech_to_text(self, audio_data: Union[BytesIO, bytes]):
        if isinstance(audio_data, BytesIO):
            audio_data = audio_data.read()
        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",
            tag_audio_events=True,
            language_code="eng",
            diarize=True, 
        )
        return transcription.text

    def text_to_speech_stream(self, text: str):
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
        for chunk in response:
            yield chunk

    ### ----------------- DEMO ----------------- ###
    # def get_demo_message_stream(self, text: str) -> io.BytesIO:
    #     random_input = random.choice(
    #         ['sample.mp3', 'sample1.mp3', 'sample2.mp3'])
    #     filename = f"/Users/surajpisal/personal/interview-agent/{random_input}"
    #     # Check if file exists in current directory
    #     if not os.path.exists(filename):
    #         raise FileNotFoundError(
    #             f"MP3 file '{filename}' not found in the current directory.")

    #     try:
    #         with open(filename, 'rb') as file:
    #             # Create a BytesIO stream from the file contents
    #             mp3_stream = io.BytesIO(file.read())

    #         mp3_stream.seek(0)

    #         return mp3_stream

    #     except IOError as e:
    #         raise IOError(f"Error reading MP3 file: {e}")
