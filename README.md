# Tupy

![CI](https://github.com/vdyshlevyi/tupy-backend/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/vdyshlevyi/tupy-backend/branch/main/graph/badge.svg)](https://codecov.io/gh/vdyshlevyi/tupy-backend)



This repository contains the simple FastAPI app.

## Prerequisites

Before getting started, ensure the following tools are installed:

* [pyenv](https://github.com/pyenv/pyenv)
* [Docker](https://www.docker.com/)
* [wget](https://www.gnu.org/software/wget/)

---

## 1. Clone the repository:
```bash
git clone https://github.com/vdyshlevyi/tupy-backend
cd tupy-backend
```

## 2. Build OSRM server
### To calculate routes, you need an OSRM server, so run the next script
```bash
# Add permission to execute
chmod +x scripts/build-osrm.sh
# Download and prepare data for routes calculation(it will take some time)
scripts/build-osrm.sh
```

## 2.1 Start OSRM server only(Option #1)
### After that, start the OSRM server or run all it once via ```docker```:
```bash
# Start the container with OSRM server
docker run --platform linux/amd64 -t -i -d -p 9010:5000 -v $(pwd)/map-data:/data osrm/osrm-backend osrm-routed --algorithm ch /data/ukraine-latest.osrm
```
### Make sure that the OSRM server is working as expected:
```bash
# Build route Kyiv -> Brovary
curl "http://localhost:9010/route/v1/driving/30.5234,50.4501;30.7906,50.5111?overview=full&geometries=geojson"
````
### The output should be similar to this:
```json
{
  "code": "Ok",
  "routes": [
    {
      "geometry": {"coordinates": [...]},
      "legs": [
        {
          "summary": "",
          "weight": 1234.56,
          "duration": 789.01,
          "steps": [...]
        }
      ],
      "distance": 24980.9,
      "duration": 2130.9,
      "weight_name": "routability",
      "weight": 2130.9
    }
  ],
  "waypoints": [
    {"distance": 35.097846, "name": "вулиця Хрещатик", ...}, 
    {"distance": 12.88704, "name": "вулиця Героїв України", ...}
  ]
}
```

## 2.2 Start FastAPI + PostgreSQL + OSRM server (Option #2)
### Start a project with dependencies using one command:
```bash
docker-compose up --build
# or run as daemon
docker-compose up --build -d
```
### In this case you should have the following services running:
- **OSRM** on port [8000](http://localhost:8000/route/v1/driving/30.5234,50.4501;30.7906,50.5111?overview=false)
- **PostgreSQL** on port [8010](http://localhost:8010)
- **FastAPI** on port [8020](http://localhost:8020/docs)

## 3. Local development
### Install requirements via poetry:
```bash
make setup
```

### Activate the virtual environment:
```bash
source venv/bin/activate
# or
. venv/bin/activate
```

### Copy and fill .env file:
```bash
cp .env_example .env
```

### Start DEV server:
```bash
make run
```
---

## Usefully checks
### Check code style(ruff):
```bash
make lint
```

### Check types:
```bash
make mypy
```

### Run tests:
```bash
make test
```

### Tests coverage:
```bash
make coverage
```

---
## Docker
### Build Docker image:
```bash
docker build --no-cache -t tupy_backend:0.1.0 .
```

### Check that the image was created:
```bash
docker image ls | grep tupy_backend
```
