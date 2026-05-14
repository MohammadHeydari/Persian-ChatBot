from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from bot import generate_bot_response_stream

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):

    return StreamingResponse(
        generate_bot_response_stream(request.message),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
