import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from openai import OpenAI
import chromadb
from pathlib import Path
from bs4 import BeautifulSoup
import os

st.title("HW 4")

# Create ChromaDB client
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChromaDB_for_HW')
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_or_create_collection('HW4Collection')

# Create OpenAI client
if 'open_ai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

def add_to_collection(collection, text, file_name):
    # Create embedding
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )

    # Get embedding
    embedding = response.data[0].embedding

    # Add embedding and document to ChromaDB
    collection.add(
        documents=[text],
        ids=[file_name],
        embeddings=[embedding]
    )

def load_htmls_to_collection(folder_path, collection):
    path = Path(folder_path)
    # Loop through the HTML files provided
    for html_path in path.glob('*.html'):
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
        # Splits document in half so we get 2 chunks per document
        midpoint = len(text) // 2
        chunk1 = text[:midpoint]
        chunk2 = text[midpoint:]

        add_to_collection(collection, chunk1, f"{html_path.name}_chunk1")
        add_to_collection(collection, chunk2, f"{html_path.name}_chunk2")

if 'HW4_VectorDB' not in st.session_state:
    chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_HW')
    collection = chroma_client.get_or_create_collection('HW4Collection')

    # Check if collection is empty and load PDFs
    if collection.count() == 0:
        loaded = load_htmls_to_collection('/workspaces/bceutoist688hw1/su_orgs/su_orgs', collection)

    st.session_state.HW4_VectorDB = collection

collection = st.session_state.HW4_VectorDB

model = st.sidebar.selectbox('Which model?', ('mini', 'nano'))

if model == "mini":
    model_to_use = "gpt-5-mini"
if model == "nano":
    model_to_use = "gpt-5-nano"

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

    client = st.session_state.openai_client
    embed_response = client.embeddings.create(
        input=prompt,
        model='text-embedding-3-small'
    )
    query_embedding = embed_response.data[0].embedding

    num_docs = collection.count()
    if num_docs > 0:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, num_docs) # Number of closest documents to return
        )

        # Extract the retrieved text to send to the LLM
        if results and results.get('documents') and len(results['documents'][0]) > 0:
            retrieved_context = "\n\n".join(results['documents'][0])
        else:
            retrieved_context = "No specific context found."
    else:
        retrieved_context = "No specific context found."
    

    system_prompt = {
        'role': 'system', 
        'content': (
            "You are a helpful assistant. Your job is to get a user's question, answer it, "
            "then ask if the user wants more info afterwards. If the user says yes, provide more information "
            "and then ask again if they want more info. If the user says no, go back to asking what you can help with. "
            "Make sure you give your answers in a manner that a 10 year old can understand. "
            "Please clear in your response if you are using the knowledge gained from your RAG context. "
            f"RAG Context: {retrieved_context}"
        )
    }

    recent_messages = st.session_state.messages[-10:]
    api_messages = [system_prompt] + recent_messages

    stream = client.chat.completions.create(
        model=model_to_use,
        messages=api_messages,
        stream=True
    )

    with st.chat_message('assistant'):
        response = st.write_stream(stream)

    st.session_state.messages.append({'role': 'assistant', 'content': response})