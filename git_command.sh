#!/bin/bash


# $1 is branch name
# $2 is commit message
# $3 is commit file path

git add $3
git commit -m "$2"
git push origin $1
