from langgraph.graph import StateGraph,START,END
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import BaseMessage,HumanMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages #add reducer
from langgraph.checkpoint.sqlite import  SqliteSaver# persistence to save menory
import sqlite3

conn = sqlite3.connect(database="Database.db",check_same_thread=False)

load_dotenv()

class ChatState(TypedDict):

    messages:Annotated[list[BaseMessage],add_messages] # basemessage is all type of message in langchain and add message work as reeducer
    
llm = ChatMistralAI()

def chat_node(state : ChatState):

    message = state['messages']

    response = llm.invoke(message)

    return {'messages':[response]}


checkpoint = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

# node
graph.add_node("chat_node",chat_node)

# edges
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

#compile

chatbot = graph.compile(checkpointer=checkpoint)
temp = set()
def retrive_all_threads():
    for msg in checkpoint.list(None):
        temp.add(msg.config['configurable']['thread_id'])
    
    return list(temp)