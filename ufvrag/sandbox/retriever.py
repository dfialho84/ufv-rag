from ufvrag.config.vector_store_config import create_vector_store

if __name__ == '__main__':
    vector_store = create_vector_store()
    retriever = vector_store.as_retriever()
    docs = retriever.invoke(input="Jakarta EE")
    for doc in docs:
        print(doc.metadata['source'])
        print(doc.page_content)
        print(20 * '-')
        # for key, item in doc.metadata.items():
        #     print(f'{key}: {item}')
        #     print(20 * '-')