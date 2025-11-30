from pydantic import BaseModel

class ConnectModel(BaseModel):
    recipient_onion : str
class SendModel(BaseModel):
    msg : str
    recipient_onion : str
class ContactFetch(BaseModel):
    user_onion : str