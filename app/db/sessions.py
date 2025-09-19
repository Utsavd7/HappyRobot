from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.database = mongodb.client.carrier_loads
    print("Connected to MongoDB Atlas")

async def close_mongo_connection():
    mongodb.client.close()
    print("Disconnected from MongoDB Atlas")

def get_database():
    return mongodb.database