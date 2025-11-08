import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="SmartSense Chatbot", page_icon="🤖")
st.title("🤖 Real Estate Agent Built by Gautham")
st.caption("I can answer questions about properties in the database.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about properties..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(BACKEND_URL, json={"message": prompt})
                response.raise_for_status()
                
                result = response.json()
                answer = result.get("response", "No response from server.")
                
            except requests.exceptions.RequestException as e:
                answer = f"Error connecting to backend: {e}"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})