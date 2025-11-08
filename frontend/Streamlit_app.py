import streamlit as st

st.set_page_config(
    page_title="The Home of my demo",
    page_icon="👋",
)

st.title("Welcome to the my demo! 👋")
st.sidebar.success("Select a page above.")

st.markdown(
    """
    This is the main control panel for the SmartSense Real Estate project.
    
    **👈 Select a page from the sidebar** to get started:
    
    - **🤖 Chatbot:** Talk to the SQL agent to query properties.
    - **📊 Ingest Data:** Upload a new `Property_list.xlsx` file to the database.
    - **🏠 Parse Floorplan:** Upload a single floorplan image for debugging.
    
    This application is the final deliverable for Phase 4.
    """
)