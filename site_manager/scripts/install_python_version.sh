#!/bin/bash
VERSION="$1"
SET_DEFAULT="$2"

if [ -z "$VERSION" ]; then
    echo "Error: Version argument required"
    exit 1
fi

clean_ver="${VERSION#Python }"
clean_ver="$(echo "$clean_ver" | xargs)"

echo "Installing requested Python version: $clean_ver..."

# Extract short minor version (e.g. 3.14 from 3.14.6)
short_ver=$(echo "$clean_ver" | grep -oE '3\.[0-9]+' | head -n 1)
[ -z "$short_ver" ] && short_ver="$clean_ver"

apt_pkg="python${short_ver}"
apt_bin="/usr/bin/${apt_pkg}"
INSTALLED_PATH=""

# 1. Check if matching system apt binary exists
if [ -x "$apt_bin" ]; then
    actual_ver=$("$apt_bin" --version 2>&1 | head -n 1)
    actual_num="${actual_ver#Python }"
    if [ "$clean_ver" = "$short_ver" ] || [ "$clean_ver" = "$actual_num" ]; then
        echo "Found system APT package binary: $actual_ver ($apt_bin)"
        INSTALLED_PATH="$apt_bin"
    fi
fi

# 2. Try APT + deadsnakes PPA if minor version requested and apt_bin not present
if [ -z "$INSTALLED_PATH" ] && [ "$clean_ver" = "$short_ver" ]; then
    echo "Attempting system installation via deadsnakes PPA & apt for $apt_pkg..."
    if sudo -n true 2>/dev/null; then
        sudo apt update
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        sudo apt install -y pkg-config "$apt_pkg" "${apt_pkg}-venv" "${apt_pkg}-dev"
        if [ -x "$apt_bin" ]; then
            INSTALLED_PATH="$apt_bin"
            echo "Installing pip/setuptools/wheel..."
            "$apt_bin" -m ensurepip --upgrade 2>/dev/null || true
            "$apt_bin" -m pip install --upgrade pip setuptools wheel 2>/dev/null || true
        fi
    else
        echo "Passwordless sudo not available for apt. Proceeding to uv installer..."
    fi
fi

# 3. Fallback or exact patch version install via uv
if [ -z "$INSTALLED_PATH" ]; then
    UV_BIN=$(which uv 2>/dev/null || echo "/usr/local/bin/uv")
    if [ -x "$UV_BIN" ]; then
        echo "Installing Python $clean_ver via uv..."
        "$UV_BIN" python install "$clean_ver"
        INSTALLED_PATH=$("$UV_BIN" python find "$clean_ver" 2>/dev/null)
    fi
fi

if [ -z "$INSTALLED_PATH" ] || [ ! -x "$INSTALLED_PATH" ]; then
    echo "Error: Failed to install Python version $clean_ver"
    exit 1
fi

REAL_VER=$("$INSTALLED_PATH" --version 2>&1 | head -n 1)
echo "Resolved Python version: $REAL_VER ($INSTALLED_PATH)"

echo "RESULT:$REAL_VER|$INSTALLED_PATH"
