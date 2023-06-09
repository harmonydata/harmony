# Harmony FastAPI API implementation

API for Harmony.

## Getting started: running the API using Docker

A prerequisite is Tika, which is a PDF parsing library. This must run as a server in Java. We use the Tika Python bindings.

### 1. Run Tika

Download and install Java if you don't have it already. Download and install Apache Tika and run it on your computer https://tika.apache.org/download.html

```
java -jar tika-server-standard-2.3.0.jar
```

### 2. Copy the Harmony library into this directory

```
rm -rf harmony
cp -r ../harmony_pypi_package/src/harmony/ ./
```

### 3. Build Docker container

```
docker build -t harmonyapi .
```

### 4. Run Docker container

Don't forget to expose port 8080:

```
docker run -p 8080:80 harmonyapi
```

You should now be able to visit http://0.0.0.0:8080/docs and view the data.

# MHC data

If you have Mental Health Catalogue data, put it in a data folder e.g. `/data` and set environment variable `DATA_PATH`.

## Deployment

A deployment script for Microsoft Azure is provided in `build_deploy.sh`.

There is also a Github Action script to deploy to Azure in `../.github/workflows/`.