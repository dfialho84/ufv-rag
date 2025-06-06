import re
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ufvrag.config.vector_store_config import create_vector_store


def trim_blank_lines(text: str) -> str:
    return re.sub(r"\n{2,}", "\n", text.strip())


def print_docs(docs: list[Document]) -> None:
    for doc in docs:
        print(20 * "=")
        titulo = doc.metadata["title"]
        source = doc.metadata["source"]
        conteudo = trim_blank_lines(doc.page_content)
        print(f"Título: {titulo}")
        print(f"Fonte: {source}")
        # print(conteudo)
        print(20 * "=")
        # input("\nAperte qualquer tecla pra continuar.")


class QuestionsList(BaseModel):
    """Represents a list of questions"""

    questions: list[str] = Field(description="The list of questions")


template = """
    Pegue a questão a seguir e a reformule de 6 formas diferentes de forma que ela tenha o mesmo significado.
    Como sexto item, inclua a questão original.
    questão: {question}
"""

prompt_template = PromptTemplate.from_template(template=template)
llm = ChatOllama(model="llama3", temperature=0).with_structured_output(QuestionsList)

reformulate_chain = prompt_template | llm


# t = """
#     Reflita sobre a questão a seguir. Caso você a considere complexa, quebre-a em pedaços, como um passo-a-passo.
#     Então, depois de criar uma sequênsica de passos mais simples, tente responder a questão.
#     A resposta deve conter o conjunto de passos e a reflexão sobre cada um deles. A resposta também deve conter a
#     resposta final, claro!

#     questão: {question}
# """
# pt = PromptTemplate.from_template(template=t)

# task_division_chain = pt | llm | StrOutputParser()

llm = ChatOllama(model="llama3", temperature=0)
rag_template = """
    Voce é um assistente que responde a perguntas. Sempre responda em Português.
    Use os seguinte trechos de documentos presente no contexto
    para responder as perguntas. Se atenha ao contexto para responder.
    Se você não souber responder, diga que você não sabe.

    contexto:
    {context}

    Pergunta: {question}
    """
prompt_template = PromptTemplate.from_template(rag_template)
rag_chain = prompt_template | llm | StrOutputParser()


if __name__ == "__main__":
    query = "Você pode me falar sobre o cluster que a DTI possui? Preciso estar vinculado a algum projeto de pesquisa para usar o cluster?"
    # query = input('Faça uma pergunta:\n')

    # response = task_division_chain.invoke(input={'question': query})
    # print(response)

    response: QuestionsList = reformulate_chain.invoke(input={"question": query})  # type: ignore
    # for q in enumerate(response.questions):
    #     print(q)

    vector_store = create_vector_store()
    # retriever = vector_store.as_retriever(
    #     search_type="mmr", search_kwargs={"k": 20, "lambda_mult": 0.7}
    # )
    questions = "\n".join(response.questions)
    print(questions)
    retrieved_docs = vector_store.similarity_search(query)
    # retrieved_docs = retriever.invoke(query)
    print_docs(retrieved_docs)

    context = "\n\n".join(trim_blank_lines(doc.page_content) for doc in retrieved_docs)
    # print(context)
    rag_response = rag_chain.invoke(input={"question": query, "context": context})
    print(query)

    print("---------")
    print(rag_response)
