import redis
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD")
    )

def get_mongo_connection() -> MongoClient:
    return MongoClient(
        host=os.getenv("MONGO_HOST"),
        port=int(os.getenv("MONGO_PORT")),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        authSource=os.getenv("MONGO_AUTH_DB", "admin")
    )

def flush_redis() -> None:
    r = get_redis_connection()
    r.flushdb()
    print("Redis очищен.")

def clear_mongo_logs():
    """
    Очищает все документы в коллекции action_logs,
    при этом сама коллекция и база остаются.
    """
    client = get_mongo_connection()
    db = client["srm_logs"]
    result = db["action_logs"].delete_many({})
    print(f"Удалено документов: {result.deleted_count}")

if __name__ == "__main__":
    flush_redis()
    clear_mongo_logs()