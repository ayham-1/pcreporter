#!/bin/bash

# Runs pcreporter in venv

pip3 install -r requirements.txt
pip3 install --editable .
pcreporter
