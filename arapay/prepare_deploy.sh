#!/usr/bin/env bash

PY="../venv/bin/python"

eval "$PY manage.py migrate"
eval "$PY manage.py collectstatic"
eval "$PY manage.py check --deploy"

