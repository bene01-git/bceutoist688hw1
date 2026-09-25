import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("IST688 HW Manager")

page1 = st.Page('HW1.py', title="HW 1")
page2 = st.Page('HW2.py', title="HW 2")
page3 = st.Page('HW3.py', title="HW 3")
page4 = st.Page('HW4.py', title="HW 4")
page5 = st.Page('HW5.py', title="HW 5", default=True)

pg = st.navigation([page1, page2, page3, page4, page5])
st.set_page_config(page_title="HWs")
pg.run()
