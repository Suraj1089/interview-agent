from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import config
from interviewer_agent import DemoInterviewer

app = FastAPI(
    title="Interview Agent",
    description="""
        Interview Agent which ask question based on user details
    """,
    debug=config.DEBUG,
    docs_url="/v1/docs",
    redoc_url="/v1/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hirewithaiinterviewer.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobDetails(BaseModel):
    job_role: str | None = None
    job_description: str | None = None


agent: DemoInterviewer | None = None


@app.post('/initialize')
async def start_interview(job_details: JobDetails):
    global agent
    agent = DemoInterviewer(job_role=job_details.job_role,
                            job_description=job_details.job_description)

    response = await agent.stream_audio_response(user_message="Start interview with introduction", initialize=True)
    return StreamingResponse(response, media_type="audio/mpeg")


@app.post('/stream')
async def stream_audio(stream: UploadFile = File(...)):
    global agent
    print(agent)
    if agent is None:
        return {'data': 'error'}
    text_bytes = await stream.read()
    text_string = text_bytes.decode('utf-8')
    audio_output = await agent.stream_audio_response(user_message=text_string)

    return StreamingResponse(audio_output, media_type="audio/mpeg")
