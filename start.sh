#!/usr/bin/env bash
gunicorn -c gunicorn.py manager:app