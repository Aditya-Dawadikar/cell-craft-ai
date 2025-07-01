from s3_init import s3
import os
from typing import List, Dict

def get_file_list(bucket: str, session_id: str, commit_id: str) -> List[str]:
    global s3
    prefix = f"session_files/{session_id}/{commit_id}/"
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        return [obj["Key"] for obj in contents]
    except Exception as e:
        print("Error listing files:", e)
        return []

def generate_presigned_get_url(bucket: str, s3_file_path: str, expires_in: int = 3600) -> str:
    global s3
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": s3_file_path},
            ExpiresIn=expires_in
        )
    except Exception as e:
        print("Error generating GET URL:", e)
        return None

def generate_presigned_post_url(bucket: str, s3_file_path: str, expires_in: int = 3600):
    global s3
    try:
        return s3.generate_presigned_post(
            Bucket=bucket,
            Key=s3_file_path,
            ExpiresIn=expires_in
        )
    except Exception as e:
        print("Error generating POST URL:", e)
        return None

def upload_file_from_path(bucket: str, local_path: str, session_id: str, commit_id: str, filename: str) -> str:
    global s3
    s3_file_path = f"session_files/{session_id}/{commit_id}/{filename}"
    try:
        s3.upload_file(local_path, bucket, s3_file_path)
        return s3_file_path
    except Exception as e:
        print("Upload failed:", e)
        return None

def upload_commit_folder(bucket: str, local_folder_path: str, session_id: str, commit_id: str) -> List[Dict]:
    """
    Uploads all files in a local commit folder to S3.

    Returns:
        A list of dicts containing file metadata for Commit.generated_files.
    """
    global s3
    uploaded_files = []

    for filename in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, filename)

        if os.path.isfile(file_path):
            s3_file_path = f"session_files/{session_id}/{commit_id}/{filename}"
            try:
                s3.upload_file(file_path, bucket, s3_file_path)

                uploaded_files.append({
                    "name": filename,
                    "file_type": filename.split(".")[-1],
                    "s3_file_path": s3_file_path,
                    "s3_url": f"s3://{bucket}/{s3_file_path}"
                })
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")

    return uploaded_files
