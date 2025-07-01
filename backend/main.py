from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import json
import dotenv
from store import session_cache
from routes import gemini_agent
from routes import version_history
from routes import sessions
from routes import db_commits
from routes import db_sessions

from db_init import init_db
from s3_init import init_s3

dotenv.load_dotenv()

def cleanup_old_files(folder, expiry_secs=3600):
    now = time.time()
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > expiry_secs:
            os.remove(fpath)


app = FastAPI()

SESSION_ROOT = os.getenv("SESSION_ROOT","session_data")
SESSION_STORE_FILE = os.path.join(SESSION_ROOT, "session_store.json")
SESSION_FILES_DIR = os.path.join(SESSION_ROOT, "session_files")

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=SESSION_ROOT), name='static')

app.include_router(gemini_agent.router)
app.include_router(version_history.router)
app.include_router(sessions.router)
app.include_router(db_sessions.router)
app.include_router(db_commits.router)


def save_sessions():
    with open(SESSION_STORE_FILE, "w") as f:
        json.dump(session_cache, f, indent=2)

@app.on_event("startup")
async def setup_session_storage():

    # initialize MongoDB
    await init_db(MONGODB_CONNECTION_STRING)

    # initialize S3 storage
    await init_s3()

    # Create folder structure
    os.makedirs(SESSION_FILES_DIR, exist_ok=True)

    # Create or load session_store.json
    if not os.path.exists(SESSION_STORE_FILE):
        with open(SESSION_STORE_FILE, "w") as f:
            json.dump({}, f, indent=2)
        session_cache.clear()
        print("Created new session_store.json")
    else:
        try:
            with open(SESSION_STORE_FILE, "r") as f:
                # session_cache = json.load(f)
                session_cache.clear()
                session_cache.update(json.load(f))
            print(f"Loaded {len(session_cache)} sessions from session_store.json")
        except json.JSONDecodeError:
            print("Corrupt session_store.json — resetting")
            session_cache.clear()
            save_sessions()

