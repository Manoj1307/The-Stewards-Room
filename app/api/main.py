from fastapi import FastAPI
from app.core.generate import generate_answer
from pydantic import BaseModel

class AskRequest(BaseModel):
    question:str

class AskResponse(BaseModel):
    answer:str

app = FastAPI()

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    answer = generate_answer(request.question)
    return AskResponse(answer=answer)