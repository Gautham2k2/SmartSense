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
    * This server exposes three key endpoints as required:
        * `/chat`: Handles chat messages and routes them to the SQL Agent.
        * `/ingest`: Receives an Excel file and triggers the `ingest_logic.py` script as a background task.
        * `/parse-floorplan`: Receives an image and runs the `inference_logic.py` script.

3.  **`mysql_db` (MySQL Container):**
    * The structured (relational) database.
    * Stores all property metadata (price, location, seller, etc.) and the JSON output from the floorplan model.

4.  **`qdrant_db` (Qdrant Container):**
    * The unstructured (vector) database.
    * Stores vector embeddings of property descriptions and certificate text, making them searchable for a future RAG agent.
  
## 🗂️ Project Structure

Here is the final structure of the application, designed for a clean separation of concerns and easy Docker deployment.

```txt
SmartSense/
├── .env                 # <-- Your local secrets (DO NOT COMMIT)
├── .env.example         # <-- Public template for environment variables
├── .gitignore           # <-- Tells Git to ignore .env, __pycache__, etc.
├── docker-compose.yml   # <-- Main file to launch the entire application
├── README.md            # <-- You are here!
│
├── assets/              # <-- All static data (Excel, images, certificates)
│   ├── Property_list.xlsx
│   ├── certificates/
│   └── images/
│
├── backend/
│   ├── Dockerfile         # <-- Instructions to build the backend container
│   ├── requirements.txt   # <-- All backend Python dependencies
│   ├── main.py            # <-- FastAPI app: hosts /chat, /ingest, /parse
│   ├── agent.py           # <-- Phase 3: SQL Agent logic (Groq + LangChain)
│   ├── ingest_logic.py    # <-- Phase 2: The ETL pipeline logic
│   └── inference_logic.py # <-- Phase 1: The YOLOv8 parsing logic
│
└── frontend/
│    ├── Dockerfile         # <-- Instructions to build the frontend container
│    ├── requirements.txt   # <-- All frontend Python dependencies
│    ├── Streamlit_App.py   # <-- The main "Welcome" page
│    └── pages/             # <-- Sub-pages for the Streamlit app
│        ├── Chatbot.py
│        ├── Ingest_Data.py
│        └── Parse_Floorplan.py
└── phase_1/
└── phase_2/
└── phase_3/
```

How to Run (Replication Steps):

Follow these steps to build and run the entire application on your local machine.

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* A Git client (like [GitHub Desktop](https://desktop.github.com/))

### Step 1: Clone the Repository
Clone this repository to your local machine.

git clone (https://github.com/Gautham2k2/SmartSense.git)
cd SmartSense

### Step 2: Create Your Environment File
Copy the template: In the project's root directory, make a copy of .env.example and name it .env
Edit .env: Open the new .env file and add your secret API key from Groq:
GROQ_API_KEY="your_gsk_...key_here"
All other database variables are already set for the Docker environment.

### Step 3: Build and Run with Docker Compose
1. Open your terminal in the project's root directory.
2. Run the following command: docker compose up --build

### Step 4: Access the Application
Once all four containers are running, open your web browser and go to: http://localhost:8501


