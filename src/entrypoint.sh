#!/bin/sh
echo "Starting app with entrypoint.sh..."
gunicorn --bind 0.0.0.0:5000 --log-level debug app:create_app()
echo "Gunicorn exited with code $?"
echo "Press Ctrl+C to exit or wait..."
tail -f /dev/null
