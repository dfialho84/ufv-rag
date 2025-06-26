from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ufvrag.config.vector_store_config import create_vector_store

vector_store = create_vector_store()

if __name__ == "__main__":
    print("Embeddig PDTI")
    pdf_path = "/home/diego/Downloads/Plano_Diretor_TI_2024-2029.pdf"
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # chunk size (characters)
        chunk_overlap=300,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_documents(docs)
    document_ids = vector_store.add_documents(all_splits)
    print(document_ids)
