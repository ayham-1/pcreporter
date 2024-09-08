#!/bin/bash

source .venv/bin/activate
pip3 install -r requirements.txt
rm -fr dist/
python3 -m build --wheel 
source .venv/bin/deactivate

pipx uninstall pcreporter
pipx install dist/*.whl
