import redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD")
    )

def flush_redis() -> None:
    r = get_redis_connection()
    r.flushdb()
    print("Redis очищен.")

if __name__ == "__main__":
    flush_redis()