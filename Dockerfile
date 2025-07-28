# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all necessary files
COPY Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py .

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port (if needed for FastAPI later)
EXPOSE 8000

# Run the engine script directly (can replace with FastAPI server later)
CMD ["python3", "Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py"]