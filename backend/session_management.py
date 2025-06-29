import os
import json
import uuid
import pandas as pd
import hashlib
import datetime
import traceback
from typing import Union, Optional

SESSION_ROOT = "session_data"
SESSION_STORE_FILE = os.path.join(SESSION_ROOT, "session_store.json")
SESSION_FILES_DIR = os.path.join(SESSION_ROOT, "session_files")

def generate_commit_id(content: Union[str, bytes]) -> str:
    now = datetime.datetime.utcnow().isoformat()

    if isinstance(content, bytes):
        content_str = content.decode("utf-8", errors="ignore")
    elif isinstance(content, str):
        content_str = content
    else:
        raise TypeError("generate_commit_id expects a str or bytes")

    combined = content_str + now
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:8]

# Load and save full session store
def load_session_store():
    if os.path.exists(SESSION_STORE_FILE):
        with open(SESSION_STORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_session_store(store):
    with open(SESSION_STORE_FILE, "w") as f:
        json.dump(store, f, indent=2)

def create_new_session(file_bytes: bytes) -> dict:
    try:
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(SESSION_FILES_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Generate commit ID and create commit-specific folder
        commit_id = generate_commit_id(file_bytes)
        commit_dir = os.path.join(session_dir, commit_id)
        os.makedirs(commit_dir, exist_ok=True)

        # Save CSV inside the commit folder
        csv_path = os.path.join(commit_dir, f"{commit_id}.csv")
        with open(csv_path, "wb") as f:
            f.write(file_bytes)

        # Initial commit metadata
        initial_commit = {
            "commit_id": commit_id,
            "parent_commit": None,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": "Initial upload",
            "mode": "CODE",
            "response": None,
            "key_steps": "Initial file upload",
            "code": None,
            "success": True,
            "error": None
        }

        history_path = os.path.join(session_dir, f"{session_id}_transform_history.json")
        with open(history_path, "w") as f:
            json.dump([initial_commit], f, indent=2)

        session_info = {
            "session_id": session_id,
            "head": commit_id,
            "last_csv_path": csv_path,
            "history_path": history_path,
            "session_dir": session_dir
        }

        session_store = load_session_store()
        session_store[session_id] = session_info
        save_session_store(session_store)

        return session_info

    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")
        return {}

def apply_transform_and_checkpoint(session, df: pd.DataFrame, step: dict, commit_id: Optional[str] = None):
    session_id = session["session_id"]
    session_dir = os.path.join(SESSION_FILES_DIR, session_id)

    parent_commit = session.get("head")

    # Generate new commit ID if not supplied
    if commit_id is None:
        commit_content = json.dumps(step, sort_keys=True)
        commit_id = generate_commit_id(commit_content)

    commit_dir = os.path.join(session_dir, commit_id)
    os.makedirs(commit_dir, exist_ok=True)

    new_csv_path = os.path.join(commit_dir, f"{commit_id}.csv")

    df.to_csv(new_csv_path, index=False)

    commit_record = {
        "commit_id": commit_id,
        "parent_commit": parent_commit,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        **step
    }

    # Update history
    history_path = session["history_path"]
    with open(history_path, "r") as f:
        history = json.load(f)
    history.append(commit_record)
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    session["head"] = commit_id
    session["last_csv_path"] = new_csv_path

    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session, commit_record

def update_history(session, step: dict):
    session_id = session["session_id"]
    session_dir = session["session_dir"]
    parent_commit = session.get("head")

    # Generate new commit ID
    commit_content = json.dumps(step, sort_keys=True)
    commit_id = generate_commit_id(commit_content)

    # Add metadata to the step
    commit_record = {
        "commit_id": commit_id,
        "parent_commit": parent_commit,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        **step
    }

    # Append to history
    with open(session["history_path"], "r") as f:
        history = json.load(f)
    history.append(commit_record)
    with open(session["history_path"], "w") as f:
        json.dump(history, f, indent=2)

    # Update session head
    session["head"] = commit_id

    # Save session store
    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session, commit_record

def list_commits(session: dict) -> list:
    with open(session["history_path"], "r") as f:
        history = json.load(f)

    return [
        {
            "commit_id": h["commit_id"],
            "key_steps": h["key_steps"],
            "timestamp": h.get("timestamp"),
            "parent_id": h.get("parent_commit"),
            "success": h.get("success", False)
        }
        for h in history if h.get("commit_id") != None and h.get("mode") == "CODE"
    ]

def branch_from_commit(session: dict, target_commit_id: str) -> dict:
    session_id = session["session_id"]
    session_dir = session["session_dir"]

    source_csv = os.path.join(session_dir, f"{target_commit_id}.csv")
    if not os.path.exists(source_csv):
        raise FileNotFoundError(f"Commit {target_commit_id} does not exist")

    with open(source_csv, "rb") as f:
        csv_bytes = f.read()

    new_commit_id = generate_commit_id(csv_bytes)
    new_csv_path = os.path.join(session_dir, f"{new_commit_id}.csv")

    with open(new_csv_path, "wb") as f:
        f.write(csv_bytes)

    branch_step = {
        "query": f"Branched from {target_commit_id}",
        "key_steps": "Branch created",
        "code": None,
        "success": True,
        "error": None
    }

    commit_record = {
        "commit_id": new_commit_id,
        "parent_commit": target_commit_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        **branch_step
    }

    # Append to history
    with open(session["history_path"], "r") as f:
        history = json.load(f)
    history.append(commit_record)
    with open(session["history_path"], "w") as f:
        json.dump(history, f, indent=2)

    # Update session state
    session["head"] = new_commit_id
    session["last_csv_path"] = new_csv_path

    # Persist session changes
    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session

def set_head(session: dict, commit_id: str) -> dict:
    session_id = session["session_id"]
    session_dir = session["session_dir"]
    csv_path = os.path.join(session_dir, f"{commit_id}.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV for commit {commit_id} not found")

    session["head"] = commit_id
    session["last_csv_path"] = csv_path

    # Save back to session store
    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session
