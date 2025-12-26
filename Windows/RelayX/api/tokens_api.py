from fastapi import APIRouter
import os, sys
from pathlib import Path

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ROOT, '..', '..')
sys.path.insert(0, PROJECT_ROOT)

from RelayX.core.tokens import create_token, read_token
from RelayX.models.request_models import CreateToken, ReadToken

router = APIRouter()

@router.post("/create_token")
async def token_create(req : CreateToken):
    try:
        status = await create_token(req.password)
        return status
    except Exception as e:
        return e

@router.post("/read_token")
async def token_read(req : ReadToken):
    try:
        await read_token(Path(req.token_path), (req.password).encode(), req.display_name)
    except Exception:
        return