import requests
import tempfile
from bs4.filter import SoupStrainer
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ufvrag.config.messenger_config import create_rag_consumer
from ufvrag.config.vector_store_config import create_vector_store

vector_store = create_vector_store()
bs4_strainer = SoupStrainer(class_=("post-title", "post-header", "post-content"))


def load_html(url: str) -> list[Document]:
    """
    Load HTML content into the vector store.
    """
    print(f"Loading HTML from {url}...")
    loader = WebBaseLoader(
        web_paths=(url,),
        # bs_kwargs={"parse_only": bs4_strainer},
    )
    return loader.load()


def load_pdf(url: str) -> list[Document]:
    """
    Load PDF content into the vector store.
    """
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_pdf_path = tmp_file.name
    loader = PyPDFLoader(tmp_pdf_path)
    return loader.load()


def load_document(url: str) -> None:
    """
    Load a document from the configured source and process it.
    """
    try:
        if url.lower().endswith(".pdf"):
            docs = load_pdf(url)
        else:
            docs = load_html(url)
        print(f"Loaded {len(docs)} documents from {url}.")
        print(f"Total characters: {len(docs[0].page_content)}")
        # print(docs[0].page_content[:100])
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # chunk size (characters)
            chunk_overlap=200,  # chunk overlap (characters)
            add_start_index=True,  # track index in original document
        )
        all_splits = text_splitter.split_documents(docs)
        print(f"Split into {len(all_splits)} chunks.")
        document_ids = vector_store.add_documents(all_splits)
        print(f"Added {len(document_ids)} documents to the vector store.")
    except:
        print(
            f"Failed to load document from {url}. Please check the URL or the document format."
        )


def load_urls() -> None:
    consumer = create_rag_consumer()
    with consumer as consumer_instance:
        try:
            while True:
                msg = consumer_instance.consume(10)
                if msg:
                    load_document(msg)
                    print(f"Consumed message: {msg}")
                else:
                    print("No messages consumed.")
        except KeyboardInterrupt:
            pass
    print(consumer)
