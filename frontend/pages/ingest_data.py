import streamlit as st
import requests

BACKEND_URL = "http://backend:8000/ingest"

st.set_page_config(page_title="Ingest Data", page_icon="📊")
st.title("📊 Data Ingestion")
st.markdown("Upload a new `Property_list.xlsx` file to trigger the ETL pipeline.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Start Ingestion"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        
        with st.spinner("Uploading file and starting background process..."):
            try:
                response = requests.post(BACKEND_URL, files=files)
                response.raise_for_status()
                
                result = response.json()
                st.success(result.get("message", "Success!"))
                st.info("The ingestion is running in the background. It may take a few minutes for the data to appear.")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")