import os
from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStore
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from .embeddings_config import create_embeddings

load_dotenv()


def create_client() -> QdrantClient:
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),  # Replace with your Qdrant server URL
        prefer_grpc=False,  # Set to True if you want to use gRPC
    )


def create_vector_store() -> VectorStore:
    """
    Create a vector store instance based on the configuration.
    """
    client = create_client()
    embeddings = create_embeddings()  # Create embeddings instance
    # print("===============================")
    # print(os.getenv("QDRANT_COLLECTION_NAME", "xxxxx"))
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=os.getenv("QDRANT_COLLECTION_NAME", "xxxxx"),
        embedding=embeddings,
    )
    return vector_store
