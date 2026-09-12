import streamlit as st
from openai import OpenAI
import time
import logging
import anthropic
import requests
from bs4 import BeautifulSoup

st.title("HW 3")
st.write("This is a chatbot that will discuss up to 2 URLs. Just enter your URL(s) on the side and ask your question about them below to start the conversation. This chatbot utilizes a 6-message conversation memory buffer.")

def read_url_content(url):
 try:
    response = requests.get(url)
    response.raise_for_status() # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
 except requests.RequestException as e:
    print(f"Error reading {url}: {e}")
    return None

url1 = st.sidebar.text_input("Enter URL 1:")
url2 = st.sidebar.text_input("Enter URL 2:")

url_context = ""
if url1:
    content1 = read_url_content(url1)
    if content1:
        url_context += f"\n\nContent from URL 1:\n{content1[:5000]}" 
if url2:
    content2 = read_url_content(url2)
    if content2:
        url_context += f"\n\nContent from URL 2:\n{content2[:5000]}"

system_content = (
    "You are a helpful assistant. Your job is to get a user's question, answer it based on the provided URL context, "
    "then ask if the user wants more info afterwards. If the user says yes, provide more information and then ask "
    "again if they want more info. If the user says no, go back to asking what you can help with. "
    "Make sure you give your answers in a manner that a 10 year old can understand."
    f"\n\nURL Context:{url_context}"
)

system_prompt = {'role': 'system', 'content': system_content}
llm_option = st.sidebar.selectbox(
    'Choose Specific LLM',
    ("GPT-5.6 Sol", "Claude Opus 5")
)

if llm_option == "GPT-5.6 Sol":
   model_to_use = "gpt-5.6-sol"
else:
   model_to_use = "claude-opus-5"

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if 'anthropic_client' not in st.session_state:
    st.session_state.anthropic_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

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

    # 6-message conversation buffer (3 user-agent exchanges)
    recent_messages = st.session_state.messages[-6:]

    if llm_option == "GPT-5.6 Sol":
        with st.chat_message('assistant'):
            client = st.session_state.openai_client
            api_messages = [system_prompt] + recent_messages
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=api_messages,
                stream=True
            )
            response = st.write_stream(stream)
    else:
        with st.chat_message('assistant'):
            client = st.session_state.anthropic_client
            # Anthropic already takes the system prompt as a separate parameter for us
            def generate_anthropic_stream():
                with client.messages.stream(
                    model=model_to_use,
                    max_tokens=1500,
                    system=system_content,
                    messages=recent_messages
                ) as stream:
                    for text in stream.text_stream:
                        yield text
            response = st.write_stream(generate_anthropic_stream())

    st.session_state.messages.append({'role': 'assistant', 'content': response})