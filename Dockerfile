FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install openai


COPY Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py

CMD ["python", "Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py"]
