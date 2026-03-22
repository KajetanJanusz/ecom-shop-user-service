#!/bin/bash
gunicorn -c gunicorn.dev.conf.py core:app