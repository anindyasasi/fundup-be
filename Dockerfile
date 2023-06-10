# Use the official Python image as the base image
FROM python: 3.10.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY . .

EXPOSE 5000

# Specify the command to run the Flask app
CMD ["python", "app.py"]
