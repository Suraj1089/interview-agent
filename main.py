from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, WebSocket, WebSocketDisconnect

from config import config
from interviewer_agent import DemoInterviewer
from websocket_route import ConnectionManager

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
    manager = ConnectionManager()
    await manager.connect(websocket)
    agent = DemoInterviewer(job_role="Software engineer",
                            job_description="1 year of experience. required skills python, django, postgres.",
                            manager=manager)
    await agent.stream_audio_response(websocket=websocket, initialize=True)
    try:
        while True:
            data = await websocket.receive_bytes()
            await agent.handle_user_response(websocket=websocket, user_response=data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
