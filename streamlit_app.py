import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("IST688 HW Manager")

page1 = st.Page('HW1.py', title="HW 1")
page2 = st.Page('HW2.py', title="HW 2", default=True)

pg = st.navigation([page1, page2])
st.set_page_config(page_title="HWs")
pg.run()
