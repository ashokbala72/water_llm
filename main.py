from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from water_llm_engine_2 import (
    overflow_control,
    run_all_analyses,
    generate_contextual_advisory,
    storm_response_coordinator
)

app = FastAPI()

# ✅ CORS Fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # or ["*"] in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ POST Input Schema
class StormRequest(BaseModel):
    location: str
    rainfall_mm: float
    tank_fill_percent: float
    river_fill_percent: float

@app.get("/")
def root():
    return {"message": "Water LLM API is running"}

@app.get("/overflow")
def overflow(location: str = Query("London")):
    return overflow_control(location)

@app.get("/analyse")
def analyse(location: str = Query("London")):
    return run_all_analyses(location)

@app.get("/advisory")
def advisory(location: str = Query("London")):
    return generate_contextual_advisory(location)

# ✅ FIXED: POST + JSON body
@app.post("/storm")
def storm(req: StormRequest):
    return storm_response_coordinator(req.location)
