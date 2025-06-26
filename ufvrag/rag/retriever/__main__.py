from .chains import (decomposition_generator_chain, decomposition_rag_chain,
                     fusion_chain, fusion_decomposition_chain,
                     fusion_rag_chain, multiquery_chain, rag_chain,
                     retrieval_chain)


def format_qa_pair(question: str, answer: str) -> str:
    formatted_string = ""
    formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
    return formatted_string.strip()


if __name__ == "__main__":
    # query = "Quem elaborou o PDTI (Plano Diretor de Tecnologia da Informação)?"
    # query = "Quais são as metas de TI?"
    query = "Quais as lições aprendidas na análise do PDTI anterior?"
    # query = "Quais são as considerações finais em relação ao PDTI?"
    # query = "o PDTI está alinhado a algum outro documento? Quais?"
    # query = "Qual é vigência do PDTI 2024-2029?"
    # query = input('Faça uma pergunta:\n')

    print("Query:", query)

    queries = multiquery_chain.invoke({"question": query})
    print("\n--- Generetaded Queries ---\n")
    for q in queries.questions:
        print(q)

    # d = fusion_chain.invoke({"question": query})
    # for rd in d:
    #     print(rd)

    print("\n=== sub questions ===")
    sub_questions = decomposition_generator_chain.invoke({"question": query})
    for i, sub_question in enumerate(sub_questions, start=1):
        print(f"{i}. {sub_question}")

    print("\n === Generating sub-questions ===")
    qa_pairs = ""
    for q in sub_questions:
        print(f"\n ---\nQuestion: {q}")
        answer = decomposition_rag_chain.invoke({"question": q, "qa_pairs": qa_pairs})
        print(f"Answer: {answer}")
        qa_pair = format_qa_pair(q, answer)
        qa_pairs = qa_pairs + "\n --- \n" + qa_pair

    print("\n\n---------")
    rag_response = rag_chain.invoke(input=query)
    print("rag:", rag_response)
    print("---------")
    fusion_response = fusion_rag_chain.invoke(input=query)
    print("rag fusion:", fusion_response)
    print("---------")
    fd_response = fusion_decomposition_chain.invoke(
        input={"question": query, "qa_pairs": qa_pairs}
    )
    print("rag decomposition:", fd_response)
