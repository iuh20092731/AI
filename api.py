from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

from model import GroqService, GPTAssistant

class ChatRequest(BaseModel):
    message: str

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize models
gpt_assistant = GPTAssistant()
groq_service = GroqService()

# Transcribe audio
@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile):
    return await groq_service.speech_to_text(file)

# Chat with AI
@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    response = gpt_assistant.process_message(request.message)
    print(response.choices[0].message.content)
    return response.choices[0].message.content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
