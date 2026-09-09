import streamlit as st
from openai import OpenAI
import time
import logging
import anthropic
import requests
from bs4 import BeautifulSoup

st.title("HW 3")

def read_url_content(url):
 try:
    response = requests.get(url)
    response.raise_for_status() # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
 except requests.RequestException as e:
    print(f"Error reading {url}: {e}")
    return None

system_prompt = {'role': 'system', 'content': ("You are a helpful assistant. Your job is to get a user's question, answer it, then ask if the user wants more info afterwards. If the user says yes, provide more information and then ask again if they want more info. If the user says no, go back to asking what you can help with. Make sure you give your answers in a manner that a 10 year old can understand.")}
llm_option = st.sidebar.selectbox(
    'Choose Specific LLM',
    ("GPT-5.6 Sol", "Claude Opus 5")
)

if llm_option == "GPT-5.6 Sol":
   model_to_use = "gpt-5.6-sol"
else:
   model_to_use = "claude-opus-5"

if 'client' not in st.session_state:
    if llm_option == "GPT-5.6 Sol":
        api_key = st.secrets["OPENAI_API_KEY"]
        st.session_state.client = OpenAI(api_key=api_key)
    else:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        st.session_state.client = anthropic.Anthropic(api_key=api_key)

if 'messages' not in st.session_state:
    st.session_state['messages'] = \
        [{'role': 'assistant', 'content': 'How can I help you?'}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg['role'])
    chat_msg.write(msg['content'])

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('user'):
        st.markdown(prompt)

    recent_messages = st.session_state.messages[-4:]

    api_messages = [system_prompt] + recent_messages

    client = st.session_state.client
    stream = client.chat.completions.create(
        model=model_to_use,
        messages=api_messages,
        stream=True
    )

    with st.chat_message('assistant'):
        response = st.write_stream(stream)

    st.session_state.messages.append({'role': 'assistant', 'content': response})