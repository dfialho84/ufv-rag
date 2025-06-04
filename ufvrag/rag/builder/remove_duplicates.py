import os
import requests
from dotenv import load_dotenv
from typing import Mapping, Any, Generator
from ufvrag.config.repository_config import url_collection
from ufvrag.config.vector_store_config import create_client, create_vector_store

load_dotenv()


def get_duplicate_urls() -> Generator[str, None, None]:
    pipeline: list[Mapping[str, Any]] = [
        {
            "$group": {
                "_id": "$digest",
                "urls": {"$addToSet": "$url"},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"_id": 0, "digest": "$_id", "urls": 1}},
    ]
    result = url_collection.aggregate(pipeline)
    for doc in result:
        for url in doc["urls"][1:]:
            yield url


qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "ufvrag")

client = create_client()
vector_store = create_vector_store()


def remove_documents_by_source(source: str) -> None:
    url = f"{qdrant_url}/collections/{collection_name}/points/delete"
    payload = {"filter": {"must": [{"key": "source", "match": {"value": source}}]}}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Pontos com 'source' especificado foram removidos com sucesso.")
        # num_to_delete = response.json() #["result"]["count"]
        # print(f"Documentos que foram removidos: {num_to_delete}")
    else:
        print(f"Erro ao deletar pontos: {response.status_code} - {response.text}")
    # docs = vector_store.similarity_search(
    #     query="",
    #     k=100,
    #     filter={"must": [{"key": "source", "match": {"value": source}}]},
    # )
    # ids_to_delete = [doc.metadata["id"] for doc in docs]
    # if len(ids_to_delete) > 0:
    #     print("Apagando ids:")
    #     for id in ids_to_delete:
    #         print(f"\t{id}")

    #     vector_store.delete(ids=ids_to_delete)
    return None


if __name__ == "__main__":
    print("Removing duplicates...")
    urls = get_duplicate_urls()
    i = 0
    for url in urls:
        i += 1
        print(f"{i} - Removing {url}...")
        remove_documents_by_source(url)
    print(i)
