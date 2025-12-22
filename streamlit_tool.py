import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langGraph_beckend_tool import chatbot,retrive_all_threads
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

def get_thread_preview(thread_id, max_len=40):
    messages = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    ).values.get('messages', [])

    # Find first HumanMessage
    for msg in messages:
        if isinstance(msg, HumanMessage):
            preview = msg.content.strip()
            return preview[:max_len] + ("..." if len(preview) > max_len else "")

    return "New Chat"



# *************************************************Session Setup************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] =retrive_all_threads()

add_thread_id(st.session_state['thread_id'])

#************************************************ SideBar UI***************************************************

st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversation')

for thread_id in st.session_state['chat_thread'][::-1]:

    preview_text = get_thread_preview(thread_id)

    if st.sidebar.button(preview_text,key=str(thread_id)):
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


    # CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}

    CONFIG = {
        'configurable':{'thread_id':st.session_state['thread_id']},
        'metadata':{
            "thread_id":st.session_state["thread_id"]
        },
        'run_name':"chat_turn"
        }
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )