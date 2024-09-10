#!/bin/bash
nohup python3 gsheets_listener.py > script_output.log 2>&1 &
echo "Python script started."
