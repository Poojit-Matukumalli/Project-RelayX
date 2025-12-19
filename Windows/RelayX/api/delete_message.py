from fastapi import APIRouter, HTTPException
import asyncio, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.database.crud import delete_message
from RelayX.models.request_models import DeleteChat

router = APIRouter()

@router.post("/delete_message")
async def delete_one_message(request: DeleteChat):
    deleted = await delete_message(request.msg_id)
    if deleted:
        return {"status" : "success", "msg" : "Deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Message not found")