from fastapi import APIRouter
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ROOT, '..', '..')
sys.path.insert(0, PROJECT_ROOT)

from RelayX.core.tokens import create_token
from RelayX.models.request_models import CreateToken

router = APIRouter()

@router.post("/token")
async def token_create(req : CreateToken):
    try:
        status = await create_token(req.password)
        return status
    except Exception as e:
        return e