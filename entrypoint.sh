#!/bin/sh

set -o errexit

alembic upgrade head

poetry run python entry.py
