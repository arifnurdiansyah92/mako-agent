import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Load Environment Variables
# This loads the OpenAI Key and DB URL from .env before anything else runs
load_dotenv()

# 2. Import Local Modules
# We import the agent logic we just built
from agent import get_or_create_agent
from database import engine

# 3. Setup FastAPI App
app = FastAPI(
    title="Agentic Meal Planner API",
    description="A backend API for an AI nutritionist agent connected to a PostgreSQL database.",
    version="1.0.0"
)

# 4. Configure CORS
# This allows your frontend (e.g., localhost:3000) to talk to this backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # Use unique IDs for different users

class ChatResponse(BaseModel):
    response: str

# 6. The Chat Endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user message, finds the correct agent session, and returns the AI response.
    """
    try:
        # Get the specific agent for this user session
        agent = get_or_create_agent(request.session_id)
        
        # Log for debugging
        logging.info(f"Session: {request.session_id} | User Message: {request.message}")
        
        # Send message to agent (asynchronous call)
        response = await agent.run(request.message)
        
        return ChatResponse(response=str(response))
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 7. Health Check Endpoint
@app.get("/health")
def health_check():
    """
    Simple check to verify API is up and DB is reachable.
    """
    try:
        # Execute a dummy query to test DB connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database_error": str(e)}

# 8. Run Logic (Optional)
if __name__ == "__main__":
    import uvicorn
    # Use 'main:app' to enable hot reloading
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)