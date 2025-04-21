# Use a Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model files and the prediction script
COPY model.pkl .
COPY encoder.pkl .
COPY vectorizer.pkl .
COPY predict_service.py .

# Expose the port the Flask app runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "predict_service.py"]