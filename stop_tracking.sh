#!/bin/bash
if [ -f script_pid.txt ]; then
    kill "$(cat script_pid.txt)"
    rm script_pid.txt
    echo "Script stopped."
else
    echo "No running script found."
fi
