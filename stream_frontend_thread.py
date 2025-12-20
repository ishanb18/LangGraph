import streamlit as st
from langchain_core.messages import HumanMessage
from langgrapgh_beckend import chatbot
import uuid

#************************************************* utility function **************************************************

def generate_thread():
    thread = uuid.uuid4()
    return thread

def reset_chat():
    thread_id = generate_thread()
    st.session_state['thread_id']=thread_id
    add_thread_id(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_messages(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values.get('messages',[])


# *************************************************Session Setup************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] =[]

add_thread_id(st.session_state['thread_id'])

#************************************************8 SideBar UI***************************************************

st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversation')

for thread_id in st.session_state['chat_thread'][::-1]:

    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']= thread_id
        messages = load_messages(thread_id)
        temp_message =[]

        for msg in messages:
            if  isinstance(msg,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            
            temp_message.append({'role':role,'content':msg.content})
        
        st.session_state['message_history'] = temp_message

# ***********************************************MAIN UI****************************************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type Here :")

if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}
    with st.chat_message('assistant'):
        # for streaming we use stream instead of invoke and use .write_stram  to display in type write effectr in streamlit

        aimessage = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
        st.session_state['message_history'].append({'role':'asssitant','content':aimessage})
