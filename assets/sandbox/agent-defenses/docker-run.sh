#!/bin/sh
# Run an agent in a container: no network, and the project mounted read-only.
#   ./docker-run.sh               # runs toy_agent.py
#   ./docker-run.sh agent_v0.py
cd "$(dirname "$0")"
docker run --rm --network none \
  -v "$PWD":/work:ro -w /work \
  python:3.12-slim python3 "${1:-toy_agent.py}"
