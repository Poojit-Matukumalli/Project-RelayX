"""
Fetches contacts and blocked contacts
"""

from fastapi import APIRouter
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.database.crud import fetch_contacts, get_username, fetch_blocked_contacts
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
            "status":"Failed",
            "msg" : f"[CONTACT FETCH ERROR]\n{str(e)}"     
        }

@router.post("/fetch_blocked")
async def get_blocked():
    try:
        blocked_contacts = await fetch_blocked_contacts()
        return get_contacts
    except Exception as e:
        return {"status" : "Failed", "msg" : f"[BLOCKED CONTACT FETCH ERROR]\n{e}"}