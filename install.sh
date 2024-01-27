#!/bin/bash

RED='\033[0;31m'
CYAN='\033[0;36m'
GREEN='\033[0;32m]'
NC='\033[0m' # No Color

# install poetry
echo -e "${GREEN}[INFO] Installing Poetry for Python3\n${NC}"
curl -sSL https://install.python-poetry.org | python3 -

# Clone pvi GitHub repository
echo -e "${GREEN}[INFO] Cloning pvi-editor\n${NC}"
repository_url="https://github.com/MuongKimhong/pvi-editor.git"
git clone "$repository_url" "$HOME/pvi-editor"

# create autocomplete cache file in home dir
cache_file="$HOME/pvi_autocomplete_cache.json"

if [ ! -e "$cache_file" ]; then
    touch "$cache_file"
    # read and write permission
    sudo chmod 600 "$cache_file"
fi

# Download pvi.sh
sudo curl -o /usr/local/bin/pvi "https://raw.githubusercontent.com/MuongKimhong/pvi-editor/master/pvi.sh"

sudo chmod +x /usr/local/bin/pvi

cd "$HOME/pvi-editor"

poetry install

echo -e "${CYAN}[INFO] Installation completed\n"
echo -e "${CYAN}- run: pvi file.py to open file.py and edit"
echo -e "${CYAN}- run: pvi . to open current directory"
echo -e "${CYAN}- run: pvi -d somedirectory to open somedirectory"

echo -e "${CYAN}\nVist https://github.com/MuongKimhong/pvi-editor for more info.\n"