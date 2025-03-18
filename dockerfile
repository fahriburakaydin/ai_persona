# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your project code into the container
COPY . .

# Expose port 8000 if your application provides a web interface
EXPOSE 8000

# Define the command to run your application
CMD ["python", "src/manager/lia_manager.py"]
