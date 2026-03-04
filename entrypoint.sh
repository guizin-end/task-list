#!/usr/bin/env bash
set -eu

alembic upgrade head

exec "$@"