from fastapi import APIRouter
import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.database.crud import set_block_status
from RelayX.models.request_models import BlockStatus

router = APIRouter()

@router.post("/set_block_state")
async def set_block(request : BlockStatus):
    try:
        onion, block_status = request.onion, request.block_status
        await set_block_status(onion, block_status)
        return {"status" : "Success", "msg": f"User has been {'Blocked' if block_status else 'Unblocked'}"}
    except Exception as e:
        return {"status" : "failed", "msg" : f"[ERROR]\n{e}"}