# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Add the app directory to the Python path
ENV PYTHONPATH=/app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY src/ .

# Command to run the application
# We use gunicorn for a production-ready server.
# The bot will be run as a web application to handle webhooks from Telegram.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "bot:application"]
