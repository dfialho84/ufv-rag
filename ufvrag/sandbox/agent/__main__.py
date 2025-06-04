from langchain.agents import create_react_agent, Tool, AgentExecutor, tool
from langchain_ollama import ChatOllama
from langchain import hub

llm = ChatOllama(model="llama3:latest", temperature=0)


@tool
def soma(data: str) -> str:
    """Soma dois valores inteiros."""
    valores = data.split(",")
    # print(f"Valores recebidos: {valores}")
    soma = 0
    for item in valores:
        soma += int(item.strip())
    return f"\nThe result of the sum is {soma}\n"
    # return str(data.a + data.b)


tools = [soma]

react_prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print("Agent...")
    # agent.run("Quanto é 2 + 2?")
    result = agent_executor.invoke(input={"input": "Quanto é 2 + 2?"})
    print(result)
