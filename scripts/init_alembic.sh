#!/bin/bash

# Alembic is checked in at repo root (alembic.ini + migrations/).
# Run from project root with DATABASE_URL set, e.g. via docker compose.
alembic upgrade head
