import streamlit as st
from openai import OpenAI
import time
import logging
import anthropic
import requests
from bs4 import BeautifulSoup

# Show title and description.
st.title("HW 2")

# Configures logging
logging.basicConfig(level=logging.INFO)

# System message for both LLMs
system_message = "You are a helpful assistant."

# Prompt for all LLMs
prompt = "Here's a URL: {url} \n\n---\n\n Summarize the URL's contents in {summary_option}. Please respond in {language}."

llm_option = st.sidebar.selectbox(
    'Choose LLM',
    ("OpenAI", "Claude")
)

# 1. Define the UI elements once
use_advanced = st.sidebar.checkbox("Use advanced model")
use_openai = st.sidebar.checkbox("OpenAI")

if use_advanced:
    if use_openai:
        selected_model = "gpt-5.4-mini"
    else:
        selected_model = "claude-sonnet-5"
else:
    if use_openai:
        selected_model = "gpt-5.4-nano"
    else:
        selected_model = "claude-haiku-4-5-20251001"

summary_option = st.sidebar.selectbox(
    'Choose a summary format',
    ("100 words", "2 connecting paragraphs", "5 bullet points")
)

lang_widget = st.radio("What language do you prefer?", ['English', 'Spanish', 'French', 'Japanese'])

if lang_widget == "English":
   language = "English"
elif lang_widget == "Spanish":
   language = "Spanish"
elif lang_widget == "French":
   language = "French"
else:
   language = "Japanese"

if st.sidebar.checkbox("Use advanced model"):
    if llm_option == "OpenAI":
        selected_model = "gpt-5.4-mini"
    else:
        selected_model = "claude-sonnet-5"
else:
    if llm_option == "OpenAI":
        selected_model = "gpt-5.4-nano"
    else:
        selected_model = "claude-haiku-4-5-20251001"

def read_url_content(url):
 try:
    response = requests.get(url)
    response.raise_for_status() # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
 except requests.RequestException as e:
    print(f"Error reading {url}: {e}")
    return None

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets.OPENAI_API_KEY
anthropic_api_key = st.secrets.ANTHROPIC_API_KEY

if llm_option == "OpenAI":
    client = OpenAI(api_key=openai_api_key)
else:
    client = anthropic.Anthropic(api_key=anthropic_api_key)

# Let the user upload a file via `st.file_uploader`.
uploaded_url = st.text_input("URL", type="url")

if uploaded_url:
    url = read_url_content(uploaded_url)
    st.write(f"Generating summary using: **{selected_model}**...")

    if llm_option == "OpenAI":
        messages = [
                {
                "role": "user",
                "content": prompt
            }
        ]

        stream = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            stream=True
        )

        st.write_stream(stream)
        st.write(stream)
    else:
        message_to_llm = [
                {
                "role": "user",
                "content": [{'type': 'text', 'text': prompt}]
            }
        ]

        message = client.messages.create(
            model=selected_model,
            system=system_message,
            messages=message_to_llm
        )

        data = message.content[0].text
        st.write(data)
