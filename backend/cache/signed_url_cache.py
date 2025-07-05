from redis_init import get_redis_cache
from storage.storage_utils import (generate_presigned_get_url,
                                   generate_presigned_post_url)
from typing import Literal
import traceback

CACHE_EXPIRY_SECONDS = 3600

async def get_signed_url(bucket:str, s3_file_path:str, method:Literal["GET","POST"]="GET"):
    try:
        redis = get_redis_cache()

        cached_url = await redis.get(s3_file_path)
        if cached_url:
            # print("Returning cached url")
            return cached_url
        
        signed_url = None
        if method == "GET":
            signed_url = await generate_presigned_get_url(bucket, s3_file_path, CACHE_EXPIRY_SECONDS)
        elif method == "POST":
            signed_url = await generate_presigned_post_url(bucket, s3_file_path, CACHE_EXPIRY_SECONDS)
        else:
            raise ValueError(f"Invalid Method: {method} for get_signed_url()")

        await redis.setex(s3_file_path, CACHE_EXPIRY_SECONDS, signed_url)

        return signed_url
    except Exception as e:
        print(e)
        traceback.print_exc()