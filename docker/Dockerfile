# Use an official Python image as the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the Python script to the image
COPY script.py .

# Install the required libraries
RUN pip install kubernetes prometheus_client

# Set the environment variable for Prometheus
ENV prometheus_multiproc_dir /tmp/metrics

# Start the Python script
CMD ["python", "script.py"]

# Expose the Prometheus endpoint
EXPOSE 8000