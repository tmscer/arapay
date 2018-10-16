#!/usr/bin/env bash

PY="../venv/bin/python"

PY manage.py collectstatic
PY manage.py --check deploy

