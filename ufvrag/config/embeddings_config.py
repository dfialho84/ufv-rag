from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings


def create_embeddings() -> Embeddings:
    return OllamaEmbeddings(model="llama3.2")
