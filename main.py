from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from assistant import Assistant

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class ChatRequest(BaseModel):
    conversation_history: list[dict]
    user_query: str


async def stream_chat(request: ChatRequest):
    assistant = Assistant()

    chunks = ''
    async for chunk in assistant.stream(request.conversation_history, request.user_query):
        chunks += chunk
        yield json.dumps({"status": "progress", "content": chunk}, ensure_ascii=False) + "\n"

    completion = json.loads(chunks)
    yield json.dumps({"status": "done", "content": {"report": assistant.report.model_dump(), "completion": completion}}, ensure_ascii=False) + "\n"
    

@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(stream_chat(request), media_type="text/event-stream")
