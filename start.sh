#!/bin/bash

cd /opt/blog
. venv/bin/activate
python3 wsgi.py
