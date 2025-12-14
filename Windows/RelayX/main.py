from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import init, connect, send, recieve, clear_chat, fetch_history, fetch_contacts, state_ws, file_sending

app = FastAPI()

origins = [
    "*",  # Allows requests from ALL origins for testing/local HTML file use
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

app.include_router(init.router)
app.include_router(connect.router)
app.include_router(send.router)
app.include_router(recieve.router)
app.include_router(clear_chat.router)
app.include_router(fetch_history.router)
app.include_router(fetch_contacts.router)
app.include_router(state_ws.router)
app.include_router(file_sending.router)

@app.get("/status")
def status():
    return {"Online":True}

if __name__ == "__main__":
    uvicorn.run("RelayX.main:app", host="127.0.0.1", port = 8000)