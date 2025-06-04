# from langchain_huggingface.embeddings
# import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


def create_embeddings() -> HuggingFaceEmbeddings:
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
    )
    return embeddings
