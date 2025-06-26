import re
import tempfile

import requests
import trafilatura
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ufvrag.config.messenger_config import create_embeddings_consumer
from ufvrag.config.repository_config import url_repository
from ufvrag.config.vector_store_config import create_vector_store
from ufvrag.models import Url
from ufvrag.utils.interrupt import ShouldStopFn, safe_interrupt_loop

consumer = create_embeddings_consumer()
vector_store = create_vector_store()


def load_html(url: str) -> list[Document]:
    """
    Load HTML content into the vector store.
    """
    print(f"Loading HTML from {url}...")
    # loader = WebBaseLoader(
    #     web_paths=(url,),
    # )
    # return loader.load()
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(
        downloaded,
        include_formatting=True,
        include_links=False,  # opcional
        include_comments=False,  # opcional
    )
    if text is None:
        return []
    return [Document(page_content=text, metadata={"source": url})]


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


def trim_blank_lines(text: str) -> str:
    return re.sub(r"\n{2,}", "\n", text.strip())


def trim_document(doc: Document) -> Document:
    doc.page_content = trim_blank_lines(doc.page_content)
    return doc


def load_document(url: Url) -> bool:
    """
    Load a document from the configured source and process it.
    """
    try:
        if url.url.lower().endswith(".pdf"):
            docs = load_pdf(url.url)
        else:
            docs = load_html(url.url)
        print(f"Loaded {len(docs)} documents from {url.url}.")
        print(f"Total characters: {len(docs[0].page_content)}")
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base", chunk_size=1000, chunk_overlap=100
        )
        # text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=1000,  # chunk size (characters)
        #     chunk_overlap=200,  # chunk overlap (characters)
        #     add_start_index=True,  # track index in original document
        # )
        all_splits = list(map(trim_document, text_splitter.split_documents(docs)))
        print(f"Split into {len(all_splits)} chunks.")
        document_ids = vector_store.add_documents(all_splits)
        print(f"Added {len(document_ids)} documents to the vector store.")
        return True
    except:
        print(
            f"Failed to load document from {url}. Please check the URL or the document format."
        )
        return False


@safe_interrupt_loop  # type: ignore
def load_urls(should_stop: ShouldStopFn) -> None:
    with consumer as consumer_instance:
        while True:
            msg = consumer_instance.consume(10)
            if msg:
                url = url_repository.find_by_url(url=msg)
                if url is None:
                    continue
                loaded = load_document(url)
                if loaded:
                    url.loaded = True
                    url_repository.update(url)
                print(f"Consumed me ssage: {msg}")
            else:
                print("No messages consumed.")

            if should_stop():
                print("Loop interrupted")
                break
    return
