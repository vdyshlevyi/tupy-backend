#!/bin/sh

set -o errexit

# alembic upgrade head   # TODO(Valerii Dyshlevyi): add mirations in future

python entry.py
