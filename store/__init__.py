from redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

class RedisStore:

  def __init__(self, key: str = "chat"):
    self._key = key
    self.redis = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, password=os.getenv("REDIS_PASSWORD"))

  def get_history(self) -> str:
        return self.redis.json().get(self._key)

  def save_history(self, question: str, answer: str) -> None:
        chat_history = self.get_history()
        if not chat_history:
            chat_history = []
        chat_history.append({"question": question, "answer": answer})
        self.redis.json().set(self._key, "$", chat_history)
