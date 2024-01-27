#!/bin/bash

# this script will be executed when user push code from footer
# -> :git push origin branch "somemessage"

# $1 is branch name
# $2 is commit message
# $3 is commit file path

if [ $# -eq 2 ]; then
    git add .
else
    git add $3
fi

git commit -m "$2"
git push origin $1
