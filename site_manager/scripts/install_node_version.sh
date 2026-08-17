#!/bin/bash
VERSION="$1"
SET_DEFAULT="$2"

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

echo "Installing Node version: $VERSION..."
nvm install "$VERSION"

NODE_BIN=$(nvm which "$VERSION" 2>/dev/null)

if [ -z "$NODE_BIN" ] || [ ! -x "$NODE_BIN" ]; then
    echo "Error: Could not locate installed Node binary for version $VERSION"
    exit 1
fi

INSTALLED_VER=$("$NODE_BIN" -v 2>/dev/null)
echo "Installed version resolved: $INSTALLED_VER ($NODE_BIN)"

if [ "$SET_DEFAULT" = "1" ]; then
    echo "Setting default alias to $INSTALLED_VER..."
    nvm alias default "$INSTALLED_VER"
    nvm use "$INSTALLED_VER"
fi

echo "RESULT:$INSTALLED_VER|$NODE_BIN"

