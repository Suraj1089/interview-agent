from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from fastapi import WebSocket
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_ai.models.gemini import GeminiModel
from websocket_route import ConnectionManager

from config import config

DEMOINTERVIEW = 'demointerview'
REALINTERVIEW = 'realinterview'


class AiMessage(BaseModel):
    content: str = Field(description="Response from Ai.")
    difficulty_level: Literal['easy', 'medium', 'hard'] = 'easy'


class UserMessage(BaseModel):
    content: str = Field(description="Response given by user")


@dataclass(init=False)
class Interviewer(ABC, Agent):
    def __init__(self,
                 job_role: str,
                 job_description: str,
                 interview_type: Literal['demointerview',
                                         'realinterview'] = REALINTERVIEW,
                 *args, **kwargs
                 ) -> None:
        super().__init__(*args, **kwargs)
        self.job_role = job_role
        self.job_description = job_description
        self.interview_type = interview_type
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
    def __init__(self, job_role: str, job_description: str, *args, **kwargs):
        super().__init__(job_role=job_role, job_description=job_description, *args, **kwargs)

    def get_messages(self):
        return []

    async def stream_response(self, websocket: WebSocket, user_prompt: str, manager: ConnectionManager):
        async with self.agent.run_stream(
            user_prompt=user_prompt,
            result_type=AiMessage,
            message_history=self.get_messages()
        ) as result:
            async for response in result.stream_structured(debounce_by=0.1):
                try:
                    message, is_last_message = response[0].parts[0].args['content'], response[1]
                    if is_last_message:
                        await manager.send_personal_message(message, websocket)
                except Exception as ex:
                    print(ex)
                    await manager.send_personal_message('Having a trouble. can please repeat?', websocket)
                    pass


class RealInterviewer(Interviewer):
    pass
