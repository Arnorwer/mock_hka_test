# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY mock_printer.py .

# Expose port
EXPOSE 5000

# Command
CMD ["python", "mock_printer.py"]
