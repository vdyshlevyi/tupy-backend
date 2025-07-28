# ========================
# Stage 1: Build dependencies
# ========================
FROM python:3.13-alpine3.20 AS builder

ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install build tools needed for compiling packages
RUN apk add --no-cache curl git gcc musl-dev libffi-dev

# Install Poetry
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Disable Poetry venv
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy only dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (into app dir)
RUN poetry install --no-root --no-interaction --no-ansi

# ========================
# Stage 2: Runtime image
# ========================
FROM python:3.13-alpine3.20 AS runtime

ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install runtime deps only (no compiler, no curl)
RUN apk add --no-cache libffi

# Copy only installed packages and app code from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY . .

# Permissions (if needed)
RUN chmod +x /app/entrypoint.sh

EXPOSE 9000
ENTRYPOINT ["/app/entrypoint.sh"]
