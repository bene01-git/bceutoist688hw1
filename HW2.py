import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("HW 2")

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

import time
import logging
import anthropic

# Configures logging
logging.basicConfig(level=logging.INFO)

# System message for both LLMs
system_message = "You are a helpful assistant."

# Prompt for all LLMs
prompt = "Here's a URL: {url} \n\n---\n\n Summarize the URL's contents in {summary_option}. Please respond in {language}."

if st.sidebar.checkbox("Use advanced model"):
    selected_model = "gpt-5.4-mini" 
else:
    selected_model = "gpt-5.4-nano"

import requests
from bs4 import BeautifulSoup
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
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_url = st.text_input("OpenAI API Key", type="url")

    if uploaded_url:
        url = read_url_content(uploaded_url)
        messages = [
            {
                "role": "user",
                "content": f""{prompt}"",
            }
        ]

        st.write(f"Generating summary using: **{selected_model}**...")

        stream = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            stream=True,
        )
        st.write_stream(stream)
        st.write(stream)
