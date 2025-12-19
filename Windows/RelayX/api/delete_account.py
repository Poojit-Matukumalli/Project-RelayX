from fastapi import APIRouter
import os, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.models.request_models import DeleteAccont
from RelayX.core.delete_account import perform_account_deletion

router = APIRouter()

@router.post("/delete_account")
async def delete_account(req : DeleteAccont):
    if not req.confirm:
        return {"status": "Auth not completed"}
    await perform_account_deletion()
    return {"status":"Success", "msg" : "Restart the app for the changes to take place"}
