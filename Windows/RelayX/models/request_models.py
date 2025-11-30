from pydantic import BaseModel

class ConnectModel(BaseModel):
    recipient : str
class SendModel(BaseModel):
    msg : str
    recipient_onion : str
class ContactFetch(BaseModel):
    username : str