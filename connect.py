import psycopg2
import os
from dotenv import load_dotenv
import redis

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD")
    )

if __name__ == "__main__":
    r = get_redis_connection()
    r.set("foo", "bar")
    print(r.get("foo").decode())