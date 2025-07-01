import os
from dotenv import load_dotenv
import boto3

load_dotenv()

s3 = None

async def init_s3():
    try:
        global s3
        load_dotenv()

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        )

        print("S3 connection successful.")
    except Exception as e:
        print("Error connecting to S3:", e)

def get_s3():
    if s3 is None:
        raise RuntimeError("S3 client is not initialized yet. Call init_s3() first.")
    return s3
