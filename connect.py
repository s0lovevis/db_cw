import psycopg2
import os
from dotenv import load_dotenv
from pymongo import MongoClient
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

def get_mongo_connection() -> MongoClient:
    return MongoClient(
        host=os.getenv("MONGO_HOST"),
        port=int(os.getenv("MONGO_PORT")),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        authSource=os.getenv("MONGO_AUTH_DB", "admin")
    )