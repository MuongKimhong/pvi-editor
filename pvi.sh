#!/bin/bash

RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

if [ "$#" -eq 0 ]; then
    echo -e "${RED}\n[PVI ERROR] No file or directory provided."
    echo -e "${CYAN}- <pvi file.txt> open file.txt and edit"
    echo -e "${CYAN}- <pvi directory> open directory"
    echo -e "${CYAN}- <pvi .> open current directory"   
    exit 0
fi

pvi_directory="$HOME/pvi-editor"

# pvi-editor exists
if [ -e "$pvi_directory" ]; then
    before_change=$(pwd)
    arguments=("$before_change"/"$@")

    # check if provided file or directory path exists
    if [ -e "${arguments[@]}" ]; then
        cd "$pvi_directory"
        entry_point="$pvi_directory/pvi/main.py"
        poetry run python "$entry_point" "${arguments[@]}"
    fi
else
    echo -e "${RED}\n[PVI ERROR] pvi-editor not found. Please install..${NC}"
    exit 0
fi