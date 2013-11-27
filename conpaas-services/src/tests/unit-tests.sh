#!/bin/bash -x

export PYTHONPATH=..
coverage run --source=conpaas run_tests.py

