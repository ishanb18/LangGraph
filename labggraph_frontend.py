import streamlit as st
from langchain_core.messages import HumanMessage
from langgrapgh_beckend import chatbot

CONFIG = {'configurable':{'thread_id':'1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type Here :")

if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    result = chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)

    aimessage = result['messages'][-1].content

    st.session_state['message_history'].append({'role':'assistant','content':aimessage})
    with st.chat_message('assistant'):
        st.text(aimessage) 
