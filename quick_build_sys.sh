#!/bin/bash

source .venv/bin/activate
pip3 install -r requirements.txt
rm -fr dist/
python3 -m build --wheel 
deactivate

pipx uninstall pcreporter
pipx install --force --global dist/*.whl
