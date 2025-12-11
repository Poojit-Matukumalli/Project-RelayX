from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import sys, os, asyncio

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue

router = APIRouter()

@router.websocket("/recieve")
async def recieve_message(websocket : WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await incoming_queue.get()
            await websocket.send_json({"msg" : msg})
    except WebSocketDisconnect:
        print("[WEBSOCKET DISCONNECT]\nClient disconnected from /state")