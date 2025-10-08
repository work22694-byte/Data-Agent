import fastapi
from fastapi import FastAPI
from pydantic import BaseModel
from Brain import BrainAgent

app = FastAPI()
agent = BrainAgent()

class UserRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "Agent backend running"}

@app.post("/ask")
def ask_agent(request: UserRequest):
    user_query = request.query
    response = agent.handle_input(user_query)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
