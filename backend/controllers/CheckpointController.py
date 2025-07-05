from models.checkpoint import Checkpoint
from models.commit import Commit, GeneratedFile
from models.DocumentMetaData import MetaData
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from controllers.CommitController import (create_commit,
                                          get_commits)
from services.langchain_chain import history_summary_chain

CHECKPOINT_THRESHOLD = 5

# === Create a checkpoint ===
async def create_checkpoint(
    session_id: str,
    summary: str,
    commit_ids: List[str],
    parent_checkpoint: Optional[str] = None
) -> Checkpoint:
    now = datetime.utcnow()
    meta_data = MetaData(created_at=now, last_updated_at=now)

    checkpoint = Checkpoint(
        checkpoint_id=ObjectId(),
        session_id=ObjectId(session_id),
        timestamp=now.isoformat(),
        summary=summary,
        commit_ids=commit_ids,
        parent_checkpoint=parent_checkpoint,
        meta_data=meta_data
    )
    return await checkpoint.insert()

# === Get checkpoint by ID ===
async def get_checkpoint_by_id(checkpoint_id: str) -> Optional[Checkpoint]:
    try:
        oid = ObjectId(checkpoint_id)
    except Exception:
        return None
    return await Checkpoint.find_one(Checkpoint.checkpoint_id == oid)

# === Get latest checkpoint for session ===
async def get_latest_checkpoint_by_session_id(session_id: str) -> Optional[Checkpoint]:
    try:
        sid = ObjectId(session_id)
    except Exception:
        return None

    return await Checkpoint.find(Checkpoint.session_id == sid).sort("-timestamp").first_or_none()

# === List all checkpoints for session ===
async def list_checkpoints_by_session_id(session_id: str, descending: bool = True) -> List[Checkpoint]:
    try:
        sid = ObjectId(session_id)
    except Exception:
        return []

    ordering = [("timestamp", DESCENDING if descending else ASCENDING)]
    return await Checkpoint.find(Checkpoint.session_id == sid).sort(ordering).to_list()

# === Update checkpoint ===
async def update_checkpoint(
    checkpoint_id: str,
    summary: Optional[str] = None,
    commit_ids: Optional[List[str]] = None,
    parent_checkpoint: Optional[str] = None
) -> Optional[Checkpoint]:
    checkpoint = await get_checkpoint_by_id(checkpoint_id)
    if not checkpoint:
        return None

    if summary is not None:
        checkpoint.summary = summary
    if commit_ids is not None:
        checkpoint.commit_ids = commit_ids
    if parent_checkpoint is not None:
        checkpoint.parent_checkpoint = parent_checkpoint

    checkpoint.meta_data.last_updated_at = datetime.utcnow()
    await checkpoint.save()
    return checkpoint

# === Soft delete checkpoint ===
async def delete_checkpoint(checkpoint_id: str) -> bool:
    checkpoint = await get_checkpoint_by_id(checkpoint_id)
    if not checkpoint:
        return False

    checkpoint.meta_data.deleted_at = datetime.utcnow()
    await checkpoint.save()
    return True

async def create_commit_with_checkpoint(
    session_id: str,
    query: str,
    parent_commit: Optional[str],
    key_steps: str,
    response: str,
    code: Optional[str] = None,
    generated_files: Optional[List[GeneratedFile]] = None,
    mode: str = "CODE",
    success: bool = True,
    error: Optional[str] = None
):
    # 1. Create the new commit as usual
    commit_doc = await create_commit(
        session_id=session_id,
        parent_commit=parent_commit,
        query=query,
        mode=mode,
        key_steps=key_steps,
        response=response,
        code=code,
        generated_files=generated_files or [],
        success=success,
        error=error
    )

    # 2. Get the latest checkpoint for the session
    latest_checkpoint = await get_latest_checkpoint_by_session_id(session_id)

    if latest_checkpoint:
        # 3. Append this commit to the latest checkpoint
        latest_checkpoint.commit_ids.append(str(commit_doc.commit_id))
        latest_checkpoint.meta_data.last_updated_at = datetime.utcnow()
        await latest_checkpoint.save()

        # 4. Check if threshold exceeded → summarize and create new checkpoint
        if len(latest_checkpoint.commit_ids) >= CHECKPOINT_THRESHOLD:
            # Fetch the actual commit docs to build the summary
            commits_to_summarize = await get_commits(session_id, commit_ids=latest_checkpoint.commit_ids)
            combined_key_steps = "\n".join([c.key_steps for c in commits_to_summarize if c.key_steps])

            full_history=f"{latest_checkpoint.summary}\n{combined_key_steps}"

            if not full_history:
                full_history = "No significant transformations yet."

            # LangChain summarization call
            summary_response = await history_summary_chain.ainvoke({
                "full_history": full_history
            })
            condensed_summary = summary_response.content.strip()

            # Create new checkpoint with empty queue
            await create_checkpoint(
                session_id=session_id,
                summary=condensed_summary,
                commit_ids=[],  # Starts fresh
                parent_checkpoint=str(latest_checkpoint.id)
            )

    else:
        # 5. No checkpoint exists → create the first checkpoint with this commit
        await create_checkpoint(
            session_id=session_id,
            summary=f"Initial step: {key_steps or 'No description.'}",
            commit_ids=[str(commit_doc.commit_id)],
            parent_checkpoint=None
        )

    return commit_doc