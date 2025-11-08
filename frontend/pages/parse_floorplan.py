import streamlit as st
import requests

BACKEND_URL = "http://backend:8000/parse-floorplan"

st.set_page_config(page_title="Parse Floorplan", page_icon="🏠")
st.title("🏠 Floorplan Debugger")
st.markdown("Upload a single floorplan image to test the parsing model.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Parse Image"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        
        with st.spinner("Processing image..."):
            try:
                response = requests.post(BACKEND_URL, files=files)
                response.raise_for_status()
                
                result = response.json()
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("Parsing Successful!")
                    st.json(result.get("json_output"))
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")