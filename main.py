from fastapi import FastAPI
from pydantic import BaseModel
from Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY import overflow_control, run_all_analyses, generate_contextual_advisory
import os

app = FastAPI()

class LocationInput(BaseModel):
    location: str

@app.get("/")
def root():
    return {"message": "✅ Water LLM API is live!"}

@app.post("/overflow-control")
def overflow_endpoint(input: LocationInput):
    return overflow_control(input.location)

@app.post("/full-analysis")
def full_analysis_endpoint(input: LocationInput):
    return run_all_analyses(input.location)

@app.post("/contextual-advisory")
def advisory_endpoint(input: LocationInput):
    return generate_contextual_advisory(input.location)
