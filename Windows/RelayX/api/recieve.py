from fastapi import APIRouter ; import sys, os

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.utils.queue import incoming_queue


router = APIRouter()

@router.get("/recieve")
async def recieve_message():
    if incoming_queue.empty():
        return {"msg" : None}
    msg = await incoming_queue.get()
    return {"msg" : msg}