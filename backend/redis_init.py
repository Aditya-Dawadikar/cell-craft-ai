import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = None

async def init_redis():
    try:
        global redis_client
        redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

        print("Redis connection successful.")
    except Exception as e:
        print("Error connecting to Redis:", e)

def get_redis_cache():
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized yet. Call init_redis() first.")
    return redis_client
