#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=backend.settings
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

cd /home/runner/workspace

echo "Starting Django backend on port 8000..."
python -m django runserver 0.0.0.0:8000 &
DJANGO_PID=$!

sleep 2

echo "Django started with PID: $DJANGO_PID"

echo "Starting Express/Vite frontend on port 5000..."
NODE_ENV=development npx tsx server/index-dev.ts &
VITE_PID=$!

echo "Vite started with PID: $VITE_PID"

trap "echo 'Shutting down...'; kill $DJANGO_PID $VITE_PID 2>/dev/null" EXIT

wait
