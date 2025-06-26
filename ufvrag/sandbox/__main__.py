import json
from typing import Annotated, Any, TypeAlias, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

tool = TavilySearch(max_result=3)
tools: list[BaseTool] = [tool]

MessageType: TypeAlias = list[Any]


class State(TypedDict):
    messages: Annotated[MessageType, add_messages]


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list[BaseTool]):
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, input: State) -> State:
        if messages := input.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input.")
        outputs: MessageType = []
        for tool_call in message.tools_calls:
            tool_name = tool_call["name"]
            tool_result = self.tools_by_name[tool_name].invoke(tool_call["args"])
            message = ToolMessage(
                content=json.dumps(tool_result),
                name=tool_name,
                tool_call_id=tool_call["id"],
            )
            outputs.append(message)
        return State(messages=outputs)


graph_builder = StateGraph(State)

llm = ChatOllama(model="llama3:latest", temperature=0)
# llm_with_tools = llm.bind_tools(tools)
llm_with_tools = llm


def chatbot(state: State) -> State:
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}


tool_node = BasicToolNode(tools)


def route_tools(state: State) -> str:
    if not state["messages"] or len(state["messages"]) == 0:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tools_calls") and len(ai_message.tools_calls) > 0:
        return "tools"
    return END


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot", route_tools, {"tools": "tools", END: END}
)
graph_builder.add_edge("tools", "chatbot")
graph = graph_builder.compile()


def stream_graph_update(user_input: str) -> None:
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


if __name__ == "__main__":
    print("This is a sandbox environment for testing and development purposes.")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting the sandbox.")
                break
            stream_graph_update(user_input)
        except:
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_update(user_input)
            break
