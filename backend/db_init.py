from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.commit import Commit
from models.session import Session

async def init_db(connection_string:str):
    try:
        client = AsyncIOMotorClient(connection_string, serverSelectionTimeoutMS=5000)
        await client.server_info()

        db = client.get_database("CellCraftAI")
        await init_beanie(database=db, document_models=[Commit, Session])

        print("Successfully connected to MongoDB")

    except Exception as e:
        raise RuntimeError("Failed to connect to MongoDB") from e
