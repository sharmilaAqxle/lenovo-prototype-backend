from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example model for request/response
class Message(BaseModel):
    text: str
    user_id: Optional[str] = None

# Example endpoint
@app.get("/")
async def root():
    return {"message": "API is running"}

# Example POST endpoint
@app.post("/api/message")
async def process_message(message: Message):
    # Add your processing logic here
    return {
        "response": f"Received: {message.text}",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 