# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the simulator script into the container
COPY simulate_logs.py .

# No external dependencies needed for this simple script,
# but if you added libraries (e.g., pandas), you would add:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script when the container starts
CMD ["python", "simulate_logs.py"]