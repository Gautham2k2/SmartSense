So, hello! This project of mine is built as a part of CaseStudy provided by SmartSense.
This is a full-stack, AI-powered "Real Estate Search Engine" built as a 48-hour case study. The application ingests, processes, and stores property data, allowing a user to ask complex questions in plain English via a chatbot interface.
The entire system is containerized with Docker and deployable with a single command.

The final application is a multi-page Streamlit dashboard that orchestrates the entire system:

* **🤖 Chatbot:** A conversational interface that allows a user to "chat" to the property database. It is powered by a LangChain SQL Agent using the Groq's llama-3.3-70b-versatile model to translate natural language into SQL queries.
* **📊 Ingest Data:** A file-uploader page that allows a user to upload a `Property_list.xlsx` file. This triggers the complete backend ETL (Extract, Transform, Load) pipeline in the background.
* **🏠 Parse Floorplan:** A debugging tool that allows a user to upload a single floorplan image and receive the JSON output from the custom-trained YOLOv8 computer vision model.

* The project is built on a containerized microservice architecture, managed entirely by `docker-compose`. This ensures portability, scalability, and a clean separation of concerns.
1.  **`frontend` (Streamlit Container):**
    * A simple, multi-page Streamlit application.
    * It is the only part of the system the user interacts with.
    * It makes REST API calls to the backend and *never* talks to the databases directly.

2.  **`backend` (FastAPI Container):**
    * The "brain" of the operation. This Python server exposes three key endpoints as required:
        * `/chat`: Handles chat messages and routes them to the SQL Agent.
        * `/ingest`: Receives an Excel file and triggers the `ingest_logic.py` script as a background task.
        * `/parse-floorplan`: Receives an image and runs the `inference_logic.py` script.

3.  **`mysql_db` (MySQL Container):**
    * The structured (relational) database.
    * Stores all property metadata (price, location, seller, etc.) and the JSON output from the floorplan model.

4.  **`qdrant_db` (Qdrant Container):**
    * The unstructured (vector) database.
    * Stores vector embeddings of property descriptions and certificate text, making them searchable for a future RAG agent.
