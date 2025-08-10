# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy and install the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates into the container
COPY app.py auth.py cache.py db.py routes.py wsgi.py ./
COPY templates/ ./templates/

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "debug", "wsgi:app"]