from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from phase_3.agent import sql_agent # Import our pre-initialized agent

app = FastAPI()
class ChatRequest(BaseModel):
    message: str
    user_id: str = "local"

@app.get("/")
def read_root():
    return {"status": "Real Estate Chatbot is running"}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    if not sql_agent:
        return {"error": "Agent not initialized. Check server logs."}
        
    print(f"Received message: {request.message}")
    
    try:
        response = sql_agent.invoke({"input": request.message})
        
        answer = response.get("output", "Sorry, I couldn't find an answer.")
        
        return {"response": answer}
        
    except Exception as e:
        print(f"Error during agent invocation: {e}")
        return {"response": f"An error occurred: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)