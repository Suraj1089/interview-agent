from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)

from config import config
from interviewer_agent import DemoInterviewer
from websocket_route import manager

app = FastAPI(
    title="Interview Agent",
    description="""
        Interview Agent which ask question based on user details
    """,
    debug=config.DEBUG,
    docs_url="/v1/docs",
    redoc_url="/v1/redoc"
)


async def get_session(
    websocket: WebSocket,
    session_id: Annotated[str | None, Cookie()] = None
):
    print(session_id)
    # TODO 
    # if session_id is None:
    #     raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session_id or "random"


@app.websocket("/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    session_id: Annotated[str, Depends(get_session)]
):
    await manager.connect(websocket)
    agent = DemoInterviewer(job_role="Software engineer",
                            job_description="1 year of experience. required skills python, django, postgres.")
    await agent.stream_response(websocket=websocket, user_prompt="Start iterview with introduction", manager=manager)
    try:
        while True:
            data = await websocket.receive_text()
            await agent.stream_response(websocket=websocket, user_prompt=str(data), manager=manager)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
