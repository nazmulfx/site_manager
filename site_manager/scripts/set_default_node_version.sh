#!/bin/bash
VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Error: Version argument required"
    exit 1
fi

if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
else
    echo "Error: NVM not found at $HOME/.nvm/nvm.sh"
    exit 1
fi

nvm alias default "$VERSION" >/dev/null 2>&1
nvm use "$VERSION" >/dev/null 2>&1

NODE_BIN=$(nvm which "$VERSION" 2>/dev/null)
INSTALLED_VER=$("$NODE_BIN" -v 2>/dev/null)

echo "$INSTALLED_VER|$NODE_BIN"
