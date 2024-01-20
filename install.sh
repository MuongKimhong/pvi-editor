#!/bin/bash

# install poetry
echo -e "\e[1;32m\n[INFO] Installing Poetry for Python3\n"
curl -sSL https://install.python-poetry.org | python3 -

# Clone pvi GitHub repository
echo -e "\e[1;32m\n[INFO] Cloning pvi-editor\n"
repository_url="https://github.com/MuongKimhong/pvi-editor.git"
git clone "$repository_url" "$HOME/pvi-editor"

# Download pvi.sh
curl -o /usr/local/bin/pvi "https://raw.githubusercontent.com/MuongKimhong/pvi-editor/master/pvi.sh"

chmod +x /usr/local/bin/pvi

cd "$HOME/pvi-editor"

poetry install

echo -e "\e[1;32m\n[INFO] Installation completed\n"
echo -e "\e[1;36m- run: pvi file.py to open file.py and edit"
echo -e "\e[1;36m- run: pvi . to open current directory"
echo -e "\e[1;36m- run: pvi -d somedirectory to open somedirectory"

echo -e "\e[1;36m\nVist https://github.com/MuongKimhong/pvi-editor for more info.\n"