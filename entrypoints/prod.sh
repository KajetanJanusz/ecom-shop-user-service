#!/bin/bash
gunicorn -c gunicorn.prod.conf.py core:app