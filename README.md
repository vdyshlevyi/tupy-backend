# Tupy

This repository contains the simple FastAPI app.

## Prerequisites

Before getting started, ensure the following tools are installed:

* [pyenv](https://github.com/pyenv/pyenv)
* [Docker](https://www.docker.com/)

---

## To start development
### **Install requirements via poetry**:
```bash
make setup
```

### **Activate the virtual environment**:
```bash
source venv/bin/activate
```

### **Copy and fill .env file**:
```bash
cp .env_example .env
```

### **Start DEV server**:
```bash
make run
```
---

## Usefull checks
### **Check code style(ruff)**:
```bash
make lint
```

### **Check types**:
```bash
make mypy
```









```bash
docker-compose up --build  # TODO(Valerii Dyshlevyi): add docker-compose.yaml file
```
