import streamlit as st
import requests
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="LLM App Template",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 LLM Assistant")
st.markdown("A simple UI connecting to a FastAPI + LangChain backend.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.info(f"Connected to: `{API_URL}`")

# Main Query Interface
query = st.text_area("Enter your prompt:", height=100, placeholder="What is the meaning of life?")

if st.button("Generate Response", type="primary"):
    if not query:
        st.warning("Please enter a prompt first.")
    else:
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/generate",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Response generated!")
                    st.container().markdown(f"### Answer:\n{data['answer']}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend API. Is it running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.caption("Template built with FastAPI, LangChain, Streamlit, and UV.")
