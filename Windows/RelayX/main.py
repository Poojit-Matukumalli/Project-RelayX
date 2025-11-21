from fastapi import FastAPI
import uvicorn

from api import init, connect, send, recieve

app = FastAPI()

app.include_router(init.router)
app.include_router(connect.router)
app.include_router(send.router)
app.include_router(recieve.router)

@app.get("/status")
def status():
    return {"Online":True}

if __name__ == "__main__":
    uvicorn.run("RelayX.main:app", host="127.0.0.1", port = 8000)