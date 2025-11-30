from fastapi import APIRouter
import os, sys

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)


from RelayX.models.request_models import ContactFetch
from RelayX.database.crud import fetch_contacts

router = APIRouter()

@router.post("/contacts")
async def get_contacts(model : ContactFetch):
    contacts = await fetch_contacts(model.username)
    return contacts
