import os
from typing import Any
from pymongo import MongoClient
from dotenv import load_dotenv
from ufvrag.repositories.mongo import MongoUrlRepository
from ufvrag.repositories.base import UrlRepository


load_dotenv()


client: MongoClient[Any] = MongoClient(
    host=os.getenv("MONGO_URI"),
    username=os.getenv("MONGO_USERNAME"),
    password=os.getenv("MONGO_PASSWORD"),
)
db = client[os.getenv("MONGO_DB_NAME", "ufvrag")]
url_collection = db["url"]

url_repository: UrlRepository = MongoUrlRepository(collection=url_collection)
