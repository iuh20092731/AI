from redis import Redis
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

load_dotenv()

class RedisStore:

    def __init__(self, key: str = "chat"):
        self._key = key
        self.redis = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, password=os.getenv("REDIS_PASSWORD"))

    def get_history(self) -> str:
        return self.redis.json().get(self._key)

    def get_history_by_id(self, id: str) -> str:
        key = f"{self._key}:{id}"
        return self.redis.json().get(key)

    def save_history(self, question: str, answer: str, id: str = None) -> None:
        key = f"{self._key}:{id}" if id else self._key
        chat_history = self.redis.json().get(key)
        if not chat_history:
            chat_history = []
        
        # Tạo message_id unique cho mỗi tin nhắn
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        chat_history.append({
            "id": message_id,
            "question": question,
            "answer": answer,
            "timestamp": timestamp
        })
        
        self.redis.json().set(key, "$", chat_history)
