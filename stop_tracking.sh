#!/bin/bash

PROCESS_NAME="gsheets_listener.py"

if pgrep -f "$PROCESS_NAME" > /dev/null; then
    echo "Process $PROCESS_NAME found. Attempting to stop..."

    pkill -f "$PROCESS_NAME"

    if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
        echo "Python script stopped successfully."
    else
        echo "Failed to stop Python script. Process still running."
    fi
else
    echo "No running instance of $PROCESS_NAME found."
fi
