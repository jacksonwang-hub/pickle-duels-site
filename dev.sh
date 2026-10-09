#!/usr/bin/env bash
# Build the site and serve dist/ locally. Usage: ./dev.sh [port]
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py

PORT="${1:-${PORT:-4321}}"
echo
echo "Pickle Duels site: http://localhost:${PORT}"
echo "Press Ctrl+C to stop."
exec python3 -m http.server "$PORT" --directory dist
