from fastapi import APIRouter ; import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue

router = APIRouter()

@router.get("/recieve")
async def recieve_message():
    if incoming_queue.empty():
        return {"msg" : None}
    msg = await incoming_queue.get()
    return {"msg" : msg}