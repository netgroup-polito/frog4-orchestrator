#!/bin/bash
echo "" > FrogOrchestrator.log
python3 start_gunicorn.py "$@"
