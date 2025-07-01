from storage.storage_utils import get_s3
from storage.storage_utils import upload_file_from_path
from controllers.SessionController import (create_session,
                                           update_session,
                                           get_session_by_session_id)
from controllers.CommitController import (create_commit,
                                          update_commit,
                                          get_commit_by_id)
import tempfile
import os
from models.requestModels.commit import GeneratedFile
from dotenv import load_dotenv
import traceback
import pandas as pd
from typing import Optional

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

async def create_new_session(file_bytes: bytes, session_name: str) -> dict:
    try:

        # Create Session in DB
        session_doc = await create_session(
            session_name=session_name,
            head=None,
            last_csv_path=None,
            history_path=None,
            session_dir=None
        )

        commit_doc = await create_commit(
            session_id=str(session_doc.session_id),
            query="Initial upload",
            mode="CHAT",
            key_steps="Initial file upload",
            response=None,
            code=None,
            parent_commit=None,
            generated_files=[],
            success=True,
            error=None
        )

        # Create temp file
        temp_dir = tempfile.mkdtemp()
        csv_path = os.path.join(temp_dir, f"{commit_doc.commit_id}.csv")
        with open(csv_path, "wb") as f:
            f.write(file_bytes)

        # Upload to S3
        s3_file_path = await upload_file_from_path(
            bucket=BUCKET_NAME,
            local_path=csv_path,
            session_id=session_doc.session_id,
            commit_id=commit_doc.commit_id,
            filename=f"{commit_doc.commit_id}.csv"
        )

        # Create Commit in DB
        generated_file = GeneratedFile(
            title=f"{commit_doc.commit_id}.csv",
            type="csv",
            url=s3_file_path
        )

        await update_commit(commit_doc.commit_id, generated_files=[generated_file])
        session_info = await update_session(session_doc.session_id,
                             head=str(commit_doc.commit_id),
                             last_csv_path=f"{s3_file_path}",
                             session_dir=f"{session_doc.session_id}/")
        
        return session_info

    except Exception as e:
        traceback.print_exc()
        print(f"Error in create_new_session: {e}")
        return {}

async def apply_transform_and_checkpoint(session_id: str, df: pd.DataFrame, step: dict):
    # 1. Get session document
    session_doc = await get_session_by_session_id(session_id)
    if not session_doc:
        raise ValueError(f"Session {session_id} not found")

    parent_commit = session_doc.head

    # 2. Create new commit in DB
    commit_doc = await create_commit(
        session_id=session_id,
        query=step.get("query", ""),
        mode=step.get("mode"),
        response=step.get("response"),
        key_steps=step.get("key_steps"),
        code=step.get("code"),
        parent_commit=parent_commit,
        generated_files=[],  # Will fill in after S3 upload
        success=step.get("success", True),
        error=step.get("error")
    )

    commit_id = str(commit_doc.commit_id)

    # 3. Save CSV locally and upload to S3
    temp_dir = tempfile.mkdtemp()
    local_csv_path = os.path.join(temp_dir, f"{commit_id}.csv")
    df.to_csv(local_csv_path, index=False)

    s3_file_path = upload_file_from_path(
        bucket=BUCKET_NAME,
        local_path=local_csv_path,
        session_id=session_id,
        commit_id=commit_id,
        filename=f"{commit_id}.csv"
    )

    # 4. Update commit with generated file info
    generated_file = GeneratedFile(
        title=f"{commit_id}.csv",
        type="csv",
        url=f"s3://{BUCKET_NAME}/{s3_file_path}"
    )

    commit_doc = await update_commit(commit_id, generated_files=[generated_file])

    # 5. Update session head
    session_doc = await update_session(
        session_id=session_id,
        head=commit_id,
        last_csv_path=s3_file_path
    )

    return session_doc, commit_doc

async def branch_from_commit(session_id: str, parent_commit_id: str) -> dict:
    # 1. Get session info
    session = await get_session_by_session_id(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # 2. Get CSV key for target commit (assume it's stored or same as head)
    temp_path = f"session_files/{session_id}/{parent_commit_id}/{parent_commit_id}.csv"

    # 3. Download the original CSV file to a temp file
    s3 = get_s3()
    s3.download_file(
        BUCKET_NAME,
        f"session_files/{session_id}/{parent_commit_id}/{parent_commit_id}.csv",
        temp_path
    )

    # 4. Create new commit document (child of target_commit_id)
    commit_doc = await create_commit(
        session_id=session_id,
        query=f"Branched from {parent_commit_id}",
        mode="CODE",
        key_steps="Branch created",
        response=None,
        code=None,
        parent_commit=parent_commit_id,
        generated_files=[],
        success=True,
        error=None
    )
    new_commit_id = str(commit_doc.commit_id)


    # 5. Upload copied CSV to new S3 path
    s3_file_path = upload_file_from_path(
        bucket=BUCKET_NAME,
        local_path=temp_path,
        session_id=session_id,
        commit_id=new_commit_id,
        filename=f"{new_commit_id}.csv"
    )

    # 6. Update commit with new file info
    generated_file = GeneratedFile(
        name=f"{new_commit_id}.csv",
        file_type="csv",
        url=f"session_files/{session_id}/{parent_commit_id}/{parent_commit_id}.csv"
    )
    
    commit_doc = await update_commit(new_commit_id, generated_files=[generated_file])

    # 7. Update session head + last_csv_path
    session_doc = await update_session(
        session_id=session_id,
        head=new_commit_id,
        last_csv_path=s3_file_path
    )

    return session_doc, commit_doc

async def set_head(session_id: str, commit_id: str) -> dict:
    session_doc = get_session_by_session_id(session_id)
    commit_doc = get_commit_by_id(commit_id)

    session_doc = await update_session(head=commit_doc.commit_id,
                                       last_csv_path=f"{commit_doc.commit_id}\{commit_doc.commit_id}.csv")

    return session_doc
