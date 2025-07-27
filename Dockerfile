FROM python:3.13-alpine3.20

# Set environment
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install build dependencies
RUN apk add --no-cache curl git gcc musl-dev libffi-dev

# Install Poetry (latest version)
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy pyproject + lock first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not use a virtualenv
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies via Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of your app
COPY . .

# Expose the port (adjust if needed)
EXPOSE 9000

# Set execute permissions for entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Define the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

