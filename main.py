from fastapi import FastAPI, Query
from water_llm_engine_2 import (
    overflow_control,
    run_all_analyses,
    generate_contextual_advisory,
    storm_response_coordinator
)

app = FastAPI()

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

@app.get("/storm")
def storm(location: str = Query("London")):
    return storm_response_coordinator(location)
