from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import os
import shutil
import json

# Import your existing logic
from agent import sql_agent
from ingest_logic import run_etl
from inference_logic import parse_floorplan

app = FastAPI(title="SmartSense API")

# --- Model for the /chat endpoint ---
class ChatRequest(BaseModel):
    message: str
    user_id: str = "local"

# --- 1. /chat endpoint (Your existing logic) ---
@app.post("/chat")
async def handle_chat(request: ChatRequest):
    if not sql_agent:
        return {"error": "Agent not initialized."}
    try:
        response = sql_agent.invoke({"input": request.message})
        return {"response": response.get("output", "Sorry, I couldn't find an answer.")}
    except Exception as e:
        return {"response": f"An error occurred: {e}"}

# --- 2. /ingest endpoint (NEW) ---
@app.post("/ingest")
async def trigger_ingest(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Save the uploaded Excel file temporarily
    temp_file_path = f"/app/assets/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run the ETL process in the background
    # This immediately returns a "success" message to the user
    # so the frontend doesn't time out.
    print(f"Starting background ETL for {file.filename}...")
    background_tasks.add_task(run_etl)
    
    return {"message": "File upload successful. Ingestion started in the background."}

# --- 3. /parse-floorplan endpoint (NEW) ---
@app.post("/parse-floorplan")
async def trigger_parse(file: UploadFile = File(...)):
    # Save the uploaded image temporarily
    temp_image_path = f"/tmp/{file.filename}"
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Run the floorplan parsing
        json_string_output = parse_floorplan(temp_image_path)
        
        # Clean up the temp file
        os.remove(temp_image_path)
        
        # Return the raw JSON string
        return {"json_output": json.loads(json_string_output)}
    except Exception as e:
        os.remove(temp_image_path)
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "SmartSense API is running"}