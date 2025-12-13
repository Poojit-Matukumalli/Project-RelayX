from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import sys, os, asyncio

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue
from RelayX.utils.config import user_onion
from RelayX.models.request_models import ConnectModel
from RelayX.database.crud import get_username, fetch_by_id

router = APIRouter()



@router.websocket("/recieve/{recipient_onion}")
async def recieve_message(websocket : WebSocket, recipient_onion : str):
    await websocket.accept()
    try:
        if not await get_username(recipient_onion):
            await websocket.send_json({"error" : "Recipient not found"})
            return
        
        while True:
            msg_id = await incoming_queue.get()
            msg = fetch_by_id(msg_id)
            if not msg:
                continue
            await websocket.send_json({"message" : msg})
    except WebSocketDisconnect:
        print("[WEBSOCKET DISCONNECT]\nClient disconnected from /state")