from s3_init import get_s3
import os
from typing import List, Dict

async def get_file_list(bucket: str, session_id: str, commit_id: str) -> List[str]:
    s3 = get_s3()
    prefix = f"{session_id}/{commit_id}/"
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        return [obj["Key"] for obj in contents]
    except Exception as e:
        print("Error listing files:", e)
        return []

async def generate_presigned_get_url(bucket: str, s3_file_path: str, expires_in: int = 3600) -> str:
    s3 = get_s3()
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": s3_file_path},
            ExpiresIn=expires_in
        )
    except Exception as e:
        print("Error generating GET URL:", e)
        return None

async def generate_presigned_post_url(bucket: str, s3_file_path: str, expires_in: int = 3600):
    s3 = get_s3()
    try:
        return s3.generate_presigned_post(
            Bucket=bucket,
            Key=s3_file_path,
            ExpiresIn=expires_in
        )
    except Exception as e:
        print("Error generating POST URL:", e)
        return None

async def upload_file_from_path(bucket: str, local_path: str, session_id: str, commit_id: str, filename: str) -> str:
    s3 = get_s3()
    s3_file_path = f"{session_id}/{commit_id}/{filename}"
    try:
        s3.upload_file(local_path, bucket, s3_file_path)
        return s3_file_path
    except Exception as e:
        print("Upload failed:", e)
        return None

async def upload_commit_folder(bucket: str, local_folder_path: str, session_id: str, commit_id: str) -> List[Dict]:
    """
    Uploads all files in a local commit folder to S3.

    Returns:
        A list of dicts containing file metadata for Commit.generated_files.
    """
    s3 = get_s3()
    uploaded_files = []

    for filename in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, filename)

        if os.path.isfile(file_path):
            s3_file_path = f"{session_id}/{commit_id}/{filename}"
            try:
                s3.upload_file(file_path, bucket, s3_file_path)

                file_type = ""
                ext = s3_file_path.split('.')[-1]
                if ext == 'csv':
                    file_type = "dataframe"
                elif ext in ['png','jpg','jpeg']:
                    file_type = 'chart'
                elif ext == 'md':
                    file_type = "readme"
                else:
                    file_type = ext

                uploaded_files.append({
                    "title": filename,
                    "type": file_type,
                    "url": s3_file_path
                })
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")

    return uploaded_files
