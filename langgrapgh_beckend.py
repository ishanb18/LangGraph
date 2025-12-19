from langgraph.graph import StateGraph,START,END
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import BaseMessage,HumanMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages #add reducer
from langgraph.checkpoint.memory import MemorySaver # persistence to save menory

load_dotenv()

class ChatState(TypedDict):

    messages:Annotated[list[BaseMessage],add_messages] # basemessage is all type of message in langchain and add message work as reeducer
    
llm = ChatMistralAI()

def chat_node(state : ChatState):

    message = state['messages']

    response = llm.invoke(message)

    return {'messages':[response]}


checkpoint = MemorySaver()

graph = StateGraph(ChatState)

# node
graph.add_node("chat_node",chat_node)

# edges
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

#compile

chatbot = graph.compile(checkpointer=checkpoint)

chatbot