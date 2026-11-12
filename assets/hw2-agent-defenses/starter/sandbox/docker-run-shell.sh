#!/bin/sh
# Part II: run one shell command in a container.
#   sh sandbox/docker-run-shell.sh <workspace> <command>
#
# TODO (Part II): lock this container down. Inside the container:
#   - no network at all;
#   - the workspace mounted read-only, except src/ and tests/, which stay writable.
# Hints: docker run --network ..., and -v host:container:ro. A second -v can mount
# a writable folder on top of a read-only one.
WS="$1"; shift
exec docker run --rm -v "$WS":/w -w /w python:3.12-slim sh -c "$*"
