#!/bin/bash

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone your GitHub repository
echo -e "\e[1;31m[INFO] Cloning pvi-editor[0m"
git clone https://github.com/MuongKimhong/pvi-editor.git

cd pvi-editor

echo -e "\e[1;31m[INFO] Install dependencies[0m"
poetry install

echo -e "\e[1;31m[INFO] Creating pvi command[0m"
sudo ln -s "$(pwd)/pvi/main.py" /usr/local/bin/pvi

echo -e "\e[1;31m[INFO] Installation completed[0m"
echo -e "\e[1;36m- run: pvi file.py to open file.py and edit"
echo -e "\e[1;36m- run: pvi . to open current directory"
echo -e "\e[1;36m- run: pvi -d somedirectory to open somedirectory"
