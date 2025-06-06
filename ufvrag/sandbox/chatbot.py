from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph

chat = ChatOllama(model='llama3', temperature=0)
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState) -> MessagesState:
    response = chat.invoke(state['messages'])
    if isinstance(response, AIMessage):
        return {"messages": [response]}
    return {"messages": []}

workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
workflow.add_edge("model", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
# config = {"configurable": {"thread_id": "abc123"}}
config = RunnableConfig(configurable={"thread_id": "abc123"})

if __name__ == '__main__':
    print("Bem vindo ao Chatbot")
    while True:
        query = input("\nFaça uma pergunta (/q para sair): ")
        if query.lower() == '/q':
            break
        input_message = HumanMessage(query)
        output = app.invoke(input={'messages': input_message}, config=config)
        output["messages"][-1].pretty_print()
        
    # result = chat.invoke(input=[
    #     HumanMessage(content="Hi! I'm Bob"),
    #     AIMessage(content="Hello Bob! How can I assist you today?"),
    #     HumanMessage(content="What's my name?"),
    # ])
    # print(type(result))
    # print(f"\n{result.content}")
    