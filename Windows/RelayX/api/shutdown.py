import sys, os
from fastapi import APIRouter

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ROOT, '..', '..')
sys.path.insert(0, PROJECT_ROOT)

from RelayX.core.delete_account import shutdown_backend
from RelayX.core.tor_bootstrap import stop_tor

router = APIRouter()

@router.post("/shutdown")
async def shutdown():
    try:
        stop_tor()
        await shutdown_backend()
    except Exception as e:
        return {"status": "Fail", "msg":e}