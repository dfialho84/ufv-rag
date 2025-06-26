from operator import attrgetter, itemgetter
from typing import Any, TypeAlias, cast

from langchain.load import dumps, loads
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_ollama import ChatOllama

from ufvrag.config.vector_store_config import create_vector_store

from .formats import QuestionsList

# from langchain_openai import ChatOpenAI



vector_store = create_vector_store()
retriever = vector_store.as_retriever()
llm = ChatOllama(model="llama3", temperature=0)
# llm = ChatOpenAI(model="llama3", temperature=0)


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


RankedDocument: TypeAlias = tuple[Document, float]


def get_unique_union(docs: list[list[Document]]) -> list[str]:
    flattened_docs = [dumps(doc) for sublist in docs for doc in sublist]
    unique_docs = list(set(flattened_docs))
    return [loads(doc) for doc in unique_docs]


def reciprocal_rank_fusion(
    docs_list: list[list[Document]], k: int = 60
) -> list[RankedDocument]:
    fused_scores: dict[str, float] = {}
    for docs in docs_list:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            # previous_score = fused_scores[doc_str]
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (cast(Document, loads(doc)), score)
        for doc, score in sorted(fused_scores.items(), key=itemgetter(1), reverse=True)
    ]
    return reranked_results


def parse_ranked_docs(ranked_docs: list[RankedDocument]) -> str:
    return "\n\n".join(doc[0].page_content for doc in ranked_docs[:5])


# rag_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
rag_template = (
    "human",
    "You are an assistant for question-answering tasks."
    "Use the following pieces of retrieved context to answer the question."
    "If you don't know the answer, just say that you don't know."
    "Use three sentences maximum and keep the answer concise."
    "Always give the answer in portuguese."
    ""
    "Question: {question}"
    "Context: {context}"
    "Answer:",
)


prompt_template = ChatPromptTemplate.from_messages([rag_template])
rag_chain: Runnable[Any, str] = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

multiquery_template = (
    "human",
    "You are an AI model assistant."
    "Your task is to generate five different versions of the given user question to retrieve relevant "
    "documents from a vector database. By generating multiple perspectives on the user question, "
    "your goal is to help the user overcome some of the limitations of the distance-based similarity search. "
    "Provide these alternative questions separated by new lines. "
    "Always give the answer in portuguese."
    "Original question: {question}",
)
prompt_perspectives = ChatPromptTemplate.from_messages([multiquery_template])
multiquery_chain: Runnable[Any, QuestionsList] = cast(
    Runnable[Any, QuestionsList],
    prompt_perspectives | llm.with_structured_output(QuestionsList),
)
retrieval_chain = (
    multiquery_chain | attrgetter("questions") | retriever.map() | get_unique_union
)

fusion_chain = (
    multiquery_chain
    | attrgetter("questions")
    | retriever.map()
    | reciprocal_rank_fusion
    | parse_ranked_docs
)

fusion_rag_chain: Runnable[Any, str] = (
    {"context": fusion_chain, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

decompostion_generator_template = (
    "human",
    "You are a helpful assistant that generates multiple sub-questions related to an input question. "
    "The goal is to break down the input into a set of sub-problems/sub-questions that can be answered in isolation. "
    "Generate multiple search queries related to: {question} "
    "Answer in portuguese."
    "Output (3 queries):",
)

decompostion_generator_prompt = ChatPromptTemplate.from_messages(
    decompostion_generator_template
)

decomposition_generator_chain: Runnable[Any, list[str]] = (
    decompostion_generator_prompt
    | llm.with_structured_output(QuestionsList)
    | attrgetter("questions")
)

decomposition_rag_template = (
    "human",
    "Here is the question you need to answer:"
    "\n --- \n {question} \n --- \n"
    "Here is any avaiable background question + answer pairs:"
    "\n --- \n {qa_pairs} \n --- \n"
    "Here is additional context relevant to the question:"
    "\n --- \n {context} \n --- \n"
    "Use the above context and any background question + answer pairs to answer the question."
    "Always give the answer in portuguese."
    "Question: {question}"
    "Answer:",
)

decomposition_rag_prompt = ChatPromptTemplate.from_messages(
    [decomposition_rag_template]
)
decomposition_rag_chain: Runnable[Any, str] = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
        "qa_pairs": itemgetter("qa_pairs"),
    }
    | decomposition_rag_prompt
    | llm
    | StrOutputParser()
)

fusion_decomposition_chain: Runnable[Any, str] = (
    {
        "context": itemgetter("question") | fusion_chain,
        "question": itemgetter("question"),
        "qa_pairs": itemgetter("qa_pairs"),
    }
    | decomposition_rag_prompt
    | llm
    | StrOutputParser()
)
