#!/bin/sh

set -o errexit

alembic upgrade head

python entry.py
