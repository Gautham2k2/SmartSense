import os
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')

load_dotenv(dotenv_path=DOTENV_PATH) 


DB_URL = "mysql+pymysql://root:admin@localhost:3307/smartsense_db"
DB_TABLE_NAME = "properties"

def get_sql_agent_executor():
    print("--- DEBUG: Creating SQL Agent ---")
    
    try:
        db = SQLDatabase.from_uri(
            DB_URL,
            include_tables=[DB_TABLE_NAME] 
        )
        print("--- DEBUG: Connected to SQLDatabase ---")
    except Exception as e:
        print(f"--- FATAL: Could not connect to SQLDatabase: {e} ---")
        return None

    if not os.getenv("GROQ_API_KEY"):
        print("--- FATAL: GROQ_API_KEY not set! ---")
        print(f"   Checked for .env file at: {DOTENV_PATH}")
        return None
        
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True
    )
    
    print("--- DEBUG: SQL Agent Created Successfully ---")
    return agent_executor

try:
    sql_agent = get_sql_agent_executor()
except Exception as e:
    print(f"Failed to initialize agent on startup: {e}")
    sql_agent = None