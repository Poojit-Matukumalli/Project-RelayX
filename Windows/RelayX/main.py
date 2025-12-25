from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import init, send, recieve, clear_chat, delete_message, delete_account, blocked_state
from api import fetch_history, fetch_contacts, state_ws, file_sending, tokens_api

app = FastAPI()

origins = [
    "*",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, GET, etc.
    allow_headers=["*"],  # Allow all headers
)
app.include_router(send.router)
app.include_router(delete_message.router)
app.include_router(init.router)
app.include_router(recieve.router)
app.include_router(clear_chat.router)
app.include_router(fetch_history.router)
app.include_router(fetch_contacts.router)
app.include_router(state_ws.router)
app.include_router(file_sending.router)
app.include_router(delete_account.router)
app.include_router(blocked_state.router)
app.include_router(tokens_api.router)

@app.get("/status")
def status():
    return {"Online":True}

if __name__ == "__main__":
    uvicorn.run("RelayX.main:app", host="127.0.0.1", port = 8000)