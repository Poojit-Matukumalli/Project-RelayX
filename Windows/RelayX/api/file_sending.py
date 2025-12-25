import os,sys, os
from fastapi import APIRouter

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.core.file_transfer import file_transfer

router = APIRouter()

@router.post("/sendfile/{target_onion}/{file_path:path}")
async def send_file_endpoint(file_path : str, target_onion : str):
    if not os.path.exists(file_path):
        return {"error" : "File path does not exist"}
    await file_transfer(file_path, target_onion)
    return {"status" : "Sent"}