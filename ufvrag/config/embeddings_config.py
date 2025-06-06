# from langchain_huggingface.embeddings
# import HuggingFaceEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings


def create_embeddings() -> Embeddings:
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="BAAI/bge-small-en-v1.5",
    # )
    return OllamaEmbeddings(model="llama3")
