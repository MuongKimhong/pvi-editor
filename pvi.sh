#!/bin/bash

pvi_directory="$HOME/pvi-editor"

cd "$pvi_directory" || exit 1

entry_point_script="$pvi_directory/pvi/main.py"

# Use "$@" to pass all the arguments provided to the script
poetry run python "$entry_point_script" "$@"
