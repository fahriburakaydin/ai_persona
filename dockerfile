# Use an official Python 3.10 slim image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into /app
COPY . .

# Add /app to PYTHONPATH so that modules under /app (like src) can be found
ENV PYTHONPATH=/app

# Expose port 8080 (Cloud Run expects the container to listen on this port)
EXPOSE 8080

# Use the new entry point file, e.g., app.py
CMD ["python", "app.py"]
