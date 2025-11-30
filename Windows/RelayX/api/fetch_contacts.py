from fastapi import APIRouter
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)


from RelayX.models.request_models import ContactFetch
from RelayX.database.crud import fetch_contacts

router = APIRouter()

@router.post("/contacts")
async def get_contacts(model : ContactFetch):
    contacts = await fetch_contacts(model.user_onion)
    return contacts
