# Start from a Python 3.11 base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire frontend source code into the container
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "Streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]