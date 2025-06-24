import os
import json
import uuid
import pandas as pd

SESSION_ROOT = "session_data"
SESSION_STORE_FILE = os.path.join(SESSION_ROOT, "session_store.json")
SESSION_FILES_DIR = os.path.join(SESSION_ROOT, "session_files")

# Load and save full session store
def load_session_store():
    if os.path.exists(SESSION_STORE_FILE):
        with open(SESSION_STORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_session_store(store):
    with open(SESSION_STORE_FILE, "w") as f:
        json.dump(store, f, indent=2)

# Create a new session
def create_new_session(file_bytes) -> str:
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(SESSION_FILES_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    original_csv = os.path.join(session_dir, f"{session_id}_t0.csv")
    with open(original_csv, "wb") as f:
        f.write(file_bytes)

    history_path = os.path.join(session_dir, f"{session_id}_transform_history.json")
    with open(history_path, "w") as f:
        json.dump([], f)

    session_info = {
        "session_id": session_id,
        "current_version": 0,
        "last_csv_path": original_csv,
        "history_path": history_path
    }

    session_store = load_session_store()
    session_store[session_id] = session_info
    save_session_store(session_store)

    return session_info

# Save a new checkpoint and update transform history
def apply_transform_and_checkpoint(session, df: pd.DataFrame, step: dict):
    session_id = session["session_id"]
    session_dir = os.path.join(SESSION_FILES_DIR, session_id)

    # Increment version
    session["current_version"] += 1
    v = session["current_version"]

    new_csv = os.path.join(session_dir, f"{session_id}_t{v}.csv")
    df.to_csv(new_csv, index=False)
    session["last_csv_path"] = new_csv

    # Update history
    with open(session["history_path"], "r") as f:
        history = json.load(f)
    history.append(step)
    with open(session["history_path"], "w") as f:
        json.dump(history, f, indent=2)
    
    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session

def update_history(session, step):
    session_id = session["session_id"]

    # Update history
    with open(session["history_path"], "r") as f:
        history = json.load(f)
    history.append(step)
    with open(session["history_path"], "w") as f:
        json.dump(history, f, indent=2)
    
    session_store = load_session_store()
    session_store[session_id] = session
    save_session_store(session_store)

    return session
