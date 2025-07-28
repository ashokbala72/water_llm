# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . /app

# Create the logs directory
RUN mkdir -p /app/logs

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional, if running web service)
EXPOSE 8000

# Set environment variable for OpenAI key (you can override this in AWS)
ENV OPENAI_API_KEY=your_default_key_here

# Run the app
CMD ["python", "Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY.py"]
