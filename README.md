# Weather Bucket

This project automates the hourly retrieval of weather data from the [Weather API](https://www.weatherapi.com/) , storing it in a PostgreSQL database. Additionally, it aggregates the daily data and uploads them to a MinIO server bucket for archiving.

## Architecture Overview
![Source](https://github.com/Harshal131/Weather-Bucket/assets/45686725/2bb2d5ee-8b75-444a-9443-217820c5d091)

## Tech Stack
<div>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="50" height="50"/>&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="50" height="50"/>&nbsp;&nbsp;
  <img src="https://static-00.iconduck.com/assets.00/airflow-icon-2048x2048-ptyvisqh.png" alt="airflow" width="50" height="50"/>&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="50" height="50"/>&nbsp;&nbsp;
  <img src="https://w7.pngwing.com/pngs/749/248/png-transparent-minio-hd-logo-thumbnail.png" alt="docker" width="50" height="50"/>&nbsp;&nbsp;
  <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="50" height="50"/>&nbsp;&nbsp;
</div>

## Setup

(1) Clone the repository:

```bash
  git clone https://github.com/Harshal131/Weather-Bucket
```

(2) Navigate to the project directory:

```bash
  cd Weather-Bucket
```

(3) Set up environment variables:

Create an .env file in the project root directory.
Add the following environment variables to the .env file:

```python
# Weather-API
API_KEY=""
API_LOCATION=""

# Postgres 
POSTGRES_HOST=""
POSTGRES_PORT=
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
POSTGRES_SCHEMA=""
POSTGRES_TABLE=""

# Minio
MINIO_HOST=""
MINIO_ACCESS_KEY=""
MINIO_SECRET_KEY=""
MINIO_BUCKET_NAME=""
```

(4) Start docker desktop.

(5) Initialize airflow initial database:
```bash
docker-compose up airflow-init
```
(6) Run the Docker Compose file to start Airflow and Minio services:
```bash
docker-compose up -d
```
## Usage
Access the Airflow UI:

Go to http://localhost:8080.
Use the default Airflow credentials configured in the .env file to log in.

Access the Minio UI:

Go to http://localhost:9000.
Use the Minio access key and secret key configured in the .env file to log in.
