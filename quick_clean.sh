#!/bin/bash

pipx uninstall pcreporter
pip3 uninstall pcreporter

rm -fr dist/
rm -fr build/
rm -fr pcreporter.egg-info/
