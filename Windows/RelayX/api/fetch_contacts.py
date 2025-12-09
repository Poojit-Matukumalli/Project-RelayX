from fastapi import APIRouter
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.database.crud import fetch_contacts, get_username
from RelayX.utils.config import user_onion


router = APIRouter()

@router.post("/contacts")
async def get_contacts():
    global user_onion
    try:
        contacts = await fetch_contacts(user_onion)
        return contacts
    except Exception as e:
        return {
            "error":"[CONTACT FETCH ERROR]\n",
            "detail" : str(e)     
        }