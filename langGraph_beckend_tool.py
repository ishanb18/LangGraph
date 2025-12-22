from langgraph.graph import StateGraph,START,END
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
from typing import Annotated,TypedDict
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.graph.message import add_messages
import requests
import os
from langchain_tavily import TavilySearch
os.environ['LANGGRAPH_PROJECT'] = 'chatbot_tool'
load_dotenv()

llm = ChatMistralAI()
# search_tool = DuckDuckGoSearchRun(region = "us-en")
search_tool = TavilySearch(max_results=5)

@tool
def calculator_tool(first_num:float,second_num:float,operation:str) -> dict:
    """
    Docstring for calculator_tool
    Perform a basic arithmetic operation on two numbers.
    
    :param first_num: it is the first number
    :type first_num: float
    :param second_num: it is the second number
    :type second_num: float
    :param operation: it the operation to perform between both the numbers Supported operations: add, sub, mul, div
    :type operation: str
    :return: it return the dict contaning first number,second number and answer after the operation
    :rtype: dict
    """
    try:
        if(operation == 'add'):
            ans = first_num+second_num
        elif(operation == 'sub'):
            ans = first_num-second_num
        elif(operation == 'mul'):
            ans = first_num*second_num
        elif(operation=='div'):
            ans = first_num/second_num
        else:
            return{"error":f"Unsupported operation : {operation}"}
        return{'first_num':first_num,"second_num":second_num,'answer':ans}
    except Exception as e:
        return {"error": str(e)}
    
@tool
def stock_price(symbol :str) ->dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()


tools = [search_tool, stock_price, calculator_tool]
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):

    messages:Annotated[list[BaseMessage],add_messages]

graph = StateGraph(ChatState)


def Chat_node(state:ChatState):
    " LLM node that answers qury and call tools"
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return{'messages':[response]}


tool_node = ToolNode(tools)

graph.add_node("Chat_node",Chat_node)
graph.add_node("tools",tool_node)

conn = sqlite3.connect(database="Database.db",check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph.add_edge(START,"Chat_node")
graph.add_conditional_edges("Chat_node",tools_condition)
graph.add_edge("tools","Chat_node")
chatbot = graph.compile(checkpointer=checkpointer)


def retrive_all_threads():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread)

