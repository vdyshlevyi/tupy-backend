# Tupy

This repository contains the simple FastAPI app.

## Prerequisites

Before getting started, ensure the following tools are installed:

* [pyenv](https://github.com/pyenv/pyenv)
* [Docker](https://www.docker.com/)

---

## To start development
### Install requirements via poetry:
```bash
make setup
```

### Activate the virtual environment:
```bash
source venv/bin/activate
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

## Usefull checks
### Check code style(ruff):
```bash
make lint
```

### Check types:
```bash
make mypy
```

---
## Docker
### Build Docker image:
```bash
docker build --no-cache -t tupy_backend:0.1.0 .
```

### Check that image was created:
```bash
docker image ls | grep tupy_backend
```


## Quick start via Docker Compose
### Just start project with dependencies using one command:
```bash
docker-compose up --build
# or run as daemon
docker-compose up --build -d
```