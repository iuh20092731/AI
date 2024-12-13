from groq import Groq
import os
from dotenv import load_dotenv
from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

load_dotenv()

class AudioTranscriptionResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.max_file_size = 5 * 1024 * 1024
        self.client = Groq(api_key=self.api_key)

    async def speech_to_text(self, file: UploadFile):
        temp_path = None
        try:
            # Check file size
            contents = await file.read()
            await file.close()

            if len(contents) > self.max_file_size:
                return AudioTranscriptionResponse(
                    success=False,
                    error="File âm thanh vượt quá 5MB. Vui lòng ghi âm ngắn hơn."
                )

            # Save temporary file
            temp_path = f"temp_{datetime.now().timestamp()}_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(contents)

            # Transcribe using new Groq API
            with open(temp_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(temp_path, audio_file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json"
                )

            return AudioTranscriptionResponse(
                success=True,
                data=transcription.text
            )

        except Exception as e:
            return AudioTranscriptionResponse(
                success=False,
                error=f"Lỗi khi xử lý âm thanh: {str(e)}"
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
