#!/bin/bash
# build.sh

echo "Starting build process..."

# Use pip directly without python -m
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Build complete!"