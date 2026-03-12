FROM python:3.10-slim

# Install Java (required by Tika for PDF parsing)
RUN apt-get update && apt-get install -y \
    default-jdk tk \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install dev dependencies
RUN pip install --no-cache-dir pytest tox matplotlib networkx

# Copy source code
COPY . .

# Set Python path so src/ is found
ENV PYTHONPATH=/app/src

CMD ["python", "-m", "pytest", "tests/", "-v"]
