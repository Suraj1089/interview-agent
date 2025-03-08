from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from config import config
from voice_encoding import VoiceModel

DEMOINTERVIEW = 'demointerview'
REALINTERVIEW = 'realinterview'


class AiMessage(BaseModel):
    content: str = Field(description="Response or question from Ai.")
    expected_answer: str = Field(description="Expected answer or query from the user.")
    difficulty_level: Literal['easy', 'medium', 'hard'] = 'easy'


class UserMessage(BaseModel):
    content: str = Field(description="Response given by user")

questions = []
@dataclass(init=False)
class Interviewer(ABC, Agent):
    def __init__(self,
                 job_role: str | None = None,
                 job_description: str | None = None,
                 interview_type: Literal['demointerview',
                                         'realinterview'] = REALINTERVIEW,
                 *args, **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.job_role = job_role
        self.job_description = job_description
        self.interview_type = interview_type
        self.questions = questions
        self.responses = {}
        self.agent = Agent(
            model=GeminiModel(model_name='gemini-1.5-flash',
                              api_key=config.GEMINI_API_KEY),
            system_prompt=(
                f"""Your name is John, and your role is to conduct interviews.  
                    You should only ask interview-related questions and avoid unrelated topics.  

                    The interview is for the role of {job_role}, and the job description is: {job_description}.  

                    ### Interview Flow:  
                    1. Begin by asking the candidate to introduce themselves.  
                    2. Start with basic questions related to the job role.  
                    3. Gradually move on to more challenging questions.  
                    4. Provide feedback on each answer:  
                    - If the answer is accurate, respond with positive reinforcement such as "Great answer!" or "Sounds good!"  
                    - If the answer is poor, provide constructive feedback like "You could answer this better."  
                    5. If the candidate struggles to answer, occasionally offer hints when requested.  
                    6. If the candidate is unable to answer multiple difficult questions, mix in some easier ones to keep them engaged.  
                    7. Don't repeat the questions.

                    Always follow these instructions carefully."""
            )
        )

    @abstractmethod
    def stream_response():
        raise NotImplementedError()


class DemoInterviewer(Interviewer):
    def __init__(self,
                 job_role: str | None = None,
                 job_description: str | None = None,
                 *args,
                 **kwargs
                 ):
        super().__init__(job_role=job_role, job_description=job_description, *args, **kwargs)
        self.voice_client = VoiceModel()

    def get_messages(self):
        return self.questions

    async def handle_user_response(self, user_response: bytes):
        decoded_response = self.voice_client.speech_to_text(
            audio_data=user_response)
        return self.stream_audio_response(user_message=decoded_response)
        

    async def stream_audio_response(self, user_message: str | None = None, initialize: bool = False):
        if not initialize and user_message is None:
            raise ValueError("User message is required")
        if user_message is None:
            user_message = "Start interview."
        
        async with self.agent.run_stream(user_prompt=user_message,
                                         result_type=AiMessage, message_history=self.get_messages()) as response:
            message = await response.get_data()
            message = message.content
            audio_stream = self.voice_client.client.text_to_speech.convert_as_stream(
                text=message,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2"
            )
            return audio_stream


        # if not initialize:
        #     key = str(len(self.responses)) if self.responses else str(0)
        #     self.responses[key] = (self.questions[-1], user_message)
        # self.questions.append(message)

        # # ✅ Stream audio response in chunks
        # async for chunk in self.voice_client.text_to_speech_stream(message):
        #     yield chunk  # Properly stream audio chunks



    async def stream_response(self, user_prompt: str):
        async with self.agent.run_stream(
            user_prompt=user_prompt,
            result_type=AiMessage,
            message_history=self.get_messages()
        ) as result:
            async for response in result.stream_structured(debounce_by=0.1):
                try:
                    message, is_last_message = response[0].parts[0].args['content'], response[1]
                    if is_last_message:
                        self.get_messages().append(message)
                except Exception as ex:
                    print(ex)
                    raise ex


class RealInterviewer(Interviewer):
    pass
